# STM32 SPI configuration

HAL names are shown for orientation; confirm against your HAL version. The SPI peripheral differs between families (notably the newer peripheral on the high-performance families).

## Contents
- Timing and baud rate
- Pin setup
- Frame format and chip-select
- Transfer modes
- Slave mode
- Failure modes
- Quick selection guide
- Tips

## Timing and baud rate

The SPI clock is the kernel or bus clock divided by a power-of-two prescaler (starting at 2). Choose the largest rate that meets all of: the device maximum clock, the setup and hold times, and signal integrity on the board. Record the real kernel clock and the prescaler:

```
SCLK = kernel_clock / prescaler       prescaler in {2, 4, 8, ...}
```

Set CPOL and CPHA to match the device (see the protocols reference table).

## Pin setup

Configure SCK, MOSI, and MISO as alternate function with the right AF. Set the output speed high enough for the clock (very fast clocks need fast edges, but faster edges mean more ringing and EMI). Drive chip-select as a GPIO output for full control, and keep it high until the transfer begins.

## Frame format and chip-select

- Data size is commonly 8 or 16 bits; the device protocol decides. Check bit order (MSB or LSB first).
- Use software chip-select for protocols that need several transfers under one selection (command then data), because hardware NSS pulses between frames on some configurations.
- Many devices need chip-select asserted a short time before the first clock and held after the last; add delays if the datasheet requires them.
- Release chip-select only after the transmission is complete and the peripheral busy flag is clear. Releasing it at the end of a DMA call can truncate the final bits.

## Transfer modes

| Mode | HAL examples | Notes |
|---|---|---|
| Polling | `HAL_SPI_Transmit`, `HAL_SPI_Receive`, `HAL_SPI_TransmitReceive` | Simple; blocks |
| Interrupt | `..._IT` | Callback on completion |
| DMA | `..._DMA` | Needs both transmit and receive channels for full duplex; callback on completion |

Notes for DMA: match the DMA data width to the frame size (16-bit frames need half-word transfers), keep buffers valid until the callback, and on cached cores clean and invalidate the cache ranges. In receive-only operation the peripheral still needs clocks, so the HAL generates dummy transmit data.

## Slave mode

Use hardware NSS or software NSS carefully; handle the first-byte preload problem (the transmit register must be loaded before the master starts clocking) and overruns. Keep handlers short and prefer DMA.

## Failure modes

| Symptom | Likely cause | Check |
|---|---|---|
| All 0x00 or 0xFF received | Wrong mode, chip-select not asserted, MISO not connected, device unpowered | Decode all signals on a logic analyzer |
| Bits shifted | CPOL or CPHA wrong | Compare the sample edge to the datasheet |
| Last byte wrong | Chip-select released early; DMA complete versus peripheral busy | Wait for the busy flag to clear |
| Works slowly only | Edges too slow or ringing, setup and hold violation | Lower the clock, adjust pin speed, shorten wires |
| 16-bit data byte-swapped | Frame size versus byte order mismatch | Check the data size and DMA width |
| Corrupt with DMA on cached cores | Cache coherency, alignment | Clean and invalidate; align buffers |
| Master mode fault | Hardware NSS input pulled low | Use software NSS management in single-master designs |

## Quick selection guide

| Situation | Use |
|---|---|
| Short register access | Blocking transmit and receive with a timeout |
| Bulk data, display, flash | DMA for both directions; release chip-select after the transfer and busy flag complete |
| Many devices on one bus | One chip-select per device, mutex around the bus |
| Act as a slave | Hardware or software NSS, interrupt or DMA, careful FIFO handling |

## Tips

1. **All 0xFF or 0x00** points to chip-select, mode, wiring, or a powered-down device.
2. **Reduce the clock** to separate timing issues from logic bugs.
3. **Set output speed** of the SPI pins high enough for the clock but no higher than needed.
