---
name: stm32-driver-bringup
description: Bring up a new peripheral or external-device driver on STM32 from the datasheet to a tested driver: extract the register map and init sequence, separate the bus layer from the device layer, handle errors and timeouts, and plan verification with a logic analyzer or loopback. Use when writing a driver for a sensor, display, memory, radio, or an on-chip peripheral, or porting a driver to STM32 HAL. Trigger with "write a driver for", "bring up this sensor", "port this driver to STM32", "datasheet to driver", "first communication with the chip", "WHO_AM_I fails".
argument-hint: "<device or peripheral, interface (I2C/SPI/UART/...), and the datasheet or register summary>"
---

# /stm32:stm32-driver-bringup

Take a device from datasheet to a working, testable driver on an STM32 target.

## Usage

```
/stm32:stm32-driver-bringup $ARGUMENTS
```

If key facts are missing, ask for the device part number, the interface and speed, the STM32 part, the HAL or LL in use, and the datasheet or register map.

## How It Works

```
┌──────────────────────────────────────────────────────────────┐
│ 1 SPEC      electrical, bus, timing, registers, init sequence │
│ 2 STRUCTURE bus port layer / device driver / application API  │
│ 3 CODE      init, read, write, error handling                 │
│ 4 BRING-UP  power, bus scan, ID read, then features           │
│ 5 TEST      checklist and captures                            │
└──────────────────────────────────────────────────────────────┘
```

## Steps

1. **Extract the spec** from the datasheet: supply and logic levels, bus mode and maximum speed, address or chip-select behavior, power-up time, reset behavior, register map, the required initialization sequence, and timing limits. List anything ambiguous as a question rather than guessing.
2. **Design the layers** (see `references/driver-template.md`): a small bus port (read and write registers, delay) implemented with HAL calls, a device driver that depends only on the port, and an application-facing API. This keeps the driver portable and testable on a host.
3. **Write the driver**: configuration structure, init, register access helpers, a status and error enum, timeouts on every wait, and a clear sequence for reset, identification, and configuration.
4. **Plan the bring-up** in order of confidence: power and reset, bus signals on a scope or logic analyzer, device presence (ID register or ACK), a known register write and read-back, then features one at a time.
5. **Give a test plan**: expected waveforms, expected register values, a loopback or known-input test, and failure-path tests (device absent, bus error).

## Output

```markdown
## Driver Bring-up: [device] on [STM32 part]

### Spec summary
| Item | Value | Datasheet section |
|---|---|---|

### Layering
[bus port, device driver, API]

### Code
[files or snippets]

### Bring-up sequence
1. [step, expected observation]

### Test plan
- [test, expected result]

### Open questions
- [ambiguities to check against the datasheet]
```

## Rules

- Never invent register addresses, bit fields, or timings; take them from the supplied datasheet or ask.
- Include timeouts, return codes, and bus error recovery in the first version.
- Keep HAL calls inside the port layer.
- Use named constants for registers and fields.

## Tips

1. **Read the ID register first**; if that fails, the bug is wiring, power, address, or bus settings, not the driver logic.
2. **Capture the bus** with a logic analyzer and decode it before changing code.
3. **Mind the address convention** (7-bit versus 8-bit) and the device's power-up delay.
