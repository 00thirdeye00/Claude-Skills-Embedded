# SPI

## Basics
- Four wires: SCLK, MOSI (controller out), MISO (controller in), and a chip-select per device (active low in most parts).
- Full duplex: every clock cycle shifts one bit out and one bit in. A read is a write of dummy bytes.
- Clock modes:

| Mode | CPOL | CPHA | Idle clock | Data sampled on |
|---|---|---|---|---|
| 0 | 0 | 0 | Low | Rising edge |
| 1 | 0 | 1 | Low | Falling edge |
| 2 | 1 | 0 | High | Falling edge |
| 3 | 1 | 1 | High | Rising edge |

- Bit order (MSB or LSB first), word size, and the maximum clock come from the slave datasheet. Vendor names for modes differ; map by CPOL and CPHA.
- Chip-select setup and hold times matter: many devices need CS low before the first clock edge and held until the last.
- MISO of an unselected device should be high impedance. Devices that do not tri-state MISO break shared buses.

## Failure modes

| Symptom | Likely cause | Check |
|---|---|---|
| All 0x00 or 0xFF received | Wrong mode, CS not asserted, MISO floating or wiring swapped | Decode CS, SCLK, MOSI, MISO together |
| Data shifted by one bit | CPHA mismatch | Compare sample edge with datasheet timing diagram |
| Works slowly, fails fast | Signal integrity, setup or hold violation, long wires | Lower the clock, add series resistors, shorten traces |
| First byte wrong | CS released too early or too late relative to the transfer | Wait for the peripheral busy flag to clear before releasing CS |
| Corruption with DMA | Buffer alignment, cache coherency, word size mismatch | Check DMA width versus frame size |
| Master-mode fault | Hardware NSS pin pulled low in multi-master setups | Use software NSS management for single-master designs |

Use a logic analyzer with an SPI decoder and verify all four signals before debugging firmware.
