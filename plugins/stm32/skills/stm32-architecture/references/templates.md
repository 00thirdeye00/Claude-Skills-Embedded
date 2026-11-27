# Architecture document templates

## Contents
- ARCHITECTURE.md (index)
- Module contract
- CLAUDE.md pointer
- Decisions log entry

## ARCHITECTURE.md (index)

```markdown
# Architecture: [project]

Last updated: [date]. Target: [MCU, board, toolchain, RTOS].

## How to extend
1. Read this file. 2. Read `modules/<name>.md` for each module you will change.
3. Read the headers of the modules it depends on. 4. Check the resource map for conflicts.
5. Update the module file and the resource map in the same change. Do not scan `src/`.

## Layers and rules
[downward dependencies only; HAL only in bsp; resource ownership; init order]

## Modules
| Module | Layer | Purpose | Public header | Depends on | Used by | Status |
|---|---|---|---|---|---|---|

## Resource map
### Pins
| Pin | Function | AF | Owner module | Notes |
|---|---|---|---|---|
### Peripherals and buses
| Instance | Owner | Mode | DMA | Lock or queue | Devices |
|---|---|---|---|---|---|
### DMA
| Controller and channel or request | Peripheral | Owner | Mode | Memory region |
|---|---|---|---|---|
### Interrupts
| IRQ | Priority | Owner | Context rule |
|---|---|---|---|
### Timers and clocks
| Resource | Use | Owner | Frequency |
|---|---|---|---|
### Memory regions
| Region | Address | Size | Use | Constraints |
|---|---|---|---|---|
### RTOS tasks
| Task | Priority | Stack | Owner | Trigger |
|---|---|---|---|---|

## Initialization order
1. [module]  2. [module]

## Decisions
| Date | Decision | Reason | Consequence |
|---|---|---|---|

## Open items
- OPEN: [question]
```

For the light size, add a short `## Module: <name>` section per module (the contract below) in the same file.

## Module contract

```markdown
# Module: [name]

Layer: [..]   Header: `src/.../<name>.h`   Status: [planned, in progress, stable]   Last changed: [date]

## Purpose
[one or two lines]

## Public API
| Function | Contract | Blocking | Context | Errors |
|---|---|---|---|---|

## Depends on
- Modules: [..]
- Resources (see resource map): [pins, DMA, IRQs, timers, bus]

## Used by
- [modules or tasks]

## Concurrency
[who calls from where; locks; shared data]

## Configuration
[compile-time options and defaults]

## Tests
[unit, loopback, or hardware test and how to run]
```

## CLAUDE.md pointer

Append this section (do not overwrite existing content):

```markdown
## Architecture
Read `docs/architecture/ARCHITECTURE.md` first. To change or extend a module, read its
`docs/architecture/modules/<name>.md` and the headers of the modules it depends on.
Do not scan `src/`. Update the module file and the resource map in the same change.
```

## Decisions log entry

`| 2026-11-24 | SPI bus owned by the storage module, display uses a queue | Avoid two modules locking one bus | Display writes are asynchronous |`
