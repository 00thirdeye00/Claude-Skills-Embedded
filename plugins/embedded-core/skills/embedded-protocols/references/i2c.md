# I2C

## Basics
- Two open-drain lines (SDA, SCL) with pull-up resistors; any device can pull a line low, and the pull-ups return it high.
- Speeds: standard 100 kHz, fast 400 kHz, fast-plus 1 MHz, high-speed 3.4 MHz.
- Transaction: START, 7-bit address plus R/W bit, ACK from the addressed device, data bytes each followed by ACK or NACK, STOP. A repeated START changes direction without releasing the bus.
- Addresses are quoted as 7-bit (0x00 to 0x7F) or as 8-bit with the R/W bit included. Datasheets mix the two conventions; confirm which one an API expects. Addresses 0x00 to 0x07 and 0x78 to 0x7F are reserved.
- Clock stretching: a slave may hold SCL low to delay the master. Masters need to support it and time out.

## Pull-up sizing

```
Rp(max) = tr / (0.8473 * Cb)         tr = allowed rise time, Cb = bus capacitance
Rp(min) = (VDD - VOL) / IOL          VOL = 0.4 V, IOL = 3 mA for standard and fast mode
```

Rise-time limits from the specification: 1000 ns (standard), 300 ns (fast), 120 ns (fast-plus). Bus capacitance is limited to 400 pF. Example: 3.3 V, 400 kHz, Cb = 100 pF gives Rp(max) = 300 ns / (0.8473 * 100 pF) = about 3.5 kohm and Rp(min) = 2.9 V / 3 mA = about 970 ohm. Pick a value between, such as 2.2 kohm.

## Failure modes

| Symptom | Likely cause | Check |
|---|---|---|
| NACK on address | Wrong address (7-bit versus 8-bit), device unpowered or in reset, wrong bus | Scan the bus; decode the address byte |
| Bus stuck low | A slave holds SDA after an interrupted transfer | Toggle SCL up to 9 times, then STOP, then reinitialize the peripheral |
| Slow, rounded edges | Pull-ups too large or too much capacitance | Scope SCL and SDA rise time |
| Works at 100 kHz, fails at 400 kHz | Pull-ups, wiring length, or timing settings | Lower speed, recheck rise time |
| Random corruption | Noise, shared long wires, missing ground, level mismatch | Shorten wires, add series resistors, use a level shifter |
| Two devices answer | Address conflict | Change address pins or use a multiplexer |

Use a level shifter designed for open-drain buses when voltages differ.
