#!/usr/bin/env python3
"""
Guard against withdrawn claims re-entering the repository

Key features:
- Reads docs/strategic/WITHDRAWN_CLAIMS_REGISTER.json (patterns, corrections, sources,
  and the must_match / must_not_match examples each pattern has to satisfy)
- --diff BASE: fails if lines added since BASE repeat a withdrawn claim (CI mode)
- --report: counts the copies still in tracked files, per claim and per directory
- Lines citing a claim as withdrawn or corrected, and verbatim/archive paths, are allowed
- A claim hard-wrapped across the lines of one prose paragraph, or across the
  lines of a fenced diagram, is caught too (.md/.txt/.html). A fence is a diagram
  when it contains a box-drawing character (the form agents copy). Plain code
  stays one statement per line. A diagram is not joined with the prose outside it.
  In a box row (text between two vertical borders) the borders are dropped, and
  a row joins the one above only when it continues it (starts in lower case)
- A wrapped claim whose joined lines carry an allow marker (a correction split
  across a line break) is allowed, like the same correction on one line
- --root DIR / --register FILE: scan another repository against this (or another) register
"""
import argparse
import collections
import fnmatch
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGISTER = ROOT / "docs/strategic/WITHDRAWN_CLAIMS_REGISTER.json"
PROSE_SUFFIXES = {".md", ".txt", ".html"}  # hard-wrapped prose; data formats keep one field per line


def load_register():
    reg = json.loads(Path(REGISTER).read_text(encoding="utf-8"))
    claims = [dict(c, rx=re.compile(c["pattern"])) for c in reg["claims"]]
    return reg, claims, re.compile(reg["allow_line_markers"])


def example_errors(reg, claims):
    """Each pattern must catch the forms it was written for and miss the correction.

    The examples live in the register, next to the pattern. A pattern edit that
    misses a must_match form, or that matches a must_not_match correction, fails
    here. exemption_must_not_match lines repeat a claim and must not be exempted
    by allow_line_markers. exemption_must_match lines are real corrections and
    must stay exempted.
    """
    errors = []
    where = "docs/strategic/WITHDRAWN_CLAIMS_REGISTER.json"
    try:
        allow = re.compile(reg["allow_line_markers"])
    except re.error as exc:
        return [f"allow_line_markers in {where} does not compile: {exc}"]

    def require_lines(key, missing):
        lines = reg.get(key)
        if not lines:
            errors.append(missing)
            return []
        return lines

    still_fail = require_lines(
        "exemption_must_not_match",
        f"Add exemption_must_not_match to {where}: lines that repeat a withdrawn claim and "
        "must not be exempted. 'The R10.6M extraction was restated by counsel.' is one.",
    )
    still_allowed = require_lines(
        "exemption_must_match",
        f"Add exemption_must_match to {where}: corrections that repeat a withdrawn claim's "
        "words and must stay exempted. The R10.6M line ending 'not an extraction' is one.",
    )
    for text in still_fail:
        if allow.search(text):
            errors.append(
                f"allow_line_markers in {where} exempts a line that repeats a withdrawn claim. "
                f"A word like 'restated' is not a correction. Line: {text}"
            )
        elif not any(c["rx"].search(text) for c in claims):
            errors.append(
                f"exemption_must_not_match in {where} does not repeat a registered claim, so it "
                f"does not constrain the marker. Line: {text}"
            )
    for text in still_allowed:
        if not allow.search(text):
            errors.append(
                f"allow_line_markers in {where} no longer exempts a correction. Keep the specific "
                f"marker (for example 'not an extraction'), not a broad word. Line: {text}"
            )
        elif not any(c["rx"].search(text) for c in claims):
            errors.append(
                f"exemption_must_match in {where} does not repeat a registered claim. Line: {text}"
            )
    for c in claims:
        cid = f"{where} claim {c['id']}"
        must = c.get("must_match") or []
        must_not = c.get("must_not_match") or []
        if not must or not must_not:
            errors.append(
                f"{cid}: add must_match (a form the pull request must reject) and must_not_match "
                "(the correction, which the pattern must not catch)."
            )
            continue
        for text in must:
            if not c["rx"].search(text):
                errors.append(
                    f"{cid}: pattern does not match must_match. Widen the pattern, or fix the example. "
                    f"Form: {text}"
                )
        for text in must_not:
            if c["rx"].search(text):
                errors.append(
                    f"{cid}: pattern matches a correction in must_not_match. Narrow the pattern and "
                    f"use the claim's correction field. Wording: {text}"
                )
    return errors


def path_checked(path, reg):
    if any(a in path for a in reg["allow_paths"]):
        return False
    return any(fnmatch.fnmatch(Path(path).name, g) for g in reg["file_globs"])


def struck_lines(path):
    """Line numbers inside a ~~strikethrough~~ that spans lines (reset at blank lines)."""
    struck, inside = set(), False
    for no, text in read_lines(path):
        if not text.strip():
            inside = False
            continue
        if inside:
            struck.add(no)
        if text.count("~~") % 2:
            inside = not inside
    return struck


def violations(path, lines, claims, allow):
    """Yield (path, line_no, claim, text) for each withdrawn claim a line repeats."""
    struck = struck_lines(path)
    for no, text in lines:
        if allow.search(text) or no in struck:
            continue
        for c in claims:
            if c["rx"].search(text):
                yield path, no, c, text.strip()
    if Path(path).suffix.lower() in PROSE_SUFFIXES:
        yield from wrapped_violations(path, {no for no, _ in lines}, claims, allow, struck)


BLOCK_START = re.compile(r"\s*([-*+]|\d+[.)]|#+)\s")  # a list item or heading starts a new unit
BOX_DRAWING = set("│┌┐└┘├┤┬┴┼▼▲►◄─")  # a fenced diagram, as opposed to a code sample
BOX_ROW = re.compile(r"^\s*[│┃║]\s*(.*?)\s*[│┃║]\s*$")  # a row inside a drawn box: │ text │


def joinable(text):
    """A line that continues a paragraph or a diagram: not blank, not a table row, not a fence marker."""
    t = text.strip()
    return bool(t) and not t.startswith(("|", "```"))


def prose_runs(lines):
    """Paragraphs of (line_no, stripped) from `lines`.

    A fenced region is included only when it is a diagram (some line contains a
    box-drawing character). Those lines are not joined with the prose outside the
    fence. Plain code is left out: joining it glues unrelated statements.
    """
    paragraphs, run, fence, in_fence = [], [], [], False

    def flush(buf):
        paragraphs.append(buf)
        return []

    def flush_fence():
        if any(any(ch in BOX_DRAWING for ch in text) for _, text in fence):
            sub = []
            for no, text in fence:
                row = BOX_ROW.match(text)
                if row:
                    # Rows of a box are separate labels ("│ Salco: Cape Town │" / "│ SOLO: UK │")
                    # unless a row continues the sentence above it, which starts in lower case.
                    content = row.group(1)
                    if not (content[:1].islower() and sub):
                        paragraphs.append(sub)
                        sub = []
                    if content:
                        sub.append((no, content))
                    continue
                if not joinable(text) or BLOCK_START.match(text):
                    paragraphs.append(sub)
                    sub = []
                if joinable(text):
                    sub.append((no, text.strip()))
            paragraphs.append(sub)

    for no, text in lines:
        if text.strip().startswith("```"):
            if in_fence:
                flush_fence()
                fence = []
                in_fence = False
            else:
                run = flush(run)
                in_fence = True
            continue
        if in_fence:
            fence.append((no, text))
            continue
        if not joinable(text) or BLOCK_START.match(text):
            run = flush(run)
        if joinable(text):
            run.append((no, text.strip()))
    if in_fence:
        flush_fence()
    paragraphs.append(run)
    return paragraphs


def wrapped_violations(path, wanted, claims, allow, struck):
    """Claims hard-wrapped across lines of one paragraph, which no single line matches.

    Each paragraph from `prose_runs` that holds a line in `wanted` is joined with
    spaces and searched once per claim; only a match that crosses a join is reported,
    at its first line. It is skipped when a line it touches carries an allow marker,
    when the touched lines carry one once joined ("... to savings, not" / "an
    extraction."), when a line is struck through, or when a line repeats the claim
    on its own (the per-line check already reports that). It is reported only when
    it touches a line in `wanted`.
    """
    paragraphs = prose_runs(read_lines(path))
    for group in paragraphs:
        if len(group) < 2 or not wanted.intersection(no for no, _ in group):
            continue
        spans, pos = [], 0
        for no, text in group:
            spans.append((no, text, pos, pos + len(text)))
            pos += len(text) + 1
        joined = " ".join(text for _, text in group)
        for c in claims:
            for m in c["rx"].finditer(joined):
                touched = [(no, text) for no, text, a, b in spans if a < m.end() and m.start() < b]
                if len(touched) < 2 or not wanted.intersection(no for no, _ in touched):
                    continue
                if any(no in struck or allow.search(t) or c["rx"].search(t) for no, t in touched):
                    continue
                if allow.search(" ".join(t for _, t in touched)):
                    continue
                yield path, touched[0][0], c, " / ".join(t for _, t in touched)


def added_lines(base):
    """Map path -> [(line_no, text)] for lines added relative to base."""
    out = subprocess.run(["git", "-C", str(ROOT), "diff", "--unified=0", "--no-color", f"{base}...HEAD"],
                         capture_output=True, text=True, check=True).stdout
    added, path, no = collections.defaultdict(list), None, 0
    for line in out.splitlines():
        if line.startswith("+++ "):
            path = line[6:] if line.startswith("+++ b/") else None
        elif line.startswith("@@"):
            no = int(re.search(r"\+(\d+)", line).group(1))
        elif path and line.startswith("+"):
            added[path].append((no, line[1:]))
            no += 1
    return added


def tracked_files():
    out = subprocess.run(["git", "-C", str(ROOT), "ls-files", "-z"], capture_output=True, check=True).stdout
    return [p for p in out.decode().split("\0") if p]


def prefilter_pattern(pattern):
    """Loosen a claim pattern so it also matches when hard-wrapped (a superset, for ripgrep -U only).

    A space may also be a line break inside a drawn box, so box borders count as spacing.
    Spaces inside a character class such as [ ,] are left as they are.
    """
    pattern = re.sub(r"\(\?<[!=][^)]*\)", "", pattern)  # lookbehinds would no longer be fixed-width
    # the checks strip indentation before joining lines, so allow for it in bounded gaps
    pattern = re.sub(r"\{(\d+),(\d+)\}", lambda m: "{%s,%d}" % (m.group(1), int(m.group(2)) + 200), pattern)
    pattern = pattern.replace("(?i)", "").replace("[^.\\n|]", "[^.|]").replace("[^.\\n]", "[^.]").replace("[^\\n]", "[\\s\\S]")
    return re.sub(r"\\.|\[(?:\\.|[^\]])*\]| ", lambda m: "[\\s│┃║]*" if m.group() == " " else m.group(), pattern)


def candidate_files(reg, claims):
    """Map each tracked file that may carry a claim to the line numbers worth checking.

    ripgrep runs the loosened patterns multiline and reports every line a possible
    match touches, so the checks below only read those lines and their paragraphs.
    Without ripgrep (or if it fails) every tracked file is checked in full (None).
    """
    tracked = tracked_files()
    import shutil
    import tempfile
    if not shutil.which("rg"):
        print("⚠️  ripgrep not found: checking every tracked file in full (slow)")
        return dict.fromkeys(tracked)
    globs = sum([["-g", g] for g in reg["file_globs"]], [])

    def run(patterns):
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
            f.write("|".join("(?:%s)" % prefilter_pattern(c) for c in patterns))
        r = subprocess.run(["rg", "-n", "-i", "-P", "-U", "--null", "--no-heading", "--no-messages",
                            "-f", f.name, *globs, "."], cwd=str(ROOT), capture_output=True, text=True)
        Path(f.name).unlink()
        return r

    patterns = [c["pattern"] for c in claims]
    runs = [run(patterns)]
    if runs[0].returncode not in (0, 1):
        # the combined expression can exceed PCRE2's compile limit; one run per claim stays within it
        runs = [run([p]) for p in patterns]
    bad = [r for r in runs if r.returncode not in (0, 1)]
    if bad:
        print(f"⚠️  ripgrep prefilter failed, checking every tracked file in full (slow): {bad[0].stderr.strip()[:200]}")
        return dict.fromkeys(tracked)
    hits = collections.defaultdict(set)
    for r in runs:
        for line in r.stdout.splitlines():
            p, _, rest = line.partition("\0")
            no = rest.split(":", 1)[0]
            if no.isdigit():
                hits[p[2:] if p.startswith("./") else p].add(int(no))
    return {p: hits[p] for p in tracked if p in hits}


def read_lines(path):
    try:
        text = (ROOT / path).read_text(encoding="utf-8")
    except (UnicodeDecodeError, FileNotFoundError, IsADirectoryError):
        return []
    return list(enumerate(text.splitlines(), 1))


def run_diff(base, reg, claims, allow):
    found = []
    for path, lines in added_lines(base).items():
        if path_checked(path, reg):
            found.extend(violations(path, lines, claims, allow))
    for path, no, c, text in found:
        print(f"❌ {path}:{no} [{c['id']}] {text[:160]}")
        print(f"   withdrawn {c['withdrawn']}: {c['correction']} ({c['source']})")
    if found:
        print(f"\n{len(found)} added line(s) repeat a withdrawn claim. Use the correction instead, or mark the line "
              "as citing the withdrawn claim (e.g. 'withdrawn', 'corrected', '~~...~~').")
        return 1
    print("✅ No withdrawn claims in added lines")
    return 0


def run_report(reg, claims, allow, out_path):
    per_claim, per_dir, rows = collections.Counter(), collections.Counter(), []
    for path, nos in candidate_files(reg, claims).items():
        if not path_checked(path, reg):
            continue
        lines = read_lines(path)
        if nos is not None:
            lines = [(no, text) for no, text in lines if no in nos]
        for p, no, c, text in violations(path, lines, claims, allow):
            per_claim[c["id"]] += 1
            per_dir[path.split("/")[0]] += 1
            rows.append((c["id"], p, no))
    print("📊 Remaining uncorrected copies by claim:")
    for c in claims:
        print(f"  {per_claim[c['id']]:5d}  {c['id']}")
    print("📊 By top-level directory:")
    for d, n in per_dir.most_common(15):
        print(f"  {n:5d}  {d}")
    if out_path:
        with open(out_path, "w", encoding="utf-8") as f:
            f.write("claim\tpath\tline\n")
            for r in sorted(rows):
                f.write("\t".join(map(str, r)) + "\n")
        print(f"Wrote {len(rows)} rows to {out_path}")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--diff", metavar="BASE", help="check lines added since BASE (e.g. origin/main)")
    mode.add_argument("--report", action="store_true", help="count remaining copies in tracked files")
    ap.add_argument("--tsv", help="with --report, write every hit to this TSV file")
    ap.add_argument("--root", help="repository to scan (default: the repository holding this script)")
    ap.add_argument("--register", help="register JSON (default: <root>/docs/strategic/WITHDRAWN_CLAIMS_REGISTER.json, "
                    "falling back to this script's repository)")
    a = ap.parse_args()
    global ROOT, REGISTER
    if a.root:
        ROOT = Path(a.root).resolve()
    if a.register:
        REGISTER = Path(a.register).resolve()
    elif (ROOT / "docs/strategic/WITHDRAWN_CLAIMS_REGISTER.json").exists():
        REGISTER = ROOT / "docs/strategic/WITHDRAWN_CLAIMS_REGISTER.json"
    reg, claims, allow = load_register()
    errors = example_errors(reg, claims)
    if errors:
        for error in errors:
            print(f"❌ {error}")
        return 2
    if a.diff:
        return run_diff(a.diff, reg, claims, allow)
    return run_report(reg, claims, allow, a.tsv)


if __name__ == "__main__":
    sys.exit(main())
