---
name: stm32-extend
description: Add or change a feature in existing STM32 firmware by reading only the architecture index, the affected module contracts, and dependency headers, not the whole code base.
argument-hint: "<the extension or change to make>"
disable-model-invocation: true
---

# /stm32:stm32-extend

Extend or modify firmware that has architecture documents, with minimal reading. The documents tell you what to read; do not scan the source tree.

## Preconditions

`docs/architecture/ARCHITECTURE.md` must exist. If it does not, stop and recommend `/stm32:stm32-architecture` (create). If the user wants to proceed anyway, list directories and public headers only to build a minimal index first.

## Steps

1. **Read the index only** (`ARCHITECTURE.md`): modules, dependencies, resource map, init order, open items.
2. **Impact analysis** with `references/extension-checklist.md`: which modules change, whether a new module is needed, which resources are touched, and any conflict in the resource map (pins, DMA, interrupt priorities, timers, bus locks, memory, task priorities and stacks, power).
3. **Read the minimum**: the contract file of each affected module, then the public headers of the modules they depend on. Open a `.c` file only when the contract cannot answer the question, and say why. Never scan `src/`.
4. **Show a short plan**: changes per module, new or changed resources, risks, tests. Wait for approval if the change touches more than one module, a shared resource, or an interrupt, DMA, or bus assignment; otherwise proceed.
5. **Implement** in the module layout: HAL only in the board support layer, one owner per resource, tests from the contract.
6. **Update the documents** in the same change: contracts, dependency table, resource map, decisions log. If Python is available run `python ../stm32-architecture/scripts/check_architecture.py --arch docs/architecture/ARCHITECTURE.md --root . --src src Core` and report the result.
7. **Report**: files changed, documents updated, checks run, and what must be verified on hardware.

## Output

```markdown
## Extension: [change]

### Impact
| Module | Change | Resources touched | Conflict |
|---|---|---|---|

### Files read
- [index, contracts, headers; any .c file with the reason]

### Plan and tests
- [..]

### Documents updated
- [..]
```

## Rules

- Resources have one owner. If the change needs a resource another module owns, propose moving ownership or sharing through that module's API; do not touch its internals.
- Do not change generated vendor code outside user sections.
- If the documents and the code disagree, say so and fix the documents or log an open item; do not guess.
