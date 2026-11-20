# Claude Skills for Embedded Systems

Claude plugins that add embedded firmware engineering skills: design, code review, debugging, driver bring-up, low power, bootloaders and OTA, release checks, peripheral configuration, and RTOS integration. The first platform is **STM32**; the same layout is meant to grow to other platforms (nRF, ESP32, RP2040, RISC-V, and more).

## Read this first: workflows and references

Everything here is a Claude *skill* (a folder with a `SKILL.md` and supporting files). The skills come in two kinds, and **you start every one of them yourself by typing its command**. Nothing loads automatically in Claude Code, so installing the plugins adds no tokens to your conversations until you call a command. This is a Claude Code setting (`disable-model-invocation`); other Claude apps may behave differently, so check how your app lists these skills.

| Kind | What it is | You give it | You get back | Count |
|---|---|---|---|---|
| **Workflow** | A fixed procedure for one engineering task | The inputs (code, dump, requirements) | A deliverable: design brief, review report, debug report, checklist | 12 |
| **Reference** | Lookup knowledge for one topic at a time | A topic and your settings or symptom | Configuration, calculations, and failure checks from one reference file | 3 |

- **Workflows:** `stm32-design`, `stm32-review`, `stm32-debug`, `stm32-driver-bringup`, `stm32-power`, `stm32-bootloader-ota`, `stm32-release`, and from `embedded-core`: `embedded-isr-concurrency`, `embedded-rtos-concepts`, `embedded-review`, `embedded-debug`, `embedded-release`.
- **References:** `stm32-peripherals` (GPIO/EXTI, UART, I2C, SPI, CAN, USB, ADC/DAC, timers/PWM, DMA, QSPI/FMC), `stm32-rtos` (FreeRTOS, Zephyr), and `embedded-protocols` (I2C, SPI, UART, CAN, USB theory).

## What this does

With these plugins installed, you can ask Claude to decode a HardFault, plan the clock tree and pins for a board, review a DMA setup, size I2C pull-ups, design an update path with rollback, or set up FreeRTOS interrupt priorities. Claude follows a structured procedure, uses checklists written for embedded work, and flags the facts you must verify against your part's reference manual and errata sheet.

## Plugins

| Plugin | Contents |
|---|---|
| [`stm32`](plugins/stm32) | 7 workflows (design, review, debug, driver bring-up, power, bootloader and OTA, release) and 2 references (`stm32-peripherals`, `stm32-rtos`) |
| [`embedded-core`](plugins/embedded-core) | 5 workflows (ISR and concurrency, RTOS concepts, review, debug, release) and 1 reference (`embedded-protocols`) |

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

## Running commands

Type the command, then your details, in one message. The skill name is prefixed by the plugin name:

```
/stm32:stm32-debug  CFSR=0x00000200 BFAR=0x40021000 stacked PC=0x08001A44
/stm32:stm32-peripherals  I2C at 400 kHz on an STM32G4, two sensors, DMA
/embedded-core:embedded-review  <paste the diff>
```

**One task: one command.** **Several tasks: one command per message, in order.** Claude cannot start these skills for you, so each step is something you type. I have not tested whether two commands in one message both run, so use separate messages. Example sequence for a new product: `stm32-design`, then `stm32-driver-bringup` for each external chip, then `stm32-review` on the code, then `stm32-release`.

| I want to... | Command |
|---|---|
| Choose an MCU, plan clocks, pins, DMA, memory, interrupts | `/stm32:stm32-design` |
| Configure or fix one peripheral (GPIO to QSPI) | `/stm32:stm32-peripherals` |
| Set up FreeRTOS or Zephyr on STM32 | `/stm32:stm32-rtos` |
| Write a driver for a sensor or chip from its datasheet | `/stm32:stm32-driver-bringup` |
| Decode a HardFault, or find why firmware hangs or resets | `/stm32:stm32-debug` |
| Reduce power or fix sleep-mode problems | `/stm32:stm32-power` |
| Plan or debug a bootloader or firmware update | `/stm32:stm32-bootloader-ota` |
| Review STM32 code | `/stm32:stm32-review` |
| Prepare a release or production programming | `/stm32:stm32-release` |
| Review, debug, or release non-STM32 firmware | `/embedded-core:embedded-review`, `/embedded-core:embedded-debug`, `/embedded-core:embedded-release` |
| Check an ISR or shared data | `/embedded-core:embedded-isr-concurrency` |
| Design tasks, priorities, stack sizes | `/embedded-core:embedded-rtos-concepts` |
| Size pull-ups, bit timing, framing for any bus | `/embedded-core:embedded-protocols` |

## When to use these plugins, and when to skip them

**Skip them** (plain Claude is cheaper and just as good) for quick factual or concept questions, small boilerplate such as a simple UART init, anything that is not firmware, and when you already know the answer.

**Use them** when the task benefits from a fixed procedure or verified checklists: decoding fault registers, reviewing DMA and cache handling, planning a boot and update path, a release check, or a design brief. A good result in one pass can save the extra turns a vague answer would cost.

**Which plugin:**
- Only STM32: install `stm32`. It works without `embedded-core`.
- Other MCUs, or generic checklists: install `embedded-core`.
- Both installed costs nothing extra in context, because nothing loads until you call it. The overlap is review, debug, and release: use the `stm32-` version for STM32 targets and the `embedded-core` version for everything else. Do not run both on the same change.

**Using fewer tokens for the same task:**
- Call the single most specific command, with the exact part number and raw data in the first message.
- Send compact inputs (exports, register values, the relevant excerpt), not whole files.
- Start a fresh conversation per stage and carry a short notes file instead of the history.

A typical command costs the skill body (about 400 to 1,300 tokens) plus one reference file (about 700 to 2,700 tokens). These are estimates.

## Step-by-step: firmware for a custom KiCad board

Short version. The full guide, with example prompts for each step, is in [docs/custom-board-guide.md](docs/custom-board-guide.md).

1. **Give Claude the board**: export a netlist, BOM, and PDF from KiCad, or use a connector (BoardRepo or GitHub) if you have one.
2. **Pin plan**: `/stm32:stm32-design` turns the netlist into a verified pin, clock, DMA, and interrupt plan.
3. **Hardware check**: ask in plain chat for a first power-on checklist; measure before flashing.
4. **Create the project**: `/stm32:stm32-rtos` for the RTOS setup; generate the project in CubeMX, CMake, or west.
5. **First light**: LED and a UART log with `/stm32:stm32-peripherals`; faults go to `/stm32:stm32-debug`.
6. **Bring up chips one at a time**: `/stm32:stm32-driver-bringup` per external device.
7. **Application structure**: `/embedded-core:embedded-rtos-concepts` and `/embedded-core:embedded-isr-concurrency`.
8. **Power, boot, updates** (if needed): `/stm32:stm32-power`, `/stm32:stm32-bootloader-ota`.
9. **Review and release**: `/stm32:stm32-review`, then `/stm32:stm32-release`.

## Repository layout

```
.claude-plugin/marketplace.json     marketplace catalog (name: embedded-skills)
docs/custom-board-guide.md          step-by-step guide for a custom KiCad board
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
- Trigger and install testing across Claude Code, the desktop app, and claude.ai.

## Contributing

Issues and pull requests are welcome. For a new skill: keep `SKILL.md` short with a trigger-rich `description`, put detail in `references/`, flag family-specific facts for verification, and write original content. Run `claude plugin validate .` before submitting.

## Credits

The structure was informed by public Claude skill and subagent collections for embedded work (VoltAgent/awesome-claude-code-subagents and Jeffallan/claude-skills). No text was copied from them.

## License

MIT. See [LICENSE](LICENSE).
