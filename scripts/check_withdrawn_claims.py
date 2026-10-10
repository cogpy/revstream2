#!/usr/bin/env python3
"""
Guard against withdrawn claims re-entering the repository

Key features:
- Reads docs/strategic/WITHDRAWN_CLAIMS_REGISTER.json (patterns, corrections, sources)
- --diff BASE: fails if lines added since BASE repeat a withdrawn claim (CI mode)
- --report: counts the copies still in tracked files, per claim and per directory
- Lines citing a claim as withdrawn or corrected, and verbatim/archive paths, are allowed
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


def load_register():
    reg = json.loads(Path(REGISTER).read_text(encoding="utf-8"))
    claims = [dict(c, rx=re.compile(c["pattern"])) for c in reg["claims"]]
    return reg, claims, re.compile(reg["allow_line_markers"])


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


def candidate_files(reg, claims):
    """Tracked files that may carry a claim: ripgrep prefilter when available, else every tracked file."""
    tracked = tracked_files()
    import shutil
    import tempfile
    if not shutil.which("rg"):
        return tracked
    combined = "|".join("(?:%s)" % c["pattern"].replace("(?i)", "") for c in claims)
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
        f.write(combined)
    globs = sum([["-g", g] for g in reg["file_globs"]], [])
    r = subprocess.run(["rg", "-l", "-i", "-P", "--no-messages", "-f", f.name, *globs, "."],
                       cwd=str(ROOT), capture_output=True, text=True)
    Path(f.name).unlink()
    if r.returncode not in (0, 1):
        return tracked
    hits = {p[2:] if p.startswith("./") else p for p in r.stdout.splitlines() if p}
    return [p for p in tracked if p in hits]


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
    for path in candidate_files(reg, claims):
        if not path_checked(path, reg):
            continue
        for p, no, c, text in violations(path, read_lines(path), claims, allow):
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
    if a.diff:
        return run_diff(a.diff, reg, claims, allow)
    return run_report(reg, claims, allow, a.tsv)


if __name__ == "__main__":
    sys.exit(main())
