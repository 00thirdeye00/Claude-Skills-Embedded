# STM32 UART configuration

HAL names are shown for orientation; confirm against your HAL version. Register details and baud-rate formulas depend on the family.

## Contents
- Baud rate and clock
- Transfer modes
- Receiving variable-length frames
- Error handling
- RS-485
- Low-power UART
- printf retargeting
- Failure modes
- Quick selection guide
- Tips

## Baud rate and clock

The baud rate is derived by dividing the peripheral's kernel clock. For a 16x oversampling USART the divider is roughly `kernel_clock / baud`; with 8x oversampling the divider differs and the maximum baud rate doubles but noise margin drops. The low-power UART uses a different formula (a 256-times scaled divider) and has a minimum ratio between kernel clock and baud rate; read the manual for the part.

Compute the actual baud rate from the integer divider and the error:

```
actual = kernel_clock / divider
error% = (actual - target) / target * 100
```

On families with kernel clock muxes, a UART may run from the bus clock, the system clock, an internal oscillator, or the low-speed clock; the baud error and the behavior in Stop mode depend on this choice.

## Transfer modes

| Mode | HAL examples | Notes |
|---|---|---|
| Polling | `HAL_UART_Transmit`, `HAL_UART_Receive` | Simple; blocks; avoid in real-time paths |
| Interrupt | `HAL_UART_Transmit_IT`, `HAL_UART_Receive_IT` | Per-byte or per-buffer interrupts; re-arm receive in the callback |
| DMA | `HAL_UART_Transmit_DMA`, `HAL_UART_Receive_DMA` | Low CPU load; needs DMA channel mapping and callbacks |
| Receive to idle | `HAL_UARTEx_ReceiveToIdle_DMA` and `_IT` | Completes when the line goes idle; the event callback receives the byte count |

Handles used with interrupt or DMA modes must outlive the call. A new transfer must not start before the previous one completed (check the handle state).

## Receiving variable-length frames

1. Start a DMA receive into a buffer (circular for continuous streams).
2. Use idle-line detection (or the receive-to-idle API) to learn where a frame ends.
3. In the event callback, compute the number of new bytes from the position, hand them to a task through a queue or notification, and keep the buffer running.
4. Optionally disable the DMA half-transfer interrupt if you only act on idle and full events.
5. Use a frame protocol (delimiters, length, CRC) so framing errors resynchronize.

## Error handling

Flags include overrun, framing, noise, and parity errors. If an error flag is not cleared, reception can stall (on some families an overrun blocks further receive). In the error callback: record the error, clear flags (HAL clears many), abort the transfer, and restart reception. Count errors in a variable for diagnostics.

## RS-485

Use the hardware driver-enable function where the USART provides it (assertion and de-assertion times set in sample-clock units), or control a GPIO manually. With a GPIO, release the driver after the transmission-complete flag, not the data-register-empty flag, so the last byte leaves the line.

## Low-power UART

The low-power UART can receive in Stop mode when clocked by an oscillator that stays on in that mode, and can wake the device on a start bit, address match, or received byte. Verify the kernel clock source is active in the target mode, and handle the wake-up and clock restoration.

## printf retargeting

Retargeting `_write` to a blocking UART transmit stalls the caller. In real-time code, copy into a queue or ring buffer and let a low-priority task or DMA transmit. Never print from interrupt handlers.

## Failure modes

| Symptom | Likely cause | Check |
|---|---|---|
| Garbage characters | Wrong baud, wrong kernel clock source, wrong clock constant, parity or stop-bit mismatch | Scope a bit time; recompute with the real clock |
| Reception stops | Overrun or other error flag not cleared; receive not re-armed | Check error callback, re-arm in callbacks |
| Lost bytes | Interrupt latency, buffer too small, high rate | Use DMA, raise priority, enlarge buffers |
| Duplicate or truncated frames | Misread DMA position, half-transfer callbacks confusing logic | Track the previous position; process only new bytes |
| RS-485 last byte cut off | Driver released too early | Use transmission-complete |
| Works at 9600, fails at 115200 | Baud error at the faster rate, clock error | Compute the error at each rate |

## Quick selection guide

| Situation | Use |
|---|---|
| Debug console, low rate | Polling or interrupt transmit |
| Continuous receive of unknown-length frames | DMA circular receive with idle-line detection, or receive-to-idle in DMA mode |
| Fixed-length frames | Interrupt or DMA receive of the exact length |
| RS-485 half duplex | Hardware driver-enable if available; otherwise GPIO released on transmission complete |
| Wake from Stop on a byte | Low-power UART with a wake-up source, kernel clock that runs in Stop |

## Tips

1. **Wrong baud** usually means the wrong kernel clock source or a wrong clock constant.
2. **Garbage only at the start** often means a line glitch at power-up; resynchronize on a frame delimiter.
3. **printf over UART** blocks; use a queue and a low-priority task in real-time code.
