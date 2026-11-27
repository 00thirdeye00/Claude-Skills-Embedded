# Templates

## Contents
- Plan
- Progress line
- Backlog entry
- firmware-plan.md

## Plan

```markdown
## Plan: [goal]

Target: [part, board, toolchain, RTOS]
Assumptions: [list]

| # | Stage | Skill | Inputs needed | Deliverable | Checkpoint | Est. tokens |
|---|---|---|---|---|---|---|

Gaps: [none, or each gap with its backlog ID]
Total estimate: [sum, plus orchestration overhead]
Questions before start: [only blocking ones]

Choose: (1) approve and self-run, (2) hand-off commands only, (3) edit the plan.
```

## Progress line

`Stage 3/9 done: stm32-rtos. Saved to firmware-plan.md. Next: stm32-peripherals (UART log).`

## Backlog entry

Append one row per gap to the table in the backlog file:

| ID | Date | Type | Skill | Gap | Exposed by | Proposed scope | Priority | Status |
|---|---|---|---|---|---|---|---|---|
| B-0NN | YYYY-MM-DD | new or update | skill name | what is missing or wrong | the task that hit it | what the skill should cover | H, M, or L | open |

Use the next free ID. Update the existing row instead of adding a duplicate.

## firmware-plan.md

```markdown
# Firmware plan
## Target
## Decisions (pin plan, clocks, priorities, memory)
## Stage log (stage, skill, date, result)
## Open risks and items to verify on hardware
## Gaps logged
```
