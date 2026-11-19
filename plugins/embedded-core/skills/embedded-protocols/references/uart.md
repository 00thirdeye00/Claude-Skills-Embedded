# UART, RS-232, RS-485

## Basics
- Asynchronous framing: idle high, a start bit (low), 5 to 9 data bits (usually 8, least significant first), optional parity, 1 or 2 stop bits. "8N1" means 8 data bits, no parity, 1 stop bit.
- Both ends must agree on baud rate. The receiver samples mid-bit, so accumulated timing error over a frame must stay well under half a bit.
- Baud error: `error% = (actual - target) / target * 100`. The transmitter and receiver errors add. As a practical rule, keep the combined error under about 2 percent. Peripherals derive the baud rate by dividing a kernel clock, so some clock and baud combinations give large errors; adjust the clock or oversampling.
- Logic-level UART is 0 to Vdd. RS-232 uses inverted, higher voltages (about plus or minus 3 to 15 V) and needs a level converter. RS-485 is differential and multi-drop.
- Hardware flow control uses RTS/CTS lines to pause the sender when the receiver buffer is nearly full.

## RS-485
- Half duplex needs a driver-enable (DE) signal: assert before the first start bit, release only after the last stop bit has fully left the shifter (not merely when the data register empties).
- Terminate both ends of the bus with the cable characteristic impedance (commonly 120 ohm) and bias the idle state so receivers see a defined level.
- Define a framing and turnaround protocol (addresses, timeouts, inter-frame gap) at the application layer.

## Receiving variable-length data
- Use an idle-line interrupt or receive timeout to detect the end of a frame.
- Use DMA into a circular buffer with half-complete and complete events, and read the DMA counter to find the write position.
- Handle overrun, framing, noise, and parity errors by clearing the flags and counting them.

## Failure modes

| Symptom | Likely cause | Check |
|---|---|---|
| Garbage characters | Baud mismatch, wrong clock source, wrong parity or stop bits | Measure one bit width on a scope; compare with the expected baud |
| Reception stops after a burst | Overrun flag never cleared, buffer too small | Check error flags, deepen the buffer, use DMA |
| Lost bytes at high rate | Interrupt latency, ISR too slow | Move to DMA, raise the priority |
| RS-485 corrupts the last byte | DE released too early | Release DE on transmission complete, not on empty |
| Works with one adapter only | Voltage levels or inverted signaling | Check RS-232 versus TTL levels |
