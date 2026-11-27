# Claude Skills for Embedded Systems

Claude plugins that add embedded firmware engineering skills: planning, design, architecture, code review, debugging, driver bring-up, low power, bootloaders and OTA, security, testing, release checks, peripheral configuration, and RTOS integration. The first platform is **STM32**; the same layout is meant to grow to other platforms (nRF, ESP32, RP2040, RISC-V, and more).

## Read this first: workflows and references

Everything here is a Claude *skill* (a folder with a `SKILL.md` and supporting files). The skills come in two kinds, and **you start every one of them yourself by typing its command**. Nothing loads automatically in Claude Code, so installing the plugins adds no tokens to your conversations until you call a command. This is a Claude Code setting (`disable-model-invocation`); other Claude apps may behave differently, so check how your app lists these skills.

| Kind | What it is | You give it | You get back | Count |
|---|---|---|---|---|
| **Workflow** | A fixed procedure for one engineering task | The inputs (code, dump, requirements) | A deliverable: plan, design brief, architecture documents, review report, debug report, checklist | 21 |
| **Reference** | Lookup knowledge for one topic at a time | A topic and your settings or symptom | Configuration, calculations, and failure checks from one reference file | 3 |

- **Plan and structure:** `stm32-orchestrator` and `embedded-core`'s `embedded-orchestrator` (plan a whole goal, then run the skills), `stm32-pin-map` (KiCad netlist to pin table), `stm32-design`, `stm32-architecture`, `stm32-extend`.
- **Build:** `stm32-cubemx-config`, `stm32-linker-startup`, `stm32-driver-bringup`, `stm32-power`, `stm32-bootloader-ota`, `stm32-security`, plus `embedded-rtos-concepts` and `embedded-isr-concurrency`.
- **Verify and ship:** `stm32-testing`, `stm32-review`, `stm32-debug`, `stm32-release`, plus `embedded-review`, `embedded-debug`, `embedded-release`.
- **References:** `stm32-peripherals` (GPIO/EXTI, UART, I2C, SPI, CAN, USB, ADC/DAC, timers/PWM, DMA, QSPI/FMC, Ethernet, SD card, audio, displays, RTC, watchdogs, CRC/RNG, OPAMP/COMP), `stm32-rtos` (FreeRTOS, Zephyr, ThreadX, RT-Thread), and `embedded-protocols` (I2C, SPI, UART, CAN, USB theory).

## What this does

With these plugins installed, you can ask Claude to turn a KiCad netlist into a pin table, plan the clock tree and pins for a board, write architecture documents so later changes read only what they need, decode a HardFault, review a DMA setup, size I2C pull-ups, design an update path with rollback, or set up FreeRTOS interrupt priorities. Claude follows a structured procedure, uses checklists written for embedded work, and flags the facts you must verify against your part's reference manual and errata sheet.

## Plugins

| Plugin | Contents |
|---|---|
| [`stm32`](plugins/stm32) | 17 skills: 15 workflows (orchestrator, architecture, extend, design, pin map, CubeMX config, linker and startup, testing, security, driver bring-up, power, bootloader and OTA, review, debug, release) and 2 references (`stm32-peripherals`, `stm32-rtos`) |
| [`embedded-core`](plugins/embedded-core) | 7 platform-independent skills: 6 workflows (orchestrator, ISR and concurrency, RTOS concepts, review, debug, release) and 1 reference (`embedded-protocols`) |

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

**One task: one command.** **Several tasks: one command per message, in order.** Claude cannot start these skills for you, so each step is something you type. I have not tested whether two commands in one message both run, so use separate messages.

### Big goals: use an orchestrator

For a multi-stage goal such as "design and develop firmware for this board", start with one command and let the orchestrator plan and run the stages:

```
/stm32:stm32-orchestrator Design and develop firmware for my board (STM32G474RE, netlist and BOM attached):
FreeRTOS, 2x CAN FD, USB CDC, 3x I2C sensors, battery powered.
```

For other MCUs use `/embedded-core:embedded-orchestrator`.

1. **Plan first.** It reads a catalog of the available skills, picks a playbook, and returns a staged plan: which skill runs at each stage, what it needs, what it produces, where you must verify something on hardware, a token estimate, and any gaps. It does nothing else until you answer.
2. **You choose:** approve and self-run, hand-off commands only (it gives you the commands to paste one per message), or edit the plan.
3. **Self-run.** After approval it runs the stages in order by reading each skill's file and following it, keeps decisions in `firmware-plan.md`, and pauses where you must act (measurements, irreversible choices).
4. **Gaps go to a backlog.** If a skill is missing or insufficient, it tells you, continues only where that is safe (labeled "not skill-backed, verify"), and adds a row to `skills-backlog.md`. The repository's own backlog is [docs/skills-backlog.md](docs/skills-backlog.md).

For a new board the plan includes an architecture stage right after design approval, so later changes read the architecture documents instead of the code base. The orchestrators are manual like the rest, and they cost extra tokens (catalog, plan, notes), so use them for multi-stage goals and a single command for a single task. Self-run works by reading sibling skill files by path; I have not tested that across Claude apps, and hand-off mode is the fallback.

### Which command for which task

| I want to... | Command |
|---|---|
| Plan and run a whole goal | `/stm32:stm32-orchestrator` (STM32) or `/embedded-core:embedded-orchestrator` (other MCUs) |
| Get an MCU pin table from a KiCad netlist | `/stm32:stm32-pin-map` |
| Choose an MCU, plan clocks, pins, DMA, memory, interrupts | `/stm32:stm32-design` |
| Create architecture documents from an approved design, or update them | `/stm32:stm32-architecture` |
| Add or change a feature without reading the whole code base | `/stm32:stm32-extend` |
| Get CubeMX settings from the design, or review an `.ioc` | `/stm32:stm32-cubemx-config` |
| Write or review a linker script and startup code, read a map file | `/stm32:stm32-linker-startup` |
| Configure or fix one peripheral (GPIO to OPAMP) | `/stm32:stm32-peripherals` |
| Set up FreeRTOS, Zephyr, ThreadX, or RT-Thread | `/stm32:stm32-rtos` |
| Write a driver for a sensor or chip from its datasheet | `/stm32:stm32-driver-bringup` |
| Plan tests and CI | `/stm32:stm32-testing` |
| Decode a HardFault, or find why firmware hangs or resets | `/stm32:stm32-debug` |
| Reduce power or fix sleep-mode problems | `/stm32:stm32-power` |
| Plan or debug a bootloader or firmware update | `/stm32:stm32-bootloader-ota` |
| Plan device security, debug policy, secure boot | `/stm32:stm32-security` |
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

A typical single command costs the skill body (about 400 to 1,300 tokens) plus one reference file (about 700 to 2,700 tokens). These are estimates.

## Step-by-step: firmware for a custom KiCad board

Short version. The full guide, with example prompts for each step, is in [docs/custom-board-guide.md](docs/custom-board-guide.md). Prefer one command? `/stm32:stm32-orchestrator` can plan and run these stages for you (see "Big goals" above). Otherwise:

1. **Give Claude the board**: export a netlist, BOM, and PDF from KiCad, or use a connector (BoardRepo or GitHub) if you have one.
2. **Pin table**: `/stm32:stm32-pin-map` turns the netlist into a compact MCU pin table.
3. **Design**: `/stm32:stm32-design` turns the pin table into a verified pin, clock, DMA, memory, and interrupt plan with a module breakdown.
4. **Architecture baseline**: `/stm32:stm32-architecture` turns the approved design into module contracts and a resource map before any code is written.
5. **Hardware check**: ask in plain chat for a first power-on checklist; measure before flashing.
6. **Create the project**: `/stm32:stm32-cubemx-config`, `/stm32:stm32-rtos`, and `/stm32:stm32-linker-startup`.
7. **First light**: LED and a UART log with `/stm32:stm32-peripherals`; faults go to `/stm32:stm32-debug`.
8. **Bring up chips one at a time**: `/stm32:stm32-driver-bringup` per external device, then `/stm32:stm32-architecture` update.
9. **Application structure and tests**: `/embedded-core:embedded-rtos-concepts`, `/embedded-core:embedded-isr-concurrency`, `/stm32:stm32-testing`.
10. **Power, boot, updates, security** (if needed): `/stm32:stm32-power`, `/stm32:stm32-bootloader-ota`, `/stm32:stm32-security`.
11. **Review and release**: `/stm32:stm32-review`, then `/stm32:stm32-release`.
12. **Later changes**: `/stm32:stm32-extend`.

## Modular design: keeping extensions cheap

Extending firmware is expensive when Claude has to read the whole code base. `/stm32:stm32-architecture` creates a small, layered set of documents right after you approve the design:

- `docs/architecture/ARCHITECTURE.md`: layers and rules, the module list with dependencies, a **resource map** (pins, DMA, interrupts and priorities, timers, buses, clocks, memory, RTOS tasks, init order), decisions, and open items.
- `docs/architecture/modules/<name>.md`: one short contract per module (public API, dependencies, owned resources, concurrency, tests).
- A pointer section for the firmware repository's `CLAUDE.md` that tells Claude to read the index first, then only the target module's contract and the headers it depends on, and not to scan `src/`.

The resource map is what makes this safe: conflicts on shared pins, DMA channels, interrupt priorities, and buses show up there, not in `#include` lines. `/stm32:stm32-extend` does an extension by reading the index, the affected contracts, and dependency headers, then updates the documents. `/stm32:stm32-design`, `/stm32:stm32-driver-bringup`, `/stm32:stm32-rtos`, and `/stm32:stm32-review` work in the same module layout, and `check_architecture.py` flags drift between the documents and the code.

Use the full layered set for larger projects; a small project can use one file. Creating the documents costs tokens once. A stale document is worse than none, so update it with every change. These skills have not been run on a real project yet (backlog B-020).

## Helper scripts and tests

| Script | Skill | Does |
|---|---|---|
| `decode_fault.py` | `stm32-debug` | Decodes CFSR, HFSR, and fault addresses; prints the `addr2line` command |
| `netlist_pins.py` | `stm32-pin-map` | KiCad netlist to MCU pin table (markdown or CSV) |
| `map_summary.py` | `stm32-linker-startup` | Region usage and largest contributors from a GNU ld map |
| `stack_usage.py` | `stm32-linker-startup` | Largest stack frames from `-fstack-usage` output |
| `check_architecture.py` | `stm32-architecture` | Checks the architecture documents and, optionally, the code for drift |

They need Python 3 and no extra packages. Run the tests with `python3 -m unittest discover -s tests -v`. The tests use small synthetic fixtures written to match the documented formats, not output captured from real tools, so try the scripts on your own files too (backlog B-019).

## Skills backlog and plans

Missing and unverified work is tracked in [docs/skills-backlog.md](docs/skills-backlog.md). Plans for what cannot be done from a chat: [docs/verification-plan.md](docs/verification-plan.md) (audit the facts against the manuals, install and trigger tests) and [docs/platform-expansion-plan.md](docs/platform-expansion-plan.md) (nRF, ESP32, RP2040, RISC-V, AVR/PIC).

## Repository layout

```
.claude-plugin/marketplace.json     marketplace catalog (name: embedded-skills)
plugins/
  stm32/
    .claude-plugin/plugin.json
    skills/<skill>/SKILL.md         short instructions, manual-only
    skills/<skill>/references/      detail loaded on demand
    skills/<skill>/scripts/         helper scripts (some skills)
    README.md, CONNECTORS.md, LICENSE
  embedded-core/                    same structure
docs/                               guides, backlog, and plans
tests/                              script tests and fixtures
```

## Accuracy and limits

- Arm architecture facts are stated plainly; family-level details (register names, bit positions, errata, option-byte encodings, mode names) vary by part and silicon revision, and the skills mark them for verification.
- The skills guide Claude; they do not replace the reference manual, datasheet, errata sheet, or testing on hardware.
- Vendor tool and library names are examples. Versions of HAL, Zephyr, and FreeRTOS change APIs; check the version you use.

## Roadmap

- Verify the facts and the install and trigger behavior (see the plans above).
- Platform plugins following the `stm32` layout: `nrf`, `esp32`, `rp2040`, `riscv`, `avr-pic`.
- Deeper per-family references and a reviewer subagent.

## Contributing

Issues and pull requests are welcome. For a new skill: keep `SKILL.md` short with a trigger-rich `description`, put detail in `references/`, flag family-specific facts for verification, and write original content. Run `claude plugin validate .` before submitting.

## Credits

The structure was informed by public Claude skill and subagent collections for embedded work (VoltAgent/awesome-claude-code-subagents and Jeffallan/claude-skills). No text was copied from them.

## License

MIT. See [LICENSE](LICENSE).
