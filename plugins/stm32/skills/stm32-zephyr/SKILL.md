---
name: stm32-zephyr
description: Develop for STM32 with the Zephyr RTOS: board selection, west build and flash workflow, devicetree overlays for pins and peripherals, pin control, Kconfig options, using GPIO, UART, I2C, SPI, and CAN drivers through the Zephyr device API, clock configuration in devicetree, power management, MCUboot with sysbuild, and debugging. Use when starting a Zephyr project on an STM32 board, enabling a peripheral, writing an overlay, fixing a build or devicetree error, or porting a bare-metal STM32 design to Zephyr. Trigger with "Zephyr on STM32", "devicetree overlay", "west build nucleo", "Zephyr pinctrl", "Kconfig prj.conf", "enable I2C in Zephyr", "Zephyr MCUboot STM32", "custom STM32 board Zephyr".
argument-hint: "<board or part, peripheral to enable, Zephyr version, or the build error>"
---

# /stm32:stm32-zephyr

Create, configure, build, and debug Zephyr applications on STM32 targets.

## Usage

```
/stm32:stm32-zephyr $ARGUMENTS
```

If details are missing, ask for the board or SoC, the Zephyr version, the peripherals and pins needed, and the exact error output.

## Workflow

1. **Confirm the environment**: Zephyr version, SDK or toolchain, and that the board name exists in that version (`west boards`).
2. **Start from the nearest board and sample.** Build a known sample first (blinky or a console sample) to prove the toolchain and flashing.
3. **Describe hardware in devicetree**: enable nodes, set pin control, clock settings, and aliases in an overlay file, not by editing the board files.
4. **Select software in Kconfig** through the project configuration file; check the resulting configuration.
5. **Use the device API** for GPIO, UART, I2C, SPI, CAN, and others, always checking that devices are ready.
6. **Debug** with the logging subsystem, fatal-error output, and the debugger through west.
7. **Add a bootloader** with MCUboot and sysbuild when updates are required.

Details, snippets, and common errors are in `references/zephyr-stm32.md`.

## Output

```markdown
## Zephyr Setup: [board / application]

### Environment
- Zephyr: [version], toolchain: [..], board: [..]

### Devicetree overlay
[overlay]

### Kconfig
[prj.conf entries]

### Code
[snippets]

### Build and flash
[commands]

### Checks
- [what to verify; what to confirm in the docs for this Zephyr version]
```

## Rules

- Zephyr's build system, board names, and options change between releases; verify against the documentation for the version in use.
- Do not edit upstream board or SoC files; use overlays and configuration fragments in the application.
- Take pin and alternate-function data from the pin control definitions for the SoC and the datasheet.
- Check `device_is_ready()` before using a device.

## Tips

1. **Read the devicetree output** (`build/zephyr/zephyr.dts`) to see the final merged tree.
2. **Kconfig warnings** about unmet dependencies are errors in disguise; read them.
3. **A peripheral that does nothing** is usually a node with `status = "okay"` missing, pins not set, or the driver option not enabled.
