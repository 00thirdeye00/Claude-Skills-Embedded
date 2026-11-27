# Skill catalog

Single source for routing. Costs are estimates in tokens: skill body plus the largest reference it may load. Skills from `embedded-core` are available only if that plugin is installed.

## Contents
- Catalog
- Known gaps
- Routing notes

## Catalog

| Skill | Use for | Needs | Produces | File | Cost |
|---|---|---|---|---|---|
| `stm32-design` | Design brief: part, clocks, pins, DMA, memory, interrupts, budgets | Requirements; netlist or pin list; datasheets | Design brief with pin, clock, memory, interrupt tables and risks | `../stm32-design/SKILL.md` | ~717 + up to ~1068 |
| `stm32-architecture` | Architecture documents from an approved design: module contracts, resource map, CLAUDE.md pointer; update after changes | Approved design brief, or the change made | `docs/architecture/` files and the CLAUDE.md pointer | `../stm32-architecture/SKILL.md` | ~803 + up to ~699 |
| `stm32-pin-map` | MCU pin table from a KiCad netlist (script), flags, hand-off to design | KiCad netlist or pasted nets | Pin map table with flags and questions | `../stm32-pin-map/SKILL.md` | ~521 + up to ~0 |
| `stm32-cubemx-config` | CubeMX settings checklist from an approved design, or .ioc review | Approved design, or the .ioc | Ordered settings table, differences found | `../stm32-cubemx-config/SKILL.md` | ~372 + up to ~887 |
| `stm32-extend` | Extend existing firmware reading only the index, contracts, and dependency headers | Architecture documents and the change wanted | Impact table, plan, code, updated documents | `../stm32-extend/SKILL.md` | ~598 + up to ~630 |
| `stm32-linker-startup` | Linker script, startup code, map and stack analysis (scripts) | Part memory map, offsets, map file | Regions, findings, usage summary | `../stm32-linker-startup/SKILL.md` | ~454 + up to ~1346 |
| `stm32-testing` | Test strategy, host tests with a fake port, HIL, CI | Module contracts or code layout, CI system | Test plan and CI pipeline | `../stm32-testing/SKILL.md` | ~526 + up to ~1080 |
| `stm32-security` | Threat model, debug and read-out policy, secure boot, TrustZone, keys | Product, threats, part | Security plan with controls and lifecycle | `../stm32-security/SKILL.md` | ~488 + up to ~984 |
| `stm32-rtos` | FreeRTOS or Zephyr setup on STM32 | RTOS, part, pin and priority plan | RTOS configuration, priority table, patterns, overlay | `../stm32-rtos/SKILL.md` | ~462 + up to ~1642 |
| `stm32-peripherals` | One peripheral at a time (GPIO to QSPI) | Peripheral, part, rates, symptom | Settings with calculations, code, verification steps | `../stm32-peripherals/SKILL.md` | ~493 + up to ~1539 |
| `stm32-driver-bringup` | Driver for an external chip from its datasheet | Chip, bus, datasheet excerpt | Bus port, driver skeleton, bring-up and test plan | `../stm32-driver-bringup/SKILL.md` | ~711 + up to ~945 |
| `stm32-debug` | Faults, hangs, resets, silent peripherals | Register values, symptoms, captures | Debug report: root cause, fix, guard | `../stm32-debug/SKILL.md` | ~1372 + up to ~2711 |
| `stm32-power` | Low-power design and diagnosis | Battery, duty cycle, wake sources | Mode plan, sequence, current budget | `../stm32-power/SKILL.md` | ~493 + up to ~965 |
| `stm32-bootloader-ota` | Bootloader, DFU, A/B slots, MCUboot | Flash layout, update transport, security needs | Layout, boot and update sequences, test list | `../stm32-bootloader-ota/SKILL.md` | ~548 + up to ~1796 |
| `stm32-review` | STM32-specific code review | Diff or files, part, HAL version | Severity-ranked findings | `../stm32-review/SKILL.md` | ~572 + up to ~1346 |
| `stm32-release` | Option bytes, protection, production programming | Policy, part, production process | Go/no-go with option-byte table | `../stm32-release/SKILL.md` | ~463 + up to ~907 |
| `embedded-rtos-concepts` | Task design, priorities, stacks, schedulability | Activities with rates and WCET | Task table, timing check | search `**/embedded-rtos-concepts/SKILL.md` (embedded-core) | ~662 + up to ~830 |
| `embedded-isr-concurrency` | ISR rules and shared data | ISR and consumer code | Concurrency findings and mechanism choice | search `**/embedded-isr-concurrency/SKILL.md` (embedded-core) | ~793 + up to ~1036 |
| `embedded-protocols` | Bus theory: sizing, timing, failure modes | Bus, speeds, devices | Calculations and verification steps | search `**/embedded-protocols/SKILL.md` (embedded-core) | ~443 + up to ~646 |
| `embedded-review` | Generic firmware review | Diff or files | Severity-ranked findings | search `**/embedded-review/SKILL.md` (embedded-core) | ~453 + up to ~978 |
| `embedded-debug` | Generic debugging method | Symptom and conditions | Debug report | search `**/embedded-debug/SKILL.md` (embedded-core) | ~450 + up to ~720 |
| `embedded-release` | Generic release checklist | Release facts | Go/no-go checklist | search `**/embedded-release/SKILL.md` (embedded-core) | ~375 + up to ~760 |

## Other plugins

`embedded-core` has `/embedded-core:embedded-orchestrator` for other MCUs. Its generic skills (`embedded-review`, `embedded-debug`, `embedded-release`, `embedded-rtos-concepts`, `embedded-isr-concurrency`, `embedded-protocols`) are listed below only for use by this orchestrator.

## Known gaps

If a stage needs one of these, mark it GAP and log it. The full list is in `docs/skills-backlog.md` of the plugin repository.

- Family-level depth is thin and unaudited against the manuals; facts are flagged for verification.
- Install, trigger, and self-run behavior are untested across Claude apps.
- No non-STM32 platform skills (nRF, ESP32, RP2040, RISC-V, AVR/PIC).
- Peripherals without a reference: USB host and OTG details, CORDIC and FMAC math accelerators, DSI and camera interfaces, low-power UART variants, touch sensing.
- MCUboot guidance has a worked example but no verified configuration.
- No script yet that checks CubeMX `.ioc` files against the design.

## Routing notes

- Prefer the `stm32-` skill for STM32 targets and the `embedded-` generic skill only for other targets or for items the STM32 skill does not cover. Do not run both on the same change.
- `stm32-peripherals` and `embedded-protocols` load one reference per use; name the topic so only one loads.
- `stm32-pin-map` feeds `stm32-design` for a board that already exists; `stm32-cubemx-config` and `stm32-linker-startup` follow the approved architecture; `stm32-extend` replaces reading the code base when architecture documents exist.
- `stm32-architecture` creates the architecture documents after the design is approved and updates them after each change; later stages should read the index and the relevant module contracts instead of the code base.
