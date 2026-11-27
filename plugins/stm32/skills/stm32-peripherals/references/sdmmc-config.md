# STM32 SD card (SDMMC/SDIO) and FatFS

Peripheral version, DMA type, and clock limits differ by family. Confirm in the reference manual and the card specification.

## Setup checklist
- **Bus width**: 1-bit for bring-up, 4-bit for speed. Pull-ups on CMD and DAT lines (card-side requirements), with series resistors and short traces.
- **Clock**: card identification must run at 400 kHz or less; switch to the transfer clock after initialization. Respect the kernel clock and divider limits of the peripheral and the card's maximum.
- **Card initialization**: reset, voltage check, power-up negotiation, read the card registers, select the card, set bus width, then raise the clock. Use the HAL init sequence or a tested stack rather than writing it from scratch.
- **Card detect and power**: use a detect pin or handle read errors; control card power if the board allows it; decide behavior on hot removal.
- **DMA**: use the internal or external DMA the family provides; align buffers as required (commonly 4 bytes, more on cached cores); on cached cores clean and invalidate around transfers or use a non-cacheable buffer.
- **FatFS**: implement the disk I/O layer on the SD driver; set the sector size, enable long file names only if needed, and size the work areas; protect the file system with a mutex when several tasks access it.

## Practical points
- Writes can take tens of milliseconds or more, and occasionally much longer when the card does internal housekeeping; never write from an interrupt or from a time-critical task.
- Open, write, and flush on a policy that survives power loss; sync after critical records.
- Use the same card brand and size class in testing as in production, and test with worn and low-quality cards.

## Failure modes
| Symptom | Likely cause | Check |
|---|---|---|
| Card not detected | Pull-ups, wiring, clock too fast during init, card power | Scope CMD and CLK, lower the init clock |
| Works in 1-bit, fails in 4-bit | Missing DAT pull-ups, trace length, clock too high | Lower the clock, check each data line |
| Random CRC or timeout errors | Signal integrity, buffer alignment, cache, supply sag | Alignment, cache maintenance, supply scope |
| File system corrupt after power loss | No sync policy, writes in progress | Add flushes, power-fail tests |
| Long stalls | Card housekeeping, blocking in a high-priority task | Move disk access to a low-priority task, add timeouts |
