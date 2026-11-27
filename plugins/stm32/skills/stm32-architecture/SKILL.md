---
name: stm32-architecture
description: Generate or update the firmware architecture documents (index, module contracts, resource map) from an approved design, so later extensions read only what they need.
argument-hint: "<approved design brief, or 'update' plus the change just made>"
disable-model-invocation: true
---

# /stm32:stm32-architecture

Turn an approved design into a small, layered set of architecture documents for the firmware repository, and keep them current after changes. The goal: a later extension reads the index, the target module's contract, and the headers it depends on, not the whole code base.

If there is no approved design, ask for one or recommend `/stm32:stm32-design` first.

## Create (right after design approval)

1. **Inputs.** Use the approved design brief (pin, clock, DMA, memory, interrupt plan). If code already exists, list its directories only; do not read files.
2. **Choose the size.** Light (about 8 modules or fewer): one `ARCHITECTURE.md` with a short section per module. Full: an index plus one file per module.
3. **Decompose into modules** by layer, using `references/modularity-rules.md`: board support, drivers, services, application. Dependencies point downward only. Each module has one purpose and one public header.
4. **Build the resource map**: every limited or shared resource with its owner (pins, peripherals, DMA, interrupts and priorities, timers, buses, clocks, memory regions, RTOS tasks and stacks, init order). This is what makes "read only the dependencies" safe.
5. **Write the documents** from `references/templates.md`. Use tables, not prose. Mark unknowns as `OPEN: <question>` and list them under open items.
6. **Stop for approval.** Show the module list, dependency table, and resource map. No code is written until the user approves the architecture.
7. **After approval,** write the files (or print them if you cannot write files) and add the pointer section to the repository's `CLAUDE.md`.

## Update (after a change)

1. Input: a summary of the change or the list of changed files. Read only those files' headers and the existing architecture documents.
2. Update the affected module contracts, the dependency table, and the resource map. Add a line to the decisions log when a decision changed.
3. Check consistency: a resource has one owner, dependencies still point downward, and no module is missing a contract. If Python and the source tree are available, run `python scripts/check_architecture.py --arch docs/architecture/ARCHITECTURE.md --root . --src src Core`; it reports upward or undeclared dependencies, duplicate resources, unknown owners, missing contracts, and interrupt-priority drift (see its header for limits).
4. Report what changed and any conflict or new open item.

## Output

```markdown
## Architecture: [project]

Mode: create or update; size: light or full

### Modules
| Module | Layer | Purpose | Depends on |
|---|---|---|---|

### Resource conflicts or open items
- [..]

### Files
- [paths written or to write]
```

## Rules

- Never read the whole code base. Never rewrite generated code (CubeMX output stays in its own area).
- Keep the documents compact and current: a stale document is worse than none. Every code change updates the module file and the resource map in the same change.
- Facts about the part (alternate functions, DMA mappings) come from the approved design; flag anything unverified.
- This costs tokens once and saves them on every later extension; for a very small project use the light size.
