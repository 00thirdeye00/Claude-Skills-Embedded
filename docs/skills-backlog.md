# Skills backlog

Missing or insufficient skills. The orchestrators (`/stm32:stm32-orchestrator`, `/embedded-core:embedded-orchestrator`) append rows when they hit a gap; maintainers triage them.

Priority: H, M, L. Status: `open`, `planned` (has a written plan), `partial`, `built, unverified` (written but not checked against real manuals, real tool output, or real hardware), `done`.

| ID | Date | Type | Skill | Gap | Exposed by | Proposed scope | Priority | Status |
|---|---|---|---|---|---|---|---|---|
| B-001 | 2026-11-22 | new | `stm32-cubemx-config` | No guidance for producing CubeMX settings from a design | Initial build | Ordered settings checklist, `.ioc` review | H | built, unverified (menu names vary by CubeMX version) |
| B-002 | 2026-11-22 | new | `stm32-pin-map` | No way to extract an MCU pin table from a KiCad netlist | Custom-board guide | Netlist to pin table (script plus skill) | H | built, unverified (tested on synthetic netlists only) |
| B-003 | 2026-11-22 | update | all `stm32-*` references | Family-level facts written from general knowledge; no audit against manuals | Initial build | Per-family audit with sources; see `docs/verification-plan.md` | H | planned |
| B-004 | 2026-11-22 | update | plugins | Trigger, install, and orchestrator self-run untested in Claude apps | Initial build | Test matrix in `docs/verification-plan.md` | H | planned |
| B-005 | 2026-11-22 | new | `stm32-testing` | No test strategy, host tests, HIL, or CI | Initial build | Test layers, fake port, CI example | M | built, unverified |
| B-006 | 2026-11-22 | new | `stm32-linker-startup` | No linker script, startup, map or stack analysis help | Initial build | Linker and startup reference, map and stack scripts | M | built, unverified (scripts tested on synthetic files) |
| B-007 | 2026-11-22 | update | `stm32-peripherals` | Missing Ethernet, SDMMC, I2S/SAI, LTDC, RTC, watchdogs, CRC/RNG, OPAMP/COMP | Initial build | One reference each | M | built, unverified |
| B-008 | 2026-11-22 | new | scripts | No fault decoder or map and stack analysis scripts | Initial build | `decode_fault.py`, `map_summary.py`, `stack_usage.py` | M | built, unverified (tested on synthetic inputs) |
| B-009 | 2026-11-22 | update | `stm32-bootloader-ota` | No verified MCUboot configuration for non-uniform sector parts | Initial build | Verified slot layouts on representative parts | M | partial (worked example added, not a verified configuration) |
| B-010 | 2026-11-22 | new | `embedded-orchestrator` | No orchestrator for non-STM32 targets | Orchestrator build | Generic planner routing to platform plugins | M | built, unverified |
| B-011 | 2026-11-22 | new | `stm32-security` | No TrustZone, secure boot, or crypto skill | Initial build | Threat model, controls, lifecycle | L | built, unverified (concepts only; verify per family) |
| B-012 | 2026-11-22 | new | platform plugins | No nRF, ESP32, RP2040, RISC-V, or AVR/PIC plugins | Roadmap | Same layout as `stm32`; see `docs/platform-expansion-plan.md` | L | planned |
| B-013 | 2026-11-22 | new | `stm32-rtos` | No ThreadX or RT-Thread reference | Initial build | One reference each | L | built, unverified |
| B-014 | 2026-11-23 | new | `stm32-extend` | No skill to extend firmware from the architecture documents | Architecture design | Impact analysis, minimal reads, doc update | H | built, unverified |
| B-015 | 2026-11-23 | update | `stm32-design` | No module breakdown or resource map in the output | Architecture design | Add both | H | built, unverified |
| B-016 | 2026-11-23 | update | `stm32-driver-bringup`, `stm32-rtos` | Code not generated in the module layout | Architecture design | Module layout and contract file | M | built, unverified |
| B-017 | 2026-11-23 | update | `stm32-review` | No module boundary or doc-sync checks | Architecture design | Add checks | M | built, unverified |
| B-018 | 2026-11-23 | new | `check_architecture.py` | No check that the architecture documents match the code | Architecture design | Consistency, dependency, and priority drift checks | M | built, unverified (tested on a synthetic sample project) |
| B-019 | 2026-11-24 | update | scripts and skills | Scripts tested only on synthetic fixtures | Script build | Run on real KiCad netlists, real map and `.su` files, real projects; fix parsers | H | open |
| B-020 | 2026-11-24 | update | `stm32-architecture`, `stm32-extend` | Never run on a real project | Architecture build | Trial on a real firmware project; tune templates and size rules | H | open |
| B-021 | 2026-11-24 | new | `.ioc` checker script | No script comparing a CubeMX `.ioc` with the design | CubeMX skill | Parse `.ioc`, compare pins, clocks, priorities, DMA | M | open |
| B-022 | 2026-11-24 | update | `embedded-core` | Platform-neutral material (architecture templates, modularity rules, testing, scripts) lives in `stm32` | Expansion plan | Move shared parts into `embedded-core` before a second platform | M | open |
| B-023 | 2026-11-24 | update | `stm32-peripherals` | Still missing: USB host and OTG detail, CORDIC and FMAC, DSI and camera, touch sensing, low-power UART variants | Peripheral build | One reference each as needed | L | open |
| B-024 | 2026-11-24 | new | `embedded-core` skills | No generic architecture, testing, linker, or security skills | Orchestrator catalog | Generic versions for non-STM32 targets | L | open |
