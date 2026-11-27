---
name: stm32-orchestrator
description: Plan and run a multi-step STM32 firmware goal (for example "design and develop firmware for this board"): produce a staged plan for approval, then run the needed skills in order, and log missing or insufficient skills to a backlog.
argument-hint: "<goal and hardware: part, board files, requirements, toolchain>"
disable-model-invocation: true
---

# /stm32:stm32-orchestrator

Supervisor for moderate-to-complex firmware goals. It plans first, acts only after you approve, and records skill gaps.

If the goal is a single small task, say so and recommend the one matching command instead of orchestrating.

## 1. Understand

Read the goal and any supplied hardware data. Ask only for what blocks planning: exact part number, what the product must do, toolchain, RTOS, and which inputs exist (netlist, BOM, datasheets, code).

## 2. Plan (no actions yet)

1. Read `references/skill-catalog.md` once. Pick the closest playbook in `references/playbooks.md` and tailor it to the goal.
2. For each stage choose the skill, the inputs it needs, the deliverable, and a checkpoint. Mark stages with no suitable skill as GAP.
3. Present the plan in the format in `references/templates.md`, with the token estimate and the gaps. Then stop and ask: approve and self-run, hand-off commands only, or edit.
4. Log each gap to the backlog now (section 4).

## 3. Execute (only after approval)

For each stage, in order:

1. Locate the skill file: `../<skill>/SKILL.md` relative to this skill's directory. For a skill from another plugin, search for `**/<skill>/SKILL.md`. If it cannot be found, treat it as a GAP (not installed) and give the hand-off command for that stage.
2. Read that SKILL.md, then only the reference files it directs you to for this stage. Follow it as if it had been invoked with the stage inputs.
3. Produce the deliverable. If you can write files, save decisions (pin plan, clock plan, priorities, open risks) to `firmware-plan.md` in the working directory, and read that file in later stages instead of re-deriving.
4. Give a short summary. Pause at checkpoints that need the user (hardware measurements, irreversible choices, conflicting data); otherwise continue.

Hand-off mode: do not read or run skills. Output the commands to paste, one per message, with the stage inputs filled in.

## 4. Skills backlog

A skill is missing or insufficient when: no skill covers the stage; the skill does not cover the family, peripheral, or chip involved; it needs facts that cannot be verified; the user rejects its output as wrong; or its output cannot meet the stage deliverable.

When that happens:
1. Tell the user in the reply: what is missing, why, and the impact.
2. Continue with general knowledge only if it is safe, labeled "not skill-backed, verify". Pause if the matter is safety-related or irreversible.
3. Append an entry to the backlog file using the format in `references/templates.md`. Use `docs/skills-backlog.md` if it exists, otherwise `skills-backlog.md` in the working directory (create it). Check existing entries and update rather than duplicate. If you cannot write files, print the entries for the user to save.

## Rules

- Never act before approval. Never apply irreversible steps (read-out protection level 2, production option bytes, mass programming) without explicit confirmation.
- One skill at a time. Load nothing you do not need. Do not re-run a finished stage unless its inputs changed.
- Mark estimates as estimates and unverified facts as unverified.
- Orchestration costs extra tokens (catalog, plan, notes). Skip it for small tasks.
