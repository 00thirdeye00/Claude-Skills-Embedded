#!/usr/bin/env python3
"""List the largest per-function stack frames from GCC .su files.

Usage: stack_usage.py build/ [--top 20] [--warn 256]

Create the files with -fstack-usage. Each line is: file:line:col:function<TAB>bytes<TAB>qualifier.
This shows individual frames only. It does not compute worst-case call-chain depth;
use the callgraph output or measure the high-water mark on target for that.
"""
import argparse
import os
import re
import sys

LINE = re.compile(r"^(.+):(\d+):(\d+):(.+?)\t(\d+)\t([\w,]+)\s*$")


def scan(path):
    files = []
    if os.path.isfile(path):
        files = [path]
    else:
        for root, _, names in os.walk(path):
            files += [os.path.join(root, n) for n in names if n.endswith(".su")]
    rows = []
    for fn in files:
        with open(fn, errors="replace") as f:
            for line in f:
                m = LINE.match(line)
                if m:
                    rows.append((int(m.group(5)), m.group(6), m.group(4), f"{m.group(1)}:{m.group(2)}"))
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path")
    ap.add_argument("--top", type=int, default=20)
    ap.add_argument("--warn", type=int, default=256, help="flag frames at or above this many bytes")
    a = ap.parse_args(argv)
    rows = scan(a.path)
    if not rows:
        print("No .su entries found; compile with -fstack-usage.", file=sys.stderr)
        return 1
    rows.sort(key=lambda r: -r[0])
    print(f"{len(rows)} functions; {sum(1 for r in rows if r[1] != 'static')} with dynamic or bounded stack use\n")
    print("| Bytes | Kind | Function | Location | Flag |")
    print("|---|---|---|---|---|")
    for b, q, fn, loc in rows[:a.top]:
        flag = "LARGE" if b >= a.warn else ""
        if q != "static":
            flag = (flag + " " + q).strip()
        print(f"| {b} | {q} | {fn} | {loc} | {flag} |")
    return 0


if __name__ == "__main__":
    sys.exit(main())
