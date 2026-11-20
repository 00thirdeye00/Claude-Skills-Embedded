---
name: stm32-review
description: Review STM32 firmware for target-specific defects: HAL/LL use, clocks, interrupts, DMA and cache, RTOS limits, flash and option bytes.
argument-hint: "<diff, files, project structure, or pull request URL>"
disable-model-invocation: true
---

# /stm32:stm32-review

Review STM32 firmware for correctness, robustness, and STM32-specific pitfalls.

If no code is given, ask for the changed files, the exact part number, the HAL or LL version, the RTOS, and the clock configuration.

## Steps

1. **Establish context**: part, core, FPU and cache presence, HAL or LL or register level, generated code versus hand-written, RTOS, and bootloader.
2. **Apply the general checklist.** If the `embedded-core` plugin is installed, use `/embedded-core:embedded-review` for the platform-independent items; otherwise apply the summary in `references/stm32-review-checklist.md`.
3. **Apply the STM32 checklist** to every file touched.
4. **Separate generated from hand-written code.** Review hand-written code and user sections of generated code; for generated files, check settings, not style.
5. **Report** using the template.

## Output

```markdown
## STM32 Review: [change summary]

### Context
- Part: [..], core: [..], HAL/LL: [..], RTOS: [..]

### Findings
| # | Severity | File:line | Category | Issue | Fix |
|---|---|---|---|---|---|

### Verified OK
- [things checked and found correct]

### Needs confirmation
- [items requiring the reference manual, errata, or a measurement]
```

## Rules

- Rank severity by consequence: can brick or corrupt data, likely field failure, fragile, style.
- State the failure scenario for each finding.
- For register-level or family-specific claims, say what must be confirmed in the reference manual or errata sheet for the exact part.
- Do not rewrite generated files by hand; recommend changing the configuration or moving code into user sections.

## Connectors

Optional (see `CONNECTORS.md`): when `~~source control`, `~~project tracker`, or `~~knowledge base` is connected, use it for diffs, tickets, and datasheets.
