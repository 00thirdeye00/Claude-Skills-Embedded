#!/usr/bin/env python3
"""Extract an MCU pin table from a KiCad netlist (s-expression export).

Usage:
  netlist_pins.py board.net --list
  netlist_pins.py board.net [--ref U1] [--format md|csv] [--max-connected 4]

Create the netlist with: kicad-cli sch export netlist --output board.net board.kicad_sch
(check `kicad-cli sch export --help` for your KiCad version).
Without --ref the script picks the only component whose value or library part contains STM32.
"""
import argparse
import csv
import io
import re
import sys

TOKEN = re.compile(r'\(|\)|"(?:\\.|[^"\\])*"|[^\s()"]+')


def parse(text):
    stack, cur = [], []
    for tok in TOKEN.findall(text):
        if tok == "(":
            stack.append(cur)
            cur = []
        elif tok == ")":
            if not stack:
                raise ValueError("unbalanced parentheses in netlist")
            done, cur = cur, stack.pop()
            cur.append(done)
        elif tok.startswith('"'):
            cur.append(bytes(tok[1:-1], "utf-8").decode("unicode_escape") if "\\" in tok else tok[1:-1])
        else:
            cur.append(tok)
    if stack:
        raise ValueError("unbalanced parentheses in netlist")
    return cur


def child(lst, key):
    for c in lst:
        if isinstance(c, list) and c and c[0] == key:
            return c
    return None


def children(lst, key):
    return [c for c in lst if isinstance(c, list) and c and c[0] == key]


def val(lst, key, default=""):
    c = child(lst, key)
    return c[1] if c and len(c) > 1 and isinstance(c[1], str) else default


def load(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        tree = parse(f.read())
    export = next((t for t in tree if isinstance(t, list) and t and t[0] == "export"), None)
    if export is None:
        raise ValueError("no (export ...) block: is this a KiCad s-expression netlist?")
    comps = {}
    for c in children(child(export, "components") or [], "comp"):
        ls = child(c, "libsource") or []
        comps[val(c, "ref")] = {"value": val(c, "value"), "footprint": val(c, "footprint"),
                                "lib": val(ls, "lib"), "part": val(ls, "part")}
    parts = {}
    for lp in children(child(export, "libparts") or [], "libpart"):
        pins = {}
        for p in children(child(lp, "pins") or [], "pin"):
            pins[val(p, "num")] = val(p, "name")
        parts[(val(lp, "lib"), val(lp, "part"))] = pins
    nets = []
    for n in children(child(export, "nets") or [], "net"):
        nodes = [{"ref": val(nd, "ref"), "pin": val(nd, "pin"), "func": val(nd, "pinfunction"),
                  "type": val(nd, "pintype")} for nd in children(n, "node")]
        nets.append({"name": val(n, "name"), "nodes": nodes})
    return comps, parts, nets


def find_mcu(comps):
    c = [r for r, d in comps.items() if re.search("stm32", d["value"] + d["part"], re.I)]
    return c


GPIO = re.compile(r"^P([A-K])(\d{1,2})")
POWER = re.compile(r"^(VDD|VSS|VBAT|VREF|VCAP|VDDA|VSSA|VDDUSB|VLCD|VDDIO|VFBSMPS|VLXSMPS|VDDSMPS|VSSSMPS|PDR_ON)", re.I)
SPECIAL = re.compile(r"(BOOT|NRST|RESET|OSC|SWD|SWCLK|SWO|JT|PH\d)", re.I)


def classify(func, ptype):
    if POWER.match(func) or ptype in ("power_in", "power_out"):
        return "power"
    if GPIO.match(func):
        return "gpio"
    if SPECIAL.search(func):
        return "special"
    return "other"


def build(path, ref=None, max_connected=4):
    comps, parts, nets = load(path)
    if ref is None:
        cands = find_mcu(comps)
        if len(cands) != 1:
            raise SystemExit("Specify --ref; MCU candidates: " + (", ".join(cands) or "none found"))
        ref = cands[0]
    if ref not in comps:
        raise SystemExit(f"Reference {ref} not found in the netlist")
    libpins = parts.get((comps[ref]["lib"], comps[ref]["part"]), {})
    rows = []
    for net in nets:
        for nd in net["nodes"]:
            if nd["ref"] != ref:
                continue
            func = nd["func"] or libpins.get(nd["pin"], "")
            others = [f'{o["ref"]}.{o["pin"]}' + (f'({o["func"]})' if o["func"] else "") for o in net["nodes"] if o is not nd and o["ref"] != ref]
            nc = net["name"].lower().startswith("unconnected-")
            shown = others[:max_connected]
            if len(others) > max_connected:
                shown.append(f"+{len(others) - max_connected} more")
            if not others and not nc:
                shown = ["(single node: nothing else on this net in the netlist)"]
            rows.append({"pin": nd["pin"], "func": func, "net": "NC" if nc else net["name"],
                         "connected": ", ".join(shown) if not nc else "", "class": classify(func, nd["type"])})

    def key(r):
        m = GPIO.match(r["func"])
        if r["class"] == "gpio" and m:
            return (0, m.group(1), int(m.group(2)))
        order = {"special": 1, "other": 2, "power": 3}[r["class"]]
        try:
            return (order, "", int(r["pin"]))
        except ValueError:
            return (order, r["pin"], 0)
    rows.sort(key=key)
    return ref, comps[ref], rows


def render(rows, fmt):
    if fmt == "csv":
        buf = io.StringIO()
        w = csv.writer(buf)
        w.writerow(["pin", "function", "net", "connected_to", "class"])
        for r in rows:
            w.writerow([r["pin"], r["func"], r["net"], r["connected"], r["class"]])
        return buf.getvalue()
    lines = ["| Pin | Function | Net | Connected to | Class |", "|---|---|---|---|---|"]
    for r in rows:
        lines.append(f'| {r["pin"]} | {r["func"]} | {r["net"]} | {r["connected"]} | {r["class"]} |')
    return "\n".join(lines) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("netlist")
    ap.add_argument("--ref")
    ap.add_argument("--list", action="store_true", help="list MCU candidates and exit")
    ap.add_argument("--format", choices=["md", "csv"], default="md")
    ap.add_argument("--max-connected", type=int, default=4)
    a = ap.parse_args(argv)
    if a.list:
        comps, _, _ = load(a.netlist)
        for r in find_mcu(comps):
            print(f'{r}\t{comps[r]["value"]}\t{comps[r]["footprint"]}')
        return 0
    ref, comp, rows = build(a.netlist, a.ref, a.max_connected)
    gp = sum(1 for r in rows if r["class"] == "gpio")
    nc = sum(1 for r in rows if r["net"] == "NC")
    print(f'# {ref}: {comp["value"] or comp["part"]}  ({len(rows)} pins, {gp} GPIO, {nc} not connected)\n')
    print(render(rows, a.format))
    return 0


if __name__ == "__main__":
    sys.exit(main())
