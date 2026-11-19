---
name: embedded-review
description: Review embedded C/C++ firmware changes for correctness, concurrency, memory safety, hardware interaction, timing, error handling, and security on any MCU. Use when reviewing a pull request or diff for firmware, auditing a driver or ISR, checking for MISRA or CERT C issues, or before merging embedded code. Trigger with "review this firmware", "is this driver correct", "check this ISR", "MISRA review", "before I merge this embedded change".
argument-hint: "<diff, file, pull request URL, or code to review>"
---

# /embedded-core:embedded-review

Review firmware code for the defects that matter on constrained, real-time, hardware-facing systems.

## Usage

```
/embedded-core:embedded-review $ARGUMENTS
```

If no code is given, ask for the diff or files, the target MCU or core, the RTOS if any, and the coding standard in force.

## Workflow

1. **Understand the change**: purpose, hardware touched, execution context (main loop, task, ISR).
2. **Walk the checklist** in `references/review-checklist.md`, concentrating on the categories the change touches.
3. **Run what is available**: compile with strict warnings and a static analyzer, and report findings with the commands used.
4. **Rank findings** by severity: Critical (can brick, corrupt, or injure), High (likely field failure), Medium (fragile), Low (style).
5. **Report** with the output template, and say what you did not review.

## Output

```markdown
## Firmware Review: [change summary]

### Context
- Target: [MCU/core], RTOS: [name/none], standard: [MISRA/CERT/none]

### Findings
| # | Severity | Location | Category | Issue | Suggested fix |
|---|---|---|---|---|---|

### What looks good
- [specific strengths]

### Not reviewed
- [areas without enough information: linker script, startup, hardware schematic, timing]

### Suggested tests
- [unit, hardware-in-the-loop, fault injection]
```

## Rules

- Quote the code involved and explain the failure scenario, not just the rule.
- Separate defects from style preferences.
- Do not claim hardware behavior you cannot verify; ask for the reference manual section or a measurement.
- If the user's coding standard conflicts with a suggestion, follow the standard and note the trade-off.

## If Connectors Available

If **~~source control** is connected:
- Pull the diff and linked issues directly and comment on specific lines.

If **~~project tracker** is connected:
- Create tickets for findings that will not be fixed in this change.

## Tips

1. **Give the execution context** of each function; the same code is fine in a task and wrong in an ISR.
2. **Include the linker script and startup** when memory or boot behavior is involved.
3. **Ask for target-specific review** using the platform plugin when one exists (for example `/stm32:stm32-review`).
