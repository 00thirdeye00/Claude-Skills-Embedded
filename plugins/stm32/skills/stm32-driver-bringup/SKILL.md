---
name: stm32-driver-bringup
description: Take a device from datasheet to a tested STM32 driver: bus layering, init sequence, error handling, and a bring-up and test plan.
argument-hint: "<device or peripheral, interface (I2C/SPI/UART/...), and the datasheet or register summary>"
disable-model-invocation: true
---

# /stm32:stm32-driver-bringup

Take a device from datasheet to a working, testable driver on an STM32 target.

If key facts are missing, ask for the device part number, the interface and speed, the STM32 part, the HAL or LL in use, and the datasheet or register map.

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

## Connectors

Optional (see `CONNECTORS.md`): when `~~source control`, `~~project tracker`, or `~~knowledge base` is connected, use it for diffs, tickets, and datasheets.
