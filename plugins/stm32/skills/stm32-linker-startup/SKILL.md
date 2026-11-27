---
name: stm32-linker-startup
description: Write or review STM32 linker scripts and startup code: memory regions, sections, vector table placement, DMA buffer sections, stack and heap, bootloader offsets, and map-file and stack analysis.
argument-hint: "<part, memory layout, bootloader offset, the linker script or map, or the symptom>"
disable-model-invocation: true
---

# /stm32:stm32-linker-startup

Author or review the linker script and startup code, and read the map file and stack usage.

## Steps

1. **Inputs**: exact part and its memory map from the reference manual, bootloader or slot offsets, regions needed for DMA, retention, or external memory, stack and heap policy, RTOS, and the current linker script or map if any.
2. **Linker script**: regions, sections, load versus run addresses, vector table alignment, special sections, stack and heap. Use `references/linker-startup.md`.
3. **Startup**: reset sequence (stack pointer, data copy, bss clear, clock and FPU setup, constructors, `main`), default and fault handlers, vector table contents.
4. **Analyze a build**: build with `-Wl,-Map=firmware.map -fstack-usage`, then run `python scripts/map_summary.py firmware.map` for region usage and largest contributors, and `python scripts/stack_usage.py build/` for the largest frames. If Python or files are not available, ask the user to run them and paste the output.
5. **Verify**: vector table at the expected address, `.data` load address, sizes within regions, alignment, and the application's `VTOR` when started by a bootloader.

## Output

```markdown
## Linker and Startup: [project]

### Memory regions
| Region | Origin | Length | Use |
|---|---|---|---|

### Findings or changes
- [..]

### Map and stack summary
- [region usage, largest contributors, large frames]

### Verification
- [commands and expected results]
```

## Rules

- Take addresses and sizes from the reference manual for the exact part; do not guess regions.
- Do not edit vendor startup files without noting what changes and why.
- The scripts were tested on synthetic map and stack files in the documented formats; check results against `arm-none-eabi-size` and `objdump` on your build.
