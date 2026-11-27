#!/usr/bin/env python3
"""Summarize a GNU ld map file: memory region usage, largest sections, largest objects.

Usage: map_summary.py firmware.map [--top 15]

Create the map with: -Wl,-Map=firmware.map
Region usage counts each output section at its run address (VMA) and, for sections with a
load address (such as .data), also at the load address (LMA) in the load region.
"""
import argparse
import re
import sys

HEX = r"0x[0-9a-fA-F]+"
REGION = re.compile(rf"^(\S+)\s+({HEX})\s+({HEX})\s*(\S*)\s*$")
SECTION = re.compile(rf"^(\.\S+)\s+({HEX})\s+({HEX})(?:\s+load address\s+({HEX}))?\s*$")
SECTION_NAME_ONLY = re.compile(r"^(\.\S+)\s*$")
SECTION_CONT = re.compile(rf"^\s+({HEX})\s+({HEX})(?:\s+load address\s+({HEX}))?\s*$")
INPUT = re.compile(rf"^\s(\.\S+)\s+({HEX})\s+({HEX})\s+(\S.*)$")
INPUT_NAME_ONLY = re.compile(r"^\s(\.\S+)\s*$")
INPUT_CONT = re.compile(rf"^\s{{10,}}({HEX})\s+({HEX})\s+(\S.*)$")


def parse(path):
    regions, sections, objects = [], [], {}
    in_mem = in_map = False
    cur = None
    pending = None  # (kind, name)
    with open(path, errors="replace") as f:
        for line in f:
            line = line.rstrip("\n")
            if line.startswith("Memory Configuration"):
                in_mem, in_map = True, False
                continue
            if line.startswith("Linker script and memory map"):
                in_mem, in_map = False, True
                continue
            if in_mem:
                m = REGION.match(line)
                if m and m.group(1) not in ("Name", "*default*"):
                    regions.append({"name": m.group(1), "origin": int(m.group(2), 16), "length": int(m.group(3), 16), "used": 0, "load_used": 0})
                continue
            if not in_map:
                continue
            m = SECTION.match(line)
            if m:
                cur = {"name": m.group(1), "vma": int(m.group(2), 16), "size": int(m.group(3), 16),
                       "lma": int(m.group(4), 16) if m.group(4) else None}
                sections.append(cur)
                pending = None
                continue
            if SECTION_NAME_ONLY.match(line) and not line.startswith(" "):
                pending = ("section", line.strip())
                continue
            if pending and pending[0] == "section":
                m = SECTION_CONT.match(line)
                if m:
                    cur = {"name": pending[1], "vma": int(m.group(1), 16), "size": int(m.group(2), 16),
                           "lma": int(m.group(3), 16) if m.group(3) else None}
                    sections.append(cur)
                pending = None
                continue
            m = INPUT.match(line)
            if m and cur is not None:
                size, where = int(m.group(3), 16), m.group(4).strip()
                if size:
                    objects[where] = objects.get(where, 0) + size
                pending = None
                continue
            if INPUT_NAME_ONLY.match(line):
                pending = ("input", line.strip())
                continue
            if pending and pending[0] == "input":
                m = INPUT_CONT.match(line)
                if m and cur is not None:
                    size, where = int(m.group(2), 16), m.group(3).strip()
                    if size:
                        objects[where] = objects.get(where, 0) + size
                pending = None
    return regions, sections, objects


def region_of(regions, addr):
    for r in regions:
        if r["origin"] <= addr < r["origin"] + r["length"]:
            return r
    return None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("map")
    ap.add_argument("--top", type=int, default=15)
    a = ap.parse_args(argv)
    regions, sections, objects = parse(a.map)
    if not regions:
        print("No 'Memory Configuration' block found; link with a MEMORY command and -Wl,-Map.", file=sys.stderr)
        return 1
    for s in sections:
        if s["size"] == 0:
            continue
        r = region_of(regions, s["vma"])
        if r:
            r["used"] += s["size"]
        if s["lma"] is not None:
            rl = region_of(regions, s["lma"])
            if rl:
                rl["load_used"] += s["size"]
    print("| Region | Origin | Size | Used | Free | Used % |")
    print("|---|---|---|---|---|---|")
    for r in regions:
        used = r["used"] + r["load_used"]
        pct = 100.0 * used / r["length"] if r["length"] else 0
        print(f'| {r["name"]} | 0x{r["origin"]:08X} | {r["length"]} | {used} | {r["length"] - used} | {pct:.1f} |')
    print(f"\nLargest output sections (top {a.top}):")
    for s in sorted((s for s in sections if s["size"]), key=lambda s: -s["size"])[:a.top]:
        lma = f' (load 0x{s["lma"]:08X})' if s["lma"] is not None else ""
        print(f'  {s["size"]:8d}  {s["name"]}  @0x{s["vma"]:08X}{lma}')
    print(f"\nLargest contributors by input file (top {a.top}):")
    for where, size in sorted(objects.items(), key=lambda kv: -kv[1])[:a.top]:
        print(f"  {size:8d}  {where}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
