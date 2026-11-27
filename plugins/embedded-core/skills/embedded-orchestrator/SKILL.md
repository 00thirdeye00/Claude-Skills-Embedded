---
name: embedded-orchestrator
description: Plan and run a multi-step embedded firmware goal on any MCU: produce a staged plan for approval, run the needed generic skills in order, hand platform-specific stages to the platform plugin when installed, and log gaps to a backlog.
argument-hint: "<goal and hardware: MCU, board files, requirements, toolchain>"
disable-model-invocation: true
---

# /embedded-core:embedded-orchestrator

Supervisor for moderate-to-complex firmware goals on any MCU. It plans first, acts only after approval, and records skill gaps.

If the target is an STM32 and the `stm32` plugin is installed (search for `**/stm32-orchestrator/SKILL.md`), recommend `/stm32:stm32-orchestrator` instead, which knows the STM32 skills. If the goal is one small task, recommend the single matching command.

## 1. Understand

Read the goal and supplied hardware data. Ask only for what blocks planning: MCU part, what the product must do, toolchain, RTOS, and which inputs exist.

## 2. Plan (no actions yet)

1. Read `references/skill-catalog.md` once and pick the closest playbook there; tailor it.
2. For each stage choose the skill, inputs, deliverable, and checkpoint. Platform-specific stages (clock and pin setup, drivers for the MCU's peripherals, bootloader, linker and startup) have no generic skill: mark them GAP unless a platform plugin for this MCU is installed.
3. Present the plan in the format in `references/templates.md` with the token estimate and gaps, then stop and ask: approve and self-run, hand-off commands only, or edit.
4. Log each gap to the backlog (section 4).

## 3. Execute (only after approval)

For each stage, in order:
1. Locate the skill: `../<skill>/SKILL.md` relative to this skill's directory; for another plugin search `**/<skill>/SKILL.md`. If not found, treat as a GAP and give the hand-off command.
2. Read that SKILL.md and only the references it directs you to for this stage. Follow it as if invoked with the stage inputs.
3. Produce the deliverable; save decisions to `firmware-plan.md` in the working directory if you can write files, and reuse it in later stages.
4. Summarize briefly. Pause at checkpoints that need the user (measurements, irreversible choices, conflicting data).

Hand-off mode: output the commands to paste, one per message, with inputs filled in.

## 4. Skills backlog

A skill is missing or insufficient when no skill covers the stage, it does not cover the MCU or peripheral involved, it needs facts that cannot be verified, the user rejects its output, or it cannot meet the stage deliverable. Then: tell the user what is missing and the impact; continue with general knowledge only if safe, labeled "not skill-backed, verify"; pause for safety or irreversible matters; append an entry (format in `references/templates.md`) to `docs/skills-backlog.md` if it exists, otherwise `skills-backlog.md` in the working directory. Update existing rows instead of duplicating. If you cannot write files, print the entries.

## Rules

- Never act before approval. Never apply irreversible steps without explicit confirmation.
- One skill at a time. Load nothing you do not need. Do not re-run a finished stage unless its inputs changed.
- Mark estimates as estimates and unverified facts as unverified. Skip orchestration for small tasks.
