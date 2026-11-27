#!/usr/bin/env python3
"""Check an ARCHITECTURE.md (see the stm32-architecture templates) for consistency and drift.

Usage:
  check_architecture.py --arch docs/architecture/ARCHITECTURE.md [--root .] [--src src Core]

Document checks (always): modules referenced exist, dependencies point downward by layer,
no dependency cycles, each module has a contract (file or section), resource owners exist,
no resource appears twice in the same resource table.
Code checks (with --root and --src): interrupt priorities set in code match the table, and
#include relations between module directories match the declared dependencies.
Exit code 1 if any ERROR is found.
"""
import argparse
import os
import re
import sys

RANK = [("bsp", 0), ("board", 0), ("driver", 1), ("service", 2), ("app", 3)]


def rank(layer):
    l = layer.lower()
    for k, v in RANK:
        if l.startswith(k):
            return v
    return None


def clean(cell):
    return cell.strip().strip("`").strip()


def tables(md):
    out, heading, i = [], "", 0
    lines = md.splitlines()
    while i < len(lines):
        ln = lines[i]
        if ln.startswith("#"):
            heading = ln.lstrip("#").strip()
        if ln.lstrip().startswith("|") and i + 1 < len(lines) and re.match(r"^\s*\|[\s:|-]+\|\s*$", lines[i + 1]):
            hdr = [clean(c) for c in ln.strip().strip("|").split("|")]
            rows, i = [], i + 2
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                rows.append([clean(c) for c in lines[i].strip().strip("|").split("|")])
                i += 1
            out.append((heading, hdr, rows))
            continue
        i += 1
    return out


def split_list(cell):
    return [c.strip().strip("`") for c in re.split(r"[,;]", cell) if c.strip().strip("`").lower() not in ("", "-", "none", "n/a")]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--arch", required=True)
    ap.add_argument("--root", default=None)
    ap.add_argument("--src", nargs="*", default=[])
    a = ap.parse_args(argv)
    findings = []

    def err(m): findings.append(("ERROR", m))
    def warn(m): findings.append(("WARN", m))

    md = open(a.arch, encoding="utf-8").read()
    base = os.path.dirname(os.path.abspath(a.arch))
    tbls = tables(md)
    mods = {}
    for h, hdr, rows in tbls:
        low = [x.lower() for x in hdr]
        if "module" in low and "layer" in low and "depends on" in low:
            ix = {k: low.index(k) for k in ("module", "layer", "depends on")}
            ix["header"] = low.index("public header") if "public header" in low else None
            ix["used"] = low.index("used by") if "used by" in low else None
            for r in rows:
                name = r[ix["module"]]
                mods[name] = {"layer": r[ix["layer"]], "deps": split_list(r[ix["depends on"]]),
                              "header": r[ix["header"]] if ix["header"] is not None and ix["header"] < len(r) else "",
                              "used": split_list(r[ix["used"]]) if ix["used"] is not None and ix["used"] < len(r) else None}
            break
    if not mods:
        err("No modules table found (columns Module, Layer, Depends on).")
        for s, m in findings: print(f"{s}: {m}")
        return 1

    for n, m in mods.items():
        rk = rank(m["layer"])
        if rk is None:
            warn(f"{n}: unknown layer '{m['layer']}'")
        for d in m["deps"]:
            if d not in mods:
                err(f"{n}: depends on unknown module '{d}'")
                continue
            rd, rn = rank(mods[d]["layer"]), rk
            if rd is not None and rn is not None:
                if rd > rn:
                    err(f"{n} ({m['layer']}) depends upward on {d} ({mods[d]['layer']})")
                elif rd == rn:
                    warn(f"{n} depends on {d} in the same layer")
        if m["used"] is not None:
            actual = sorted(x for x, mm in mods.items() if n in mm["deps"])
            if sorted(m["used"]) != actual:
                warn(f"{n}: 'Used by' {sorted(m['used'])} differs from dependents {actual}")
        has_file = os.path.isfile(os.path.join(base, "modules", n + ".md"))
        has_sec = re.search(rf"^##\s+Module:\s*{re.escape(n)}\s*$", md, re.M) is not None
        if not (has_file or has_sec):
            err(f"{n}: no contract (modules/{n}.md or a '## Module: {n}' section)")

    state = {}
    def dfs(n, path):
        state[n] = 1
        for d in mods[n]["deps"]:
            if d not in mods: continue
            if state.get(d) == 1:
                err("dependency cycle: " + " -> ".join(path + [n, d])); continue
            if d not in state: dfs(d, path + [n])
        state[n] = 2
    for n in mods:
        if n not in state: dfs(n, [])

    prios = {}
    for h, hdr, rows in tbls:
        low = [x.lower() for x in hdr]
        if not rows or h.lower().startswith("modules") or "depends on" in low:
            continue
        owner_ix = next((i for i, x in enumerate(low) if "owner" in x), None)
        seen = {}
        for r in rows:
            key = r[0] if r else ""
            if key and key.lower() not in ("-", ""):
                if key in seen and "task" not in h.lower():
                    err(f"'{h}': resource '{key}' listed twice")
                seen[key] = True
            if owner_ix is not None and owner_ix < len(r):
                for o in split_list(r[owner_ix]):
                    if o not in mods and o.lower() not in ("shared", "bsp", "board support", "hardware"):
                        err(f"'{h}': owner '{o}' of '{key}' is not a known module")
        if "irq" in low and "priority" in low:
            for r in rows:
                try: prios[r[low.index("irq")]] = int(r[low.index("priority")])
                except (ValueError, IndexError): pass

    if a.root and a.src:
        files = []
        for s in a.src:
            for root, _, names in os.walk(os.path.join(a.root, s)):
                files += [os.path.join(root, n) for n in names if n.endswith((".c", ".h"))]
        text = {f: open(f, errors="replace").read() for f in files}
        found = {}
        pat = re.compile(r"(?:HAL_NVIC_SetPriority|NVIC_SetPriority)\s*\(\s*(\w+)\s*,\s*(\d+)")
        for f, t in text.items():
            for irq, p in pat.findall(t):
                found.setdefault(irq, set()).add(int(p))
        for irq, p in prios.items():
            if irq in found and p not in found[irq]:
                err(f"IRQ {irq}: table priority {p} but code sets {sorted(found[irq])}")
            elif irq not in found:
                warn(f"IRQ {irq}: in table but no SetPriority call found in {a.src}")
        for irq in sorted(set(found) - set(prios)):
            warn(f"IRQ {irq}: priority set in code but missing from the table")
        hdr_owner = {}
        for n, m in mods.items():
            if m["header"]:
                hdr_owner[os.path.basename(m["header"])] = n
        inc = re.compile(r'#\s*include\s+"([^"]+)"')
        for n, m in mods.items():
            if not m["header"]:
                continue
            mdir = os.path.dirname(os.path.join(a.root, m["header"]))
            for f, t in text.items():
                if os.path.dirname(f) != mdir:
                    continue
                for inc_name in inc.findall(t):
                    owner = hdr_owner.get(os.path.basename(inc_name))
                    if owner and owner != n and owner not in m["deps"]:
                        err(f"{n}: {os.path.relpath(f, a.root)} includes {inc_name} ({owner}) but '{owner}' is not a declared dependency")

    for s, m in findings:
        print(f"{s}: {m}")
    errs = sum(1 for s, _ in findings if s == "ERROR")
    print(f"\n{len(mods)} modules checked; {errs} errors, {len(findings) - errs} warnings")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
