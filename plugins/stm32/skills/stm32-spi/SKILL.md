---
name: stm32-spi
description: Configure and debug STM32 SPI: clock mode (CPOL and CPHA), baud prescaler, frame size, chip-select handling, full-duplex DMA transfers, slave mode, and corruption at high clock rates. Use when talking to flash, displays, sensors, ADCs, or radios over SPI, when received data is shifted, all zeros, or all ones, or when throughput must increase. Trigger with "STM32 SPI", "SPI DMA", "SPI mode 0 or 3", "SPI all zeros", "chip select timing", "SPI 16-bit", "SPI slave", "SPI clock too fast".
argument-hint: "<device, mode, clock rate, transfer pattern, or the symptom>"
---

# /stm32:stm32-spi

Configure STM32 SPI and fix mode, timing, and DMA problems.

## Usage

```
/stm32:stm32-spi $ARGUMENTS
```

If details are missing, ask for the part, the SPI instance, the device datasheet timing, clock rate, frame size, and a logic analyzer capture if available.

## Workflow

1. **Take the device timing** from its datasheet: mode, maximum clock, bit order, chip-select setup and hold.
2. **Compute the prescaler** from the SPI kernel clock and choose a rate at or below the device limit and the signal-integrity limit.
3. **Configure** pins (speed matched to the clock), mode, frame size, and chip-select control.
4. **Choose the transfer mode** with the table below.
5. **Verify** with a logic analyzer: all four signals, then data.

Details, configuration checklists, example code, and failure modes are in `references/spi-config.md`.

## Choosing an approach

| Situation | Use |
|---|---|
| Short register access | Blocking transmit and receive with a timeout |
| Bulk data, display, flash | DMA for both directions; release chip-select after the transfer and busy flag complete |
| Many devices on one bus | One chip-select per device, mutex around the bus |
| Act as a slave | Hardware or software NSS, interrupt or DMA, careful FIFO handling |

## Output

```markdown
## SPI Plan: [context]

### Timing table (mode, rate, prescaler, kernel clock)
- [..]

### Transfer plan (mode, DMA, chip-select handling)
- [..]

### Verification steps
- [..]
```

## Rules

- Map mode numbers by CPOL and CPHA, not by name alone.
- Release chip-select only after the transfer, including the busy flag, is complete.
- Match DMA data width to the frame size.
- Confirm register-level and family-specific details against the reference manual, datasheet, and errata sheet for the exact part.

## Tips

1. **All 0xFF or 0x00** points to chip-select, mode, wiring, or a powered-down device.
2. **Reduce the clock** to separate timing issues from logic bugs.
3. **Set output speed** of the SPI pins high enough for the clock but no higher than needed.
