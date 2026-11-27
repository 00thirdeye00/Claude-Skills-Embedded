---
name: stm32-cubemx-config
description: Turn an approved STM32 design (pins, clocks, DMA, interrupts, RTOS) into an ordered CubeMX settings checklist, or review an existing .ioc against the design.
argument-hint: "<approved design, or the .ioc to review>"
disable-model-invocation: true
---

# /stm32:stm32-cubemx-config

Produce the exact settings to enter in STM32CubeMX for an approved design, or review an existing `.ioc` file against it. Claude does not run CubeMX; you enter the settings and generate the project.

## Steps

1. **Inputs**: the approved design (pin, clock, DMA, interrupt, RTOS plan) and, if reviewing, the `.ioc` file (a text file).
2. **Create mode**: write an ordered checklist from `references/cubemx-checklist.md`, with each setting's value and the design item it comes from.
3. **Review mode**: compare the `.ioc` with the design and list differences: pins and alternate functions, clock frequencies, NVIC priorities and grouping, DMA mapping, timebase source, middleware settings.
4. **Project settings**: toolchain choice, per-peripheral file generation, user-code preservation, stack and heap sizes.
5. **After generation**: where hand-written code goes, what not to edit, and how to keep the `.ioc` in version control.

## Output

```markdown
## CubeMX Settings: [project]

| Tab | Setting | Value | From design |
|---|---|---|---|

### Differences found (review mode)
- [..]

### After generating
- [..]
```

## Rules

- Menu names and options change between CubeMX versions; tell the user to verify names against their version.
- Take values from the approved design; do not invent clock or AF values.
- Do not hand-edit generated files outside the user-code sections.
- For Zephyr projects use `/stm32:stm32-rtos` (overlays and Kconfig) instead.
