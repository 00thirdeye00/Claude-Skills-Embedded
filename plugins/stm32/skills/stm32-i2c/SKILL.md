---
name: stm32-i2c
description: Configure and debug STM32 I2C: timing register or clock settings, 7-bit address shifting, master transfers with polling, interrupts, or DMA, slave mode, error flags, bus recovery from a stuck line, pull-up sizing, and differences between the older and newer I2C peripherals. Use when an I2C device does not ACK, the bus hangs or is stuck busy, transfers time out, or speed must be raised. Trigger with "STM32 I2C", "HAL_I2C error", "I2C busy flag stuck", "no ACK", "I2C timing register", "I2C 400 kHz", "I2C DMA", "I2C slave".
argument-hint: "<devices and addresses, speed, mode, or the symptom>"
---

# /stm32:stm32-i2c

Configure STM32 I2C and diagnose NACKs, hangs, and timing problems.

## Usage

```
/stm32:stm32-i2c $ARGUMENTS
```

If details are missing, ask for the part, the I2C instance, bus speed, device addresses, pull-up values, and the HAL error code or captured waveform.

## Workflow

1. **Gather**: devices, addresses (7-bit), speed, wiring length, and pull-ups.
2. **Identify the peripheral generation**: the older peripheral uses clock-control and rise-time registers; the newer one uses a timing register that must be generated for the kernel clock and speed.
3. **Configure** pins as open-drain alternate function with the right alternate-function number, then the peripheral.
4. **Choose the transfer mode** and add timeouts and a bus-recovery path.
5. **Verify** by scanning the bus, decoding with a logic analyzer, and measuring rise time.

Details, configuration checklists, example code, and failure modes are in `references/i2c-config.md`.

## Choosing an approach

| Situation | Use |
|---|---|
| Register read of a sensor | Memory-read helper (register address then data) with a timeout |
| Many small transactions in an RTOS | Interrupt or DMA with a completion semaphore; protect the bus with a mutex |
| Bus stuck low | Bus-recovery routine, then peripheral re-initialization |
| Act as a slave | Address-match interrupt, listen mode, handle stretching |

## Output

```markdown
## I2C Plan: [context]

### Bus parameters (speed, timing values, pull-up calculation)
- [..]

### Transfer plan (mode, timeouts, recovery)
- [..]

### Wiring and verification steps
- [..]
```

## Rules

- State the address convention used by the API (7-bit shifted left by one in HAL).
- Give timing values with the kernel clock and speed they were generated for.
- Always include timeouts and a recovery path.
- Confirm register-level and family-specific details against the reference manual, datasheet, and errata sheet for the exact part.

## Tips

1. **ACK but wrong data**: check register addresses, endianness, and repeated-start requirements.
2. **Busy flag stuck** after an aborted transfer: run bus recovery.
3. **Scope the rise time** before blaming firmware.
