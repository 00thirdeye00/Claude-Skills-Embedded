---
name: stm32-qspi-fmc
description: Configure and debug STM32 external memory interfaces: Quad-SPI and Octo-SPI flash with indirect and memory-mapped modes, command phases, dummy cycles, quad-enable setup, and execute-in-place, plus the flexible memory controller (FMC or FSMC) for SRAM, PSRAM, NOR, LCD, and SDRAM with timing and initialization sequences, and the cache and MPU attributes these regions need. Use when an external flash or RAM does not respond, returns wrong data when memory-mapped, or runs slowly. Trigger with "STM32 QSPI", "OctoSPI flash", "memory-mapped flash", "external SDRAM STM32", "FMC timing", "execute in place", "PSRAM on STM32", "dummy cycles".
argument-hint: "<memory part, interface, mode, clock, or the symptom>"
---

# /stm32:stm32-qspi-fmc

Bring up external flash and RAM on STM32 memory interfaces.

## Usage

```
/stm32:stm32-qspi-fmc $ARGUMENTS
```

If details are missing, ask for the part, the external memory part number and datasheet, the interface and clock, the mode (indirect, memory-mapped, execute-in-place), and what is read back.

## Workflow

1. **Take the command set and timing** from the memory datasheet: read commands, dummy cycles for the chosen clock, address width, quad-enable bit, and initialization sequence.
2. **Configure the interface**: clock, chip-select timing, sampling shift, instruction, address, and data lines.
3. **Bring up in indirect mode first**: read the ID, then a status register, then data.
4. **Enable memory-mapped mode** with the right read command and dummy cycles; set the MPU and cache attributes.
5. **Verify** with a data pattern, a speed test, and, for execute-in-place, a reset-and-run test.

Details, configuration checklists, example code, and failure modes are in `references/qspi-fmc-config.md`.

## Choosing an approach

| Need | Use |
|---|---|
| Initial bring-up and writes | Indirect mode with explicit commands |
| Read-heavy data or code in external flash | Memory-mapped mode, with the read command, dummy cycles, and cache settings set |
| Parallel SRAM, PSRAM, LCD | FMC with matched address-setup and data-setup timing |
| Large RAM | SDRAM through FMC with the full initialization sequence and refresh rate |
| Higher throughput | Quad or octal lines, higher clock, DMA |

## Output

```markdown
## QSPI, OctoSPI, and FMC Plan: [context]

### Interface parameters (lines, clock, dummy cycles, timing)
- [..]

### Initialization sequence
- [..]

### Memory attributes (cache, MPU)
- [..]

### Verification steps
- [..]
```

## Rules

- Take command codes, dummy cycles, and timings from the memory datasheet, not from memory.
- State the dependency of dummy cycles on the clock frequency.
- Define the cache and MPU attributes for each external region.
- Confirm register-level and family-specific details against the reference manual, datasheet, and errata sheet for the exact part.

## Tips

1. **ID reads work but data is wrong**: dummy cycles, sampling shift, or clock too high.
2. **Memory-mapped reads fail** after reset if the memory is still in an unexpected mode; reset or re-enter the known mode in init.
3. **Write operations** need write-enable commands and status polling.
