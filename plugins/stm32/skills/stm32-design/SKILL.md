---
name: stm32-design
description: Produce an STM32 design brief: part choice, clock tree, pins, DMA, memory map, interrupt priorities, and timing and power budgets.
argument-hint: "<requirements: peripherals, speed, power, RTOS, memory, or an existing part and pin list>"
disable-model-invocation: true
---

# /stm32:stm32-design

Produce an STM32 design brief: part choice, clocks, pins, DMA, memory, interrupts, timing, and power, with the trade-offs stated.

If requirements are thin, ask for the required peripherals and counts, data rates, deadlines, power source or battery life, RTOS, and package or cost limits.

## Steps

1. **Capture requirements** and turn them into numbers: instance counts per peripheral, throughput, latency, flash and RAM with growth margin, temperature range, supply.
2. **Select the part** using `references/mcu-selection.md`. Offer a primary choice and an alternative, and state what would change the choice.
3. **Plan clocks, pins, DMA, memory, and interrupts** using `references/pin-clock-dma-planning.md`. Resolve conflicts on paper before layout or CubeMX.
4. **Budget** timing, CPU load, and current. Mark every estimate as an estimate.
5. **List risks and verification steps**: items to confirm in the datasheet, reference manual, and errata sheet.

## Output

```markdown
## STM32 Design Brief: [project]

### Requirements
| Item | Value |
|---|---|

### Part selection
- Primary: [part], alternative: [part], rationale: [...]

### Clock plan
| Clock | Source | Frequency | Notes |
|---|---|---|---|

### Pin and peripheral plan
| Function | Peripheral | Pin(s) | AF | DMA | Notes |
|---|---|---|---|---|---|

### Memory plan
| Region | Address range | Use | Constraints |
|---|---|---|---|

### Interrupt plan
| Priority | Sources | Rationale |
|---|---|---|

### Budgets
- CPU load: [..]; worst-case latency: [..]; current: [..]

### Risks and checks
- [item to verify against the datasheet, reference manual, errata]
```

## Rules

- Take alternate-function numbers from the datasheet table, not from memory.
- Reserve debug pins, reset, boot, and oscillator pins before allocating the rest.
- State which choices are fixed by silicon (for example which DMA can reach which RAM) and which are flexible.
- Flag any assumption about a specific part number that you have not verified.

## Connectors

Optional (see `CONNECTORS.md`): when `~~source control`, `~~project tracker`, or `~~knowledge base` is connected, use it for diffs, tickets, and datasheets.
