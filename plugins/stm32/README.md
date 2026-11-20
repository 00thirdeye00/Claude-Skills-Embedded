# stm32 plugin

Skills for developing STM32 firmware with Claude: design, code review, debugging, driver bring-up, low power, bootloaders and OTA updates, release checks, peripheral configuration, and FreeRTOS and Zephyr integration, across STM32 families.

Companion plugin: `embedded-core` (platform-independent checklists and theory). Everything here works without it.

## Workflows and references

All skills are started by you with a command; none loads on its own (in Claude Code), so they add no tokens until you call them.

- **Workflow**: a fixed procedure that ends in a deliverable (brief, report, checklist). You give inputs; Claude follows the steps.
- **Reference**: lookup knowledge for one topic. You name the topic and your settings or symptom; Claude loads one reference file and answers.

### Workflows

| Command | Use it when |
|---|---|
| `/stm32:stm32-design` | Starting a design or a board: part choice, clock tree, pins, DMA, memory, interrupt priorities, budgets |
| `/stm32:stm32-debug` | A HardFault, a hang, a reset loop, a silent peripheral, or a debug-versus-standalone difference |
| `/stm32:stm32-driver-bringup` | You must write a driver for a chip from its datasheet |
| `/stm32:stm32-review` | You want STM32-specific review of code: HAL/LL use, clocks, DMA and cache, priorities, flash and option bytes |
| `/stm32:stm32-power` | Battery life matters or sleep modes misbehave |
| `/stm32:stm32-bootloader-ota` | You need a bootloader, DFU, A/B slots with rollback, or MCUboot |
| `/stm32:stm32-release` | You are preparing a release or production programming and need to set protection |

### References

| Command | Covers |
|---|---|
| `/stm32:stm32-peripherals` | GPIO/EXTI, UART, I2C, SPI, CAN/FDCAN, USB, ADC/DAC, timers/PWM, DMA, QSPI/FMC (one reference loaded per use) |
| `/stm32:stm32-rtos` | FreeRTOS (config, priorities, HAL timebase, patterns) and Zephyr (west, overlays, Kconfig) |

## How to run them

Type the command and your details in one message:

```
/stm32:stm32-debug CFSR=0x00000200 BFAR=0x40021000 stacked PC=0x08001A44
/stm32:stm32-peripherals SPI DMA to a display at 20 MHz on an STM32H7
```

For several tasks, send one command per message in order, for example `stm32-design`, then `stm32-driver-bringup` for each chip, then `stm32-review`, then `stm32-release`. Claude cannot start these skills for you. For a full walk-through on a custom KiCad board, see `docs/custom-board-guide.md` in the repository root.

## When to use it, when to skip it

Skip it for quick questions and small boilerplate; plain Claude is cheaper. Use it when you want the fixed procedure and verified checklists: fault decoding, DMA and cache review, boot and update design, release checks. Use the `embedded-core` equivalents only for non-STM32 targets.

## Token cost

Nothing is loaded until you call a command. A command costs the skill body (about 400 to 1,300 tokens) plus one reference file (about 700 to 2,700 tokens). Figures are estimates.

## Accuracy

Arm architecture facts are stated plainly. Family-level facts (register names, bit positions, errata, option-byte encodings, mode names) vary by part and silicon revision, so the skills flag them for verification against the reference manual, datasheet, and errata sheet. Treat generated code and numbers as drafts to verify on hardware.

## Connectors

Optional. See `CONNECTORS.md`. Skills use `~~source control`, `~~project tracker`, and `~~knowledge base` placeholders and work without any connector.

## License

MIT. See `LICENSE`.
