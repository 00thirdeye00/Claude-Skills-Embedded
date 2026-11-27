# stm32 plugin

Skills for developing STM32 firmware with Claude: planning, design, architecture, code review, debugging, driver bring-up, low power, bootloaders and OTA, security, testing, release checks, peripheral configuration, and RTOS integration, across STM32 families.

Companion plugin: `embedded-core` (platform-independent checklists, theory, and an orchestrator for other MCUs). Everything here works without it.

## Workflows and references

All skills are started by you with a command; none loads on its own (in Claude Code), so they add no tokens until you call them.

- **Workflow**: a fixed procedure that ends in a deliverable (plan, brief, documents, report, checklist).
- **Reference**: lookup knowledge for one topic. You name the topic and your settings or symptom; Claude loads one reference file.

### Workflows

| Command | Use it when |
|---|---|
| `/stm32:stm32-orchestrator` | You have a multi-stage goal: it plans, waits for approval, runs the stage skills, and logs missing skills to a backlog |
| `/stm32:stm32-pin-map` | You have a KiCad netlist and want a compact MCU pin table (script) |
| `/stm32:stm32-design` | Starting a design or a board: part, clocks, pins, DMA, memory, interrupts, module breakdown, budgets |
| `/stm32:stm32-architecture` | Right after design approval: module contracts, resource map, CLAUDE.md pointer; also updates them after changes |
| `/stm32:stm32-extend` | Adding or changing a feature in firmware that has architecture documents, reading only what is needed |
| `/stm32:stm32-cubemx-config` | You need CubeMX settings from the design, or an `.ioc` reviewed |
| `/stm32:stm32-linker-startup` | Linker script, startup code, map file and stack analysis (scripts) |
| `/stm32:stm32-driver-bringup` | You must write a driver for a chip from its datasheet |
| `/stm32:stm32-testing` | You need a test strategy, host tests, or CI |
| `/stm32:stm32-debug` | A HardFault, a hang, a reset loop, a silent peripheral, or a debug-versus-standalone difference (fault decoder script) |
| `/stm32:stm32-power` | Battery life matters or sleep modes misbehave |
| `/stm32:stm32-bootloader-ota` | You need a bootloader, DFU, A/B slots with rollback, or MCUboot |
| `/stm32:stm32-security` | You need a threat model, debug and read-out policy, secure boot, or TrustZone planning |
| `/stm32:stm32-review` | You want STM32-specific review: HAL/LL use, clocks, DMA and cache, priorities, flash, option bytes, module boundaries |
| `/stm32:stm32-release` | You are preparing a release or production programming and need to set protection |

### References

| Command | Covers |
|---|---|
| `/stm32:stm32-peripherals` | GPIO/EXTI, UART, I2C, SPI, CAN/FDCAN, USB, ADC/DAC, timers/PWM, DMA, QSPI/FMC, Ethernet, SD card, audio, displays, RTC, watchdogs, CRC/RNG, OPAMP/COMP (one reference loaded per use) |
| `/stm32:stm32-rtos` | FreeRTOS, Zephyr, ThreadX, RT-Thread (one reference loaded per use) |

## How to run them

Type the command and your details in one message:

```
/stm32:stm32-debug CFSR=0x00000200 BFAR=0x40021000 stacked PC=0x08001A44
/stm32:stm32-peripherals SPI DMA to a display at 20 MHz on an STM32H7
```

For a multi-stage goal use `/stm32:stm32-orchestrator`. For several separate tasks, send one command per message in order. Claude cannot start these skills for you. For a full walk-through on a custom KiCad board see `docs/custom-board-guide.md` in the repository root.

## Helper scripts

Python 3, no extra packages. Tested only on synthetic fixtures so far; try them on your own files.

| Script | Skill |
|---|---|
| `decode_fault.py` | `stm32-debug` |
| `netlist_pins.py` | `stm32-pin-map` |
| `map_summary.py`, `stack_usage.py` | `stm32-linker-startup` |
| `check_architecture.py` | `stm32-architecture` |

## When to use it, when to skip it

Skip it for quick questions and small boilerplate; plain Claude is cheaper. Use it when you want the fixed procedure and verified checklists: fault decoding, DMA and cache review, boot and update design, architecture documents, release checks. Use the `embedded-core` equivalents only for non-STM32 targets.

## Token cost

Nothing is loaded until you call a command. A command costs the skill body (about 300 to 1,300 tokens) plus one reference file (about 500 to 2,700 tokens). Figures are estimates.

## Accuracy

Arm architecture facts are stated plainly. Family-level facts (register names, bit positions, errata, option-byte encodings, mode names) vary by part and silicon revision, so the skills flag them for verification against the reference manual, datasheet, and errata sheet. Treat generated code and numbers as drafts to verify on hardware.

## Connectors

Optional. See `CONNECTORS.md`. Skills use `~~source control`, `~~project tracker`, and `~~knowledge base` placeholders and work without any connector.

## License

MIT. See `LICENSE`.
