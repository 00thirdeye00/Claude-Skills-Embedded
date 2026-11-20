---
name: embedded-protocols
description: Size, configure, and troubleshoot I2C, SPI, UART/RS-485, CAN/CAN FD, and USB buses on any MCU.
argument-hint: "<bus, devices and speeds, or the symptom on the wire>"
disable-model-invocation: true
---

# /embedded-core:embedded-protocols

Explain, choose, size, and troubleshoot embedded buses independent of the MCU vendor.

If the bus is not named, ask which bus, the devices, the speed, the cable length, and what is seen on the wire.

## Workflow

1. **Identify the bus and the question** (selection, electrical sizing, timing, framing, or fault).
2. **Load the matching reference**:

| Bus | Load |
|---|---|
| I2C | `references/i2c.md` |
| SPI | `references/spi.md` |
| UART, RS-232, RS-485 | `references/uart.md` |
| CAN, CAN FD | `references/can.md` |
| USB | `references/usb.md` |

3. **Compute with numbers**: show the formula, the inputs, and the result.
4. **Recommend a probe** (oscilloscope or logic analyzer, with the trigger and decode setting) to confirm.
5. **Report** with the output template.

## Quick selection guide

| Need | Usually |
|---|---|
| Few slow sensors, two wires, many devices | I2C |
| High throughput to one or a few chips, short distance | SPI |
| Point-to-point text or binary link, debug console | UART |
| Multi-node, noisy environment, robust arbitration | CAN or CAN FD |
| Long multi-drop with simple framing | RS-485 over UART |
| Host connectivity, mass storage, audio, high bandwidth | USB |

## Output

```markdown
## Bus Analysis: [bus and context]

### Inputs
- [speed, devices, length, voltage, capacitance]

### Calculation
[formula and result]

### Recommendation
[settings, component values]

### How to verify
- [probe point, trigger, expected waveform or decode]
```

## Rules

- Give formulas and units, and say which values come from datasheets and must be confirmed.
- Distinguish the protocol specification from vendor peripheral behavior.
- When troubleshooting, ask for waveforms or captures before guessing.
