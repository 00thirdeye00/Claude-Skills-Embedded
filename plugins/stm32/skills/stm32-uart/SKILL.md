---
name: stm32-uart
description: Configure and debug STM32 UART, USART, and LPUART: baud rate and kernel clock, polling versus interrupt versus DMA transfers, receiving variable-length frames with idle-line detection, error flags, RS-485 driver enable, printf retargeting, and wake-up from Stop. Use when setting up serial communication, losing bytes, seeing garbage characters, or stalled reception. Trigger with "STM32 UART", "USART DMA receive", "idle line detection", "garbage characters", "overrun error", "RS-485 on STM32", "printf over UART", "LPUART".
argument-hint: "<baud rate, frame format, transfer mode, or the symptom>"
---

# /stm32:stm32-uart

Configure STM32 serial ports and fix reception and framing problems.

## Usage

```
/stm32:stm32-uart $ARGUMENTS
```

If details are missing, ask for the part, the UART instance, baud rate and frame format, expected message lengths, and whether DMA or low power is required.

## Workflow

1. **Gather**: baud rate, frame format, message pattern (fixed or variable length), peak rate, and levels (TTL, RS-232, RS-485).
2. **Check the clock**: find the kernel clock of the instance and compute the achieved baud rate and error.
3. **Choose the transfer mode** with the table below.
4. **Configure** pins, clocks, the UART, DMA, and interrupts; plan error handling for overrun, framing, and noise.
5. **Verify** with a loopback test and a logic analyzer decode.

Details, configuration checklists, example code, and failure modes are in `references/uart-config.md`.

## Choosing an approach

| Situation | Use |
|---|---|
| Debug console, low rate | Polling or interrupt transmit |
| Continuous receive of unknown-length frames | DMA circular receive with idle-line detection, or receive-to-idle in DMA mode |
| Fixed-length frames | Interrupt or DMA receive of the exact length |
| RS-485 half duplex | Hardware driver-enable if available; otherwise GPIO released on transmission complete |
| Wake from Stop on a byte | Low-power UART with a wake-up source, kernel clock that runs in Stop |

## Output

```markdown
## UART Plan: [context]

### Clock and baud calculation (kernel clock, divider, actual baud, error)
- [..]

### Transfer plan (mode, buffers, callbacks)
- [..]

### Error handling plan
- [..]

### Verification steps
- [..]
```

## Rules

- State the baud error and keep the total error acceptable (about 2 percent combined, less is better).
- Handle error flags so reception cannot stall.
- Do not call blocking transmit from an ISR or a high-priority task.
- Confirm register-level and family-specific details against the reference manual, datasheet, and errata sheet for the exact part.

## Tips

1. **Wrong baud** usually means the wrong kernel clock source or a wrong clock constant.
2. **Garbage only at the start** often means a line glitch at power-up; resynchronize on a frame delimiter.
3. **printf over UART** blocks; use a queue and a low-priority task in real-time code.
