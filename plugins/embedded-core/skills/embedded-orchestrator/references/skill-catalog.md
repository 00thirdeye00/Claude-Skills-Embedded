# Skill catalog (embedded-core)

Costs are rough token estimates: skill body plus the largest reference it may load.

## Contents
- Catalog
- Playbook: generic firmware project
- Platform plugins
- Known gaps

## Catalog

| Skill | Use for | Needs | Produces | File | Cost |
|---|---|---|---|---|---|
| `embedded-rtos-concepts` | Task design, priorities, IPC, stacks, schedulability | Activities with rates and WCET | Task table, timing check | `../embedded-rtos-concepts/SKILL.md` | ~660 + up to ~830 |
| `embedded-isr-concurrency` | ISR rules and shared data | ISR and consumer code or design | Findings and mechanism choice | `../embedded-isr-concurrency/SKILL.md` | ~790 + up to ~1,040 |
| `embedded-protocols` | Bus theory: sizing, timing, failure modes | Bus, speeds, devices | Calculations and verification steps | `../embedded-protocols/SKILL.md` | ~440 + up to ~650 |
| `embedded-review` | Generic firmware review | Diff or files | Severity-ranked findings | `../embedded-review/SKILL.md` | ~450 + up to ~980 |
| `embedded-debug` | Generic debugging method | Symptom and conditions | Debug report | `../embedded-debug/SKILL.md` | ~450 + up to ~720 |
| `embedded-release` | Release checklist | Release facts | Go/no-go checklist | `../embedded-release/SKILL.md` | ~380 + up to ~760 |

## Playbook: generic firmware project

1. Collect inputs: MCU, requirements, toolchain, RTOS, hardware documents.
2. Platform setup (clocks, pins, drivers, bootloader, linker): GAP unless a platform plugin is installed.
3. `embedded-protocols` for each bus: sizing and timing. Checkpoint (you): verify on the bench.
4. `embedded-rtos-concepts`: task table, priorities, stacks, timing check.
5. `embedded-isr-concurrency` for each interrupt and shared data path.
6. `embedded-review` on the code. Checkpoint (you): fix or accept findings.
7. `embedded-debug` for failures as they occur.
8. `embedded-release`.

## Platform plugins

| Platform | Plugin and orchestrator | Status |
|---|---|---|
| STM32 | `stm32` with `/stm32:stm32-orchestrator` | Available |
| nRF, ESP32, RP2040, RISC-V, AVR/PIC | none | Planned |

## Known gaps

- No platform-specific skills outside STM32.
- No generic skills for architecture documents, testing and CI, linker and startup, or security; the `stm32` plugin has STM32 versions of these.
