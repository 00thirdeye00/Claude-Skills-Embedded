# Writing firmware for a custom KiCad board with the stm32 plugin

A step-by-step guide for a board you designed in KiCad and now need firmware for. Every command below is typed by you; nothing loads on its own. Commands are `/stm32:...` and `/embedded-core:...` (see the main README for installation).

Claude drafts, checks, and explains. You still verify on hardware: measure the rails, confirm pin functions in the datasheet, and test every driver.

## Contents
- Before you start
- Step 1: Give Claude the board
- Step 2: Turn the schematic into a firmware pin plan
- Step 3: Hardware sanity check before flashing
- Step 4: Create the project
- Step 5: First light
- Step 6: Bring up peripherals and chips one at a time
- Step 7: Application structure
- Step 8: Power, boot, and updates
- Step 9: Review and release
- Keeping token use low

## Before you start

Collect:
- The exact MCU part number (for example the full ordering code, not just the family).
- The KiCad project (schematic at least).
- Datasheets or reference-manual extracts for the MCU and for each external chip.
- What the product must do: interfaces, rates, power source, update method.
- Your toolchain choice: STM32CubeIDE or CMake with the Arm GNU Toolchain, or Zephyr; and the debug probe.

## Step 1: Give Claude the board

Pick one way. Prefer the smallest input that answers the question.

**A. Exports (works everywhere).** Export compact files from the KiCad schematic. With KiCad 8 or later, `kicad-cli` can do it (check `kicad-cli sch export --help` for your version):

```
kicad-cli sch export netlist --output board.net board.kicad_sch
kicad-cli sch export bom     --output bom.csv   board.kicad_sch
kicad-cli sch export pdf     --output board.pdf board.kicad_sch
```

Upload the netlist, BOM, and PDF to the chat. A raw `.kicad_sch` file is large and costs many tokens; exports are smaller. For a big board, upload only the MCU's sheet or the nets that touch the MCU.

**B. BoardRepo connector (if you use it).** If the board is on BoardRepo and the BoardRepo connector is enabled in your Claude app, Claude can read schematic connectivity ("what connects to U1"), the BOM, and KiCad's own checks without you pasting anything. This is also cheaper for large boards because Claude asks only for the parts it needs.

**C. GitHub connector.** If the KiCad project is in a GitHub repository you have connected, Claude can read specific files from it. Prefer exports over raw schematics for token cost.

## Step 2: Turn the schematic into a firmware pin plan

```
/stm32:stm32-design The board is built: STM32G474RE, 8 MHz HSE, 32.768 kHz LSE.
Netlist and BOM are attached. Needs: 2x CAN FD, USB CDC, 3x I2C sensors, FreeRTOS.
1) List every MCU pin with its net and what it connects to.
2) Check each alternate function against the datasheet and flag conflicts.
3) Plan clocks, DMA, memory, and interrupt priorities.
```

You get a design brief with pin and alternate-function tables, a clock plan, DMA assignments, and risks. Check every alternate-function number against the datasheet yourself; Claude marks the ones it could not verify.

## Step 3: Hardware sanity check before flashing

In plain chat, ask: "From this schematic, write a first power-on checklist: rails and expected voltages, boot pin states, reset circuit, debug header pinout, oscillators, and anything that could damage the MCU." Then measure the rails, look for shorts, and confirm the debug header pinout matches your probe before connecting power. If the board has a problem, fix the hardware first: firmware cannot compensate for a wrong boot pin or a missing decoupling capacitor.

## Step 4: Create the project

Ask Claude for the settings to enter into your generator, or for a Zephyr board overlay:

```
/stm32:stm32-rtos Create the FreeRTOS setup for this pin plan on STM32G474RE:
HAL timebase on a spare timer, interrupt priority table, heap choice, task list.
```

Generate the project in your own tools (CubeMX or CMake or west), and paste back any build errors.

## Step 5: First light

Get the smallest working program first: LED blink, then a UART log message. Use one peripheral command:

```
/stm32:stm32-peripherals UART2 for the debug console, 115200 baud on this clock tree, DMA transmit.
```

If it does not start, or you land in a fault handler:

```
/stm32:stm32-debug HardFault at boot. CFSR=0x... HFSR=0x... stacked PC=0x... LR=0x...
```

## Step 6: Bring up peripherals and chips one at a time

Order that avoids chasing several problems at once: clocks, GPIO, UART log, buses (I2C, SPI), DMA, then CAN and USB. For each external chip:

```
/stm32:stm32-driver-bringup BMI270 IMU on I2C1, datasheet excerpt attached.
```

For bus-level questions (pull-ups, bit timing) use `/embedded-core:embedded-protocols`. For a peripheral that misbehaves use `/stm32:stm32-peripherals` with the symptom and a logic analyzer capture.

## Step 7: Application structure

```
/embedded-core:embedded-rtos-concepts Tasks: IMU 1 kHz, CAN 500 kbit/s, USB log, UI 50 Hz. Check priorities, stacks, and deadlines.
/embedded-core:embedded-isr-concurrency Review how my DMA callback hands data to the CAN task.
```

## Step 8: Power, boot, and updates

Use these only if the product needs them:

```
/stm32:stm32-power Battery 2000 mAh, wake every 10 s, sensors on I2C, target 1 year.
/stm32:stm32-bootloader-ota A/B slots with rollback over USB DFU on this part.
```

## Step 9: Review and release

```
/stm32:stm32-review <paste the diff or files>
/stm32:stm32-release Option bytes, read-out protection policy, production programming for 50 units.
```

Use `/embedded-core:embedded-review` and `/embedded-core:embedded-release` only for generic items you want beyond the STM32 ones; avoid running both on the same change.

## Keeping token use low

- Give the exact part number and raw values the first time, so Claude does not need a question round.
- One command per message, and the most specific command for the task.
- Send exports or the MCU's nets, not the whole board.
- Keep a short notes file in your repo (pin plan, clock plan, decisions) and paste that into later conversations instead of the history.
- Start a new conversation for each step when the earlier ones are long.
