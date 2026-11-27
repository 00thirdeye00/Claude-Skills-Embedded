# Platform expansion plan

This plan covers backlog item B-012: new platform plugins beyond STM32. It is a plan, not a result.

## Contents
- Gate
- Order
- Plugin template
- Per-platform notes
- Effort and sequencing

## Gate

Start a second platform after the STM32 plugin has passed the verification plan (`docs/verification-plan.md`, tests 1 to 9 in Claude Code and the priority-family audit). Otherwise the same unverified patterns get copied.

## Order

1. **nRF** (Nordic): Zephyr-based development is the main path, so it reuses the Zephyr and RTOS material; adds Bluetooth Low Energy and power-focused skills.
2. **ESP32**: ESP-IDF with FreeRTOS, Wi-Fi and Bluetooth, partition tables and OTA; a large user base.
3. **RP2040**: Pico SDK, PIO state machines, dual core; small and well documented.
4. **RISC-V** (generic cores and vendor families): different debug and fault model; start once the pattern is proven.
5. **AVR and PIC**: bare-metal-heavy, no RTOS focus; lowest priority.

Choose a different order if your own projects need another platform first.

## Plugin template

Each platform plugin follows the `stm32` layout, with skills renamed by prefix (`nrf-...`):

| Skill | Purpose |
|---|---|
| `<p>-orchestrator` | Plan and run multi-stage goals, backlog |
| `<p>-architecture`, `<p>-extend` | Architecture documents and extension (the templates are platform-neutral and can move to `embedded-core`) |
| `<p>-design` | Part choice, clocks, pins, memory, interrupts |
| `<p>-debug` | Fault and hang debugging for that core and SDK |
| `<p>-driver-bringup` | Drivers in the module layout |
| `<p>-peripherals` | One reference per peripheral |
| `<p>-rtos` | RTOS and SDK integration |
| `<p>-power`, `<p>-bootloader-ota`, `<p>-release`, `<p>-review`, `<p>-testing`, `<p>-security` | As for STM32, adapted |

All skills are manual (`disable-model-invocation: true`), with short bodies, references loaded on demand, `README.md`, `CONNECTORS.md`, `LICENSE`, a catalog and playbooks for the orchestrator, and tests for any scripts.

Refactor first: move platform-neutral parts (architecture templates, modularity rules, test and CI reference, generic scripts) into `embedded-core` so platforms do not duplicate them. Record that as a backlog item before starting.

## Per-platform notes

| Platform | Specifics to cover |
|---|---|
| nRF | Zephyr and the vendor SDK, devicetree overlays, Bluetooth stack configuration, radio coexistence, low-power states, secure boot and partitions |
| ESP32 | ESP-IDF components and menuconfig, FreeRTOS on dual cores, partition tables, OTA and rollback, Wi-Fi and Bluetooth, power management, flash encryption and secure boot |
| RP2040 | Pico SDK and CMake, PIO programs, dual core, clock and PLL, USB, flash execution in place and its limits |
| RISC-V | Core and vendor differences, trap and CSR decoding instead of Cortex-M fault registers, toolchain and linker details |
| AVR and PIC | Register-level access, interrupt and memory model, fuses and configuration bits, limited RAM |

## Effort and sequencing

Rough effort for one platform at the depth of the current `stm32` plugin: about the same as the STM32 build, reduced by reuse of the templates, scripts, and testing material, and increased by any platform that needs different fault decoding or toolchains. Plan each platform as: scaffold from the template, orchestrator and design first, then debug and peripherals, then the rest, with a verification pass before release.
