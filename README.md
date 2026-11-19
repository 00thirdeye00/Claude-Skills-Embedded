# Claude Skills for Embedded Systems

Claude plugins that add embedded firmware engineering skills: debugging, design, code review, driver bring-up, low power, bootloaders and OTA, release checks, peripheral configuration, and RTOS integration. The first platform is **STM32**; the same layout is meant to grow to other platforms (nRF, ESP32, RP2040, RISC-V, and more).

## What this does

With these plugins installed, Claude loads the right guidance when you work on firmware. Ask it to decode a HardFault, plan the clock tree and pins for a new board, review a DMA setup, size I2C pull-ups, design an update path with rollback, or set up FreeRTOS interrupt priorities, and it follows a structured workflow, uses checklists written for embedded work, and flags the facts you must verify against your part's reference manual and errata sheet.

Each skill is a short instruction file plus reference files that Claude reads only when needed, so context stays small.

## Plugins

| Plugin | Contents |
|---|---|
| [`stm32`](plugins/stm32) | 19 skills: 7 workflow skills (design, review, debug, driver bring-up, power, bootloader and OTA, release), 10 peripheral skills (GPIO/EXTI, UART, I2C, SPI, CAN, USB, ADC/DAC, timers/PWM, DMA, QSPI/FMC), and 2 RTOS skills (FreeRTOS, Zephyr) |
| [`embedded-core`](plugins/embedded-core) | 6 platform-independent skills: ISR and concurrency, RTOS concepts, bus protocols, review, debug, and release checklists |

Install `stm32` on its own, or add `embedded-core` for the shared theory. The STM32 skills work without it.

## Install

### Claude Code

Add this repository as a marketplace, then install the plugins:

```bash
claude plugin marketplace add 00thirdeye00/Claude-Skills-Embedded
claude plugin install stm32@embedded-skills
claude plugin install embedded-core@embedded-skills
```

Inside a Claude Code session, the same steps are:

```
/plugin marketplace add 00thirdeye00/Claude-Skills-Embedded
/plugin install stm32@embedded-skills
/plugin install embedded-core@embedded-skills
```

Check the result with `claude plugin list`. Update later with `claude plugin marketplace update embedded-skills`.

### Claude desktop app (Cowork)

1. Open the **Plugins** page and select **Add marketplace**.
2. Enter `00thirdeye00/Claude-Skills-Embedded` (or `https://github.com/00thirdeye00/Claude-Skills-Embedded`).
3. Install `stm32`, and optionally `embedded-core`, from the new marketplace tab.

To install without the marketplace, zip a plugin folder (for example `plugins/stm32`, with `.claude-plugin/plugin.json` at the top level of the zip) and use the upload option on the Plugins page.

### Claude.ai in a browser (single skills)

Plugins are not required for skills. To add one skill, zip its folder so the folder is at the top of the archive, then upload it in the Skills settings of your account:

```bash
cd plugins/stm32/skills
zip -r stm32-debug.zip stm32-debug
```

Menu names can differ between Claude app versions; check the current in-app help.

### Try it from a local clone

```bash
git clone https://github.com/00thirdeye00/Claude-Skills-Embedded
claude plugin validate ./Claude-Skills-Embedded
claude plugin marketplace add ./Claude-Skills-Embedded
claude plugin install stm32@embedded-skills
```

## Use

Skills trigger from your request, or you can call them by name as `/<plugin>:<skill>`:

```
/stm32:stm32-debug  CFSR=0x00000200 BFAR=0x40021000 stacked PC=0x08001A44
/stm32:stm32-design  USB CDC + 2x CAN + 3x I2C, battery powered, FreeRTOS
/stm32:stm32-bootloader-ota  A/B slots with rollback on a 512 KB part
/embedded-core:embedded-protocols  I2C pull-up for 400 kHz, 120 pF
```

Give Claude the exact part number, the HAL or LL version, the RTOS, and raw register values or captures; the answers depend on them.

## Repository layout

```
.claude-plugin/marketplace.json     marketplace catalog (name: embedded-skills)
plugins/
  stm32/
    .claude-plugin/plugin.json
    skills/<skill>/SKILL.md         short, trigger-rich instructions
    skills/<skill>/references/      detail loaded on demand
    README.md, CONNECTORS.md, LICENSE
  embedded-core/                    same structure
```

## Accuracy and limits

- Arm architecture facts are stated plainly; family-level details (register names, bit positions, errata, option-byte encodings, mode names) vary by part and silicon revision, and the skills mark them for verification.
- The skills guide Claude; they do not replace the reference manual, datasheet, errata sheet, or testing on hardware.
- Vendor tool and library names are examples. Versions of HAL, Zephyr, and FreeRTOS change APIs; check the version you use.

## Roadmap

- Platform plugins following the `stm32` layout: `nrf`, `esp32`, `rp2040`, `riscv`, `avr-pic`.
- Deeper STM32 references per family, helper scripts (fault decoder, map-file analysis), and a reviewer subagent.

## Contributing

Issues and pull requests are welcome. For a new skill: keep `SKILL.md` short with a trigger-rich `description`, put detail in `references/`, flag family-specific facts for verification, and write original content. Run `claude plugin validate .` before submitting.

## Credits

The structure was informed by public Claude skill and subagent collections for embedded work (VoltAgent/awesome-claude-code-subagents and Jeffallan/claude-skills). No text was copied from them.

## License

MIT. See [LICENSE](LICENSE).
