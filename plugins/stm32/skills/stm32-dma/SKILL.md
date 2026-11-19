---
name: stm32-dma
description: Configure and debug STM32 DMA: request mapping (stream and channel tables or the DMA request multiplexer), normal, circular, and double-buffer modes, data widths, FIFO and burst settings, interrupts and flags, memory regions the DMA can reach, and cache coherency on cached cores. Use when a DMA transfer never starts, completes with wrong data, stops after one transfer, or when planning DMA use across peripherals. Trigger with "STM32 DMA", "DMA not working", "DMA circular", "DMA transfer error", "DMA channel conflict", "DMA cache coherency", "DMAMUX", "DMA stream mapping".
argument-hint: "<peripheral and direction, buffer locations, mode, or the symptom>"
---

# /stm32:stm32-dma

Plan and troubleshoot STM32 DMA transfers.

## Usage

```
/stm32:stm32-dma $ARGUMENTS
```

If details are missing, ask for the part, the peripheral and direction, data widths, buffer addresses and memory regions, the mode (one-shot or circular), and any DMA error flags.

## Workflow

1. **List the transfers** with peripheral, direction, width, rate, and mode.
2. **Map each to a DMA channel or stream** using the request table or the multiplexer; resolve conflicts.
3. **Check memory reach and cache**: the buffer's RAM region must be reachable, aligned, and coherent.
4. **Configure** addresses, increments, widths, priority, mode, and interrupts; enable the peripheral's DMA request.
5. **Verify** with a known pattern, then check callbacks, flags, and the counter.

Details, configuration checklists, example code, and failure modes are in `references/dma-config.md`.

## Choosing an approach

| Need | Use |
|---|---|
| Move a block once | Normal mode, completion interrupt |
| Continuous sampling or reception | Circular mode with half and full callbacks |
| Ping-pong without gaps | Double-buffer mode where supported, or circular with two halves |
| Memory to memory | A controller that supports it (check the part), or a software copy |
| Peripheral on a cached core | Non-cacheable buffer region, or explicit cache clean and invalidate |

## Output

```markdown
## DMA Plan: [context]

### Transfer table (peripheral, direction, controller, channel or request, width, mode)
- [..]

### Memory and cache plan
- [..]

### Interrupt and callback plan
- [..]

### Verification steps
- [..]
```

## Rules

- Take the request mapping from the reference manual for the exact part.
- Check that the buffer region is reachable by the chosen controller.
- Do not reuse a channel while a transfer is active; check state before restart.
- Confirm register-level and family-specific details against the reference manual, datasheet, and errata sheet for the exact part.

## Tips

1. **Nothing happens**: the peripheral's own DMA enable bit, or the request mapping.
2. **Data wrong on cached cores**: cache clean and invalidate, alignment to the cache line.
3. **Transfer error flag**: wrong address region, unsupported width or alignment.
