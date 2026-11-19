---
name: stm32-design
description: Design an STM32 firmware and hardware-interface plan: choose the family and part, plan the clock tree, pin multiplexing, DMA and peripheral allocation, memory map and linker layout, interrupt priorities, timing, and power budget. Use when starting a new STM32 project, selecting between STM32 parts, laying out pins and peripherals, checking whether a design fits, or planning migration between STM32 families. Trigger with "which STM32 should I use", "plan the pins", "clock configuration", "will this fit on an F4", "interrupt priority plan", "memory map for STM32", "DMA channel conflicts".
argument-hint: "<requirements: peripherals, speed, power, RTOS, memory, or an existing part and pin list>"
---

# /stm32:stm32-design

Produce an STM32 design brief: part choice, clocks, pins, DMA, memory, interrupts, timing, and power, with the trade-offs stated.

## Usage

```
/stm32:stm32-design $ARGUMENTS
```

If requirements are thin, ask for the required peripherals and counts, data rates, deadlines, power source or battery life, RTOS, and package or cost limits.

## How It Works

```
┌────────────────────────────────────────────────────────────┐
│ 1 REQUIREMENTS   peripherals, rates, deadlines, power, cost │
│ 2 PART           family and device with growth margin       │
│ 3 CLOCKS         sources, PLL, buses, kernel clocks         │
│ 4 PINS + DMA     alternate functions, conflicts, requests   │
│ 5 MEMORY         flash layout, RAM regions, stack/heap      │
│ 6 INTERRUPTS     priority plan, RTOS limit                  │
│ 7 BUDGETS        timing, CPU load, current                  │
└────────────────────────────────────────────────────────────┘
```

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

## If Connectors Available

If **~~knowledge base** is connected:
- Pull the datasheet, reference manual, and internal design notes for the chosen part.

If **~~project tracker** is connected:
- Link the design brief to the requirement tickets and create tickets for open risks.

## Tips

1. **Plan the pins before the schematic is frozen**; moving a function later may force a respin.
2. **Keep 30 to 50 percent flash and RAM margin** early; firmware grows.
3. **Choose the family for the peripherals**, not only for CPU speed.
