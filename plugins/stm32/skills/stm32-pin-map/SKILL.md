---
name: stm32-pin-map
description: Extract an MCU pin table from a KiCad netlist and prepare it for the design stage, so the whole schematic never has to be pasted into the chat.
argument-hint: "<netlist path, MCU reference (for example U1), or pasted nets>"
disable-model-invocation: true
---

# /stm32:stm32-pin-map

Turn a KiCad netlist into a compact MCU pin table, then check it against the datasheet before design work starts.

## Steps

1. **Get the netlist.** Ask for the KiCad netlist, exported with `kicad-cli sch export netlist --output board.net board.kicad_sch` (check `kicad-cli sch export --help` for your KiCad version). Without file access, ask the user to run the script (step 2) and paste the table, or paste only the nets that touch the MCU.
2. **Run the script** (needs Python): `python scripts/netlist_pins.py board.net --list` to find MCU candidates, then `python scripts/netlist_pins.py board.net --ref U1`. Use `--format csv` to save it. If it reports a parse error or finds no pins, say so; do not guess.
3. **Review the table**: GPIO pins sorted by port, special pins (boot, reset, oscillator, debug), power pins, `NC` pins, and named nets with a single node (something not in the netlist, such as a connector).
4. **Infer intended signals** from net names only as suggestions. Ask the user to confirm any that matter.
5. **Check alternate functions** only against an alternate-function table the user supplies from the datasheet. Never fill AF numbers from memory.
6. **Flag**: debug pins used for other purposes, boot pins with unclear state, power pins missing connections, shared or conflicting functions, pins whose peripheral choice limits DMA or timer options.
7. **Hand off**: give the table to `/stm32:stm32-design` for clocks, DMA, memory, and interrupts.

## Output

```markdown
## Pin Map: [MCU] ([n] pins, [g] GPIO, [nc] not connected)

| Pin | Function | Net | Connected to | Intended signal | AF check |
|---|---|---|---|---|---|

### Flags
- [..]

### Questions for the user
- [..]
```

## Rules

- Mark every inferred signal as inferred and every unchecked AF as unchecked.
- The script was tested on synthetic netlists written to match the KiCad s-expression format, not on a large range of real boards. If results look wrong, compare with the schematic.
- Do not paste the whole netlist into the conversation; work from the table.
