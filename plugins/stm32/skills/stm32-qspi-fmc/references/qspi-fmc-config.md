# STM32 external memory interfaces

Interface features differ by family (Quad-SPI, Octo-SPI, FSMC, FMC). Confirm timing parameters, modes, and limits in the reference manual and the datasheets of both the MCU and the memory.

## Contents
- Quad-SPI and Octo-SPI flash
- Memory-mapped mode and execute-in-place
- FMC and FSMC
- SDRAM initialization
- Cache and MPU attributes
- Failure modes

## Quad-SPI and Octo-SPI flash

A transaction has up to five phases: instruction, address, alternate bytes, dummy cycles, and data. Each phase has its own line width (single, dual, quad, or octal) and size. Take the command codes and dummy-cycle counts from the memory datasheet; the number of dummy cycles depends on the read command and the clock frequency, and some memories have configuration registers to set it.

Bring-up sequence in indirect mode:

1. Reset the memory and wait for its ready time.
2. Read the identification and compare it with the datasheet.
3. Set the quad-enable bit in the status or configuration register (needed on many memories for quad operation), then verify by reading it back.
4. Read a few bytes with the single-line command, then with the fast or quad command.
5. Test erase, write enable, program, and status polling for writes.

Timing: choose the clock divider so the clock meets the memory maximum and the sampling point is stable; some peripherals offer a sampling shift or delay-block setting to recover margin at high clocks. Check the chip-select high time between commands.

## Memory-mapped mode and execute-in-place

In memory-mapped mode the controller issues the read command automatically when the CPU accesses the mapped address range, so the external flash appears as read-only memory and code can execute from it. Configure the read command, dummy cycles, and line widths, then enable the mode. Notes:

- Stop memory-mapped mode (abort) before issuing indirect commands such as erase or program, and return to it afterwards.
- Code running from the external flash must not erase or write the same flash; run those routines from internal memory.
- Interrupt vectors, critical handlers, and the flash driver should be in internal memory.
- A bootloader initializes the interface and jumps into the mapped region, so the application's linker script places code at the mapped address.

## FMC and FSMC

The flexible memory controller drives parallel memories: SRAM, PSRAM, NOR flash, parallel LCD controllers, and on some parts NAND and SDRAM. Configure per bank: data width, memory type, address and data multiplexing, wait and burst settings, and the timing parameters (address setup, data setup, bus turnaround) derived from the memory datasheet and the bus clock period. Start with conservative (slower) timings and tighten them. For LCD controllers, the address line chosen as the data/command select decides which address writes commands.

## SDRAM initialization

SDRAM requires a controller configuration and an initialization sequence issued as commands:

1. Configure timing (row to column delay, precharge, refresh recovery and others) from the SDRAM datasheet and the clock period.
2. Enable the SDRAM clock and wait the specified power-up delay.
3. Issue a precharge-all command.
4. Issue the required number of auto-refresh commands.
5. Load the mode register (burst length, CAS latency, and others).
6. Program the refresh rate counter so every row is refreshed within the retention time.

Take every value from the SDRAM datasheet; wrong settings give data that looks correct for a while and then corrupts.

## Cache and MPU attributes

On cores with caches, external memory regions need attributes through the MPU: memory-mapped external flash is usually cacheable and read-only; external RAM used by the CPU is cacheable, but regions shared with DMA or display controllers need either non-cacheable attributes or cache maintenance; device-style regions (LCD command registers on an FMC bank) must not be cached or reordered. Speculative accesses to unmapped addresses can fault on some cores, so restrict the MPU regions to the real size.

## Failure modes

| Symptom | Likely cause | Check |
|---|---|---|
| ID read fails | Wiring, chip-select, clock, memory in a different mode, power-up delay missing | Scope the clock and chip-select; reset the memory; delay after power-up |
| ID correct, data wrong | Dummy cycles, sampling point, clock too high | Lower the clock; set the dummy cycles from the datasheet |
| Memory-mapped reads return zeros or fault | Mode not configured, wrong command, MPU or cache attributes, address wrong | Verify the mapped mode settings and the address range |
| Code in external flash crashes randomly | Erase or program running from the same flash, interrupt in mapped region during mode change | Move write code to internal memory; handle interrupts |
| Parallel memory works slowly or fails | Timing too tight, data width mismatch | Relax the timings; check the width and address lines |
| SDRAM corrupts over time | Refresh rate or initialization wrong | Recheck the initialization sequence and the refresh counter |
