#!/usr/bin/env python3
"""
Add or extend the withdrawn-claims banner at the top of files that still carry a withdrawn claim

Key features:
- Scans a repository (default: this one) with the rules of check_withdrawn_claims.py
- Markdown, text, Scheme and YAML files get a banner naming each claim found and its correction
  (the register's "banner" text); an existing banner is extended, never duplicated
- JSON and other formats that cannot carry a banner are listed, not edited
- Dry run by default; --apply writes
"""
import argparse
import collections
import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_withdrawn_claims as C  # noqa: E402

MARK = "<!-- withdrawn-claims-banner -->"
REG = "docs/strategic/WITHDRAWN_CLAIMS_REGISTER.json"
PREFIX = {".md": "> ", ".txt": "# ", ".scm": ";; ", ".yml": "# ", ".yaml": "# "}


def style(path):
    p = PREFIX[path.suffix.lower()]
    marker = MARK if p == "> " else p + "withdrawn-claims-banner"
    return p, marker


def update(path, ids, claims, today, write):
    """Return the claim ids this file's banner lacks; add them when write is set."""
    by = {c["id"]: c for c in claims}
    p, marker = style(path)
    with open(path, encoding="utf-8", newline="") as f:  # keep CRLF files CRLF
        text = f.read()
    nl = "\r\n" if "\r\n" in text else "\n"
    lines = text.split(nl)
    bullet = lambda i: f"{p}- corrected (`{i}`): {by[i]['banner']}"  # noqa: E731
    if marker in lines:
        k = lines.index(marker)
        end = k + 1
        while end < len(lines) and lines[end].startswith(p):
            end += 1
        have = "\n".join(lines[k:end])
        new = [i for i in ids if f"(`{i}`)" not in have]
        if new and write:
            lines[end - 1:end - 1] = [bullet(i) for i in new]  # keep the footer last
    else:
        new = list(ids)
        if write:
            start = 0
            if p == "> " and lines and lines[0].strip() == "---":  # YAML front matter stays first
                try:
                    start = lines.index("---", 1) + 1
                except ValueError:
                    start = 0
            block = [marker, f"{p}⛔ **This file contains claims since withdrawn or corrected (flagged {today}).** "
                     "Do not reuse them; use the corrections:"]
            block += [bullet(i) for i in ids]
            block.append(f"{p}Register and sources: `{REG}` (cogpy/ad-res-j7).")
            lines[start:start] = block + [""]
    if new and write:
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(nl.join(lines))
    return new


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", help="repository to banner (default: this one)")
    ap.add_argument("--apply", action="store_true", help="write the banners (default: dry run)")
    a = ap.parse_args()
    if a.root:
        C.ROOT = Path(a.root).resolve()
    reg, claims, allow = C.load_register()
    today = datetime.date.today().isoformat()
    hits = collections.defaultdict(list)
    for path in C.candidate_files(reg, claims):
        if not C.path_checked(path, reg):
            continue
        for p, _no, c, _t in C.violations(path, C.read_lines(path), claims, allow):
            if c["id"] not in hits[p]:
                hits[p].append(c["id"])
    order = [c["id"] for c in claims]
    edited, skipped = 0, []
    for p, ids in sorted(hits.items()):
        ids = sorted(ids, key=order.index)
        if Path(p).suffix.lower() not in PREFIX:
            skipped.append((p, ids))
            continue
        new = update(C.ROOT / p, ids, claims, today, a.apply)
        if new:
            edited += 1
            print(f"{'bannered' if a.apply else 'would banner'} {p}: {', '.join(new)}")
    for p, ids in skipped:
        print(f"⚠️  cannot banner {p}: {', '.join(ids)}")
    print(f"📊 {len(hits)} files carry withdrawn claims; {edited} {'bannered' if a.apply else 'need a banner'}; "
          f"{len(skipped)} not bannerable")
    return 0


if __name__ == "__main__":
    sys.exit(main())
