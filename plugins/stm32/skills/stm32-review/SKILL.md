---
name: stm32-review
description: Review STM32 firmware for target-specific defects: wrong HAL or LL usage, missing clock enables, interrupt flag handling, DMA and cache coherency, interrupt priority and RTOS limits, flash and option-byte handling, linker script and startup problems, errata exposure, and power-mode mistakes. Use when reviewing STM32 code, a CubeMX-generated project, a driver, or a pull request for an STM32 target, before merging or releasing. Trigger with "review my STM32 code", "check this HAL driver", "is my DMA setup right", "review CubeMX project", "audit interrupt priorities".
argument-hint: "<diff, files, project structure, or pull request URL>"
---

# /stm32:stm32-review

Review STM32 firmware for correctness, robustness, and STM32-specific pitfalls.

## Usage

```
/stm32:stm32-review $ARGUMENTS
```

If no code is given, ask for the changed files, the exact part number, the HAL or LL version, the RTOS, and the clock configuration.

## How It Works

```
┌───────────────────────────────────────────────────────────┐
│ 1 CONTEXT    part, core, HAL/LL, RTOS, execution contexts │
│ 2 GENERIC    embedded checklist (embedded-review)         │
│ 3 STM32      references/stm32-review-checklist.md         │
│ 4 REPORT     severity-ranked findings with fixes          │
└───────────────────────────────────────────────────────────┘
```

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

## If Connectors Available

If **~~source control** is connected:
- Fetch the diff and comment on lines.

If **~~project tracker** is connected:
- File tickets for deferred findings.

## Tips

1. **Include the `.ioc` or equivalent** so clock and pin settings can be reviewed.
2. **State the HAL version**; function behavior and names change between releases.
3. **Provide the linker script** when memory placement or DMA buffers are involved.
