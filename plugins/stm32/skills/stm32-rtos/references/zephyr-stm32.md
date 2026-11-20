# Zephyr on STM32

Commands, board names, bindings, and options change between Zephyr releases. Treat the snippets as patterns and check them against the documentation and the board files of your version.

## Contents
- Workflow commands
- Application layout
- Devicetree overlays
- Clock configuration
- Kconfig
- Drivers through the device API
- Threads and synchronization
- Low power
- MCUboot
- Debugging
- Common errors

## Workflow commands

```
west init ~/zephyrproject            # first time: fetch Zephyr
cd ~/zephyrproject && west update    # fetch modules (includes the STM32 HAL module)
west boards | grep -i nucleo         # list board names for this version
west build -b nucleo_f401re zephyr/samples/basic/blinky
west flash                           # flash with the board's default runner
west debug                           # start a debug session
west build -t menuconfig             # browse Kconfig
```

Use a sample first to prove the toolchain and flashing path. Flash runners include OpenOCD, the vendor programmer, and J-Link, depending on the board definition.

## Application layout

```
app/
  CMakeLists.txt
  prj.conf                 # Kconfig for the application
  app.overlay              # devicetree overlay for all boards, or
  boards/nucleo_f401re.overlay   # board-specific overlay
  src/main.c
```

## Devicetree overlays

An overlay modifies the board's devicetree. Enable a node, select pins through pin control, and set properties. Example for an I2C bus (pin node names come from the SoC pin control header; check yours):

```dts
&i2c1 {
    status = "okay";
    pinctrl-0 = <&i2c1_scl_pb8 &i2c1_sda_pb9>;
    pinctrl-names = "default";
    clock-frequency = <I2C_BITRATE_FAST>;

    sensor0: sensor@48 {
        compatible = "vendor,device";      /* use a binding that exists for the device */
        reg = <0x48>;                      /* 7-bit address */
    };
};
```

Use aliases and node labels to refer to hardware from code. Inspect the merged result in `build/zephyr/zephyr.dts`.

## Clock configuration

Clocks are described in devicetree. The oscillator nodes, the PLL, and the clock controller are configured by overlay. The following is an illustration of the structure for an F4 part; values depend on the SoC and board, so start from the board's own devicetree and change only what you need:

```dts
&clk_hse { clock-frequency = <DT_FREQ_M(8)>; status = "okay"; };

&pll {
    div-m = <4>; mul-n = <168>; div-p = <2>; div-q = <7>;
    clocks = <&clk_hse>;
    status = "okay";
};

&rcc {
    clocks = <&pll>;
    clock-frequency = <DT_FREQ_M(168)>;
    ahb-prescaler = <1>; apb1-prescaler = <4>; apb2-prescaler = <2>;
};
```

Check each bus's maximum frequency and the flash wait states, which the clock driver sets from the configuration.

## Kconfig

```
CONFIG_GPIO=y
CONFIG_SERIAL=y
CONFIG_I2C=y
CONFIG_LOG=y
CONFIG_ASSERT=y
CONFIG_MAIN_STACK_SIZE=2048
```

Run menuconfig or read `build/zephyr/.config` to confirm values. Stack size, heap size (`CONFIG_HEAP_MEM_POOL_SIZE`), and logging options affect RAM use. Optional diagnostics such as stack-size checking and thread names are available through Kconfig; check the option names in your version.

## Drivers through the device API

```c
#include <zephyr/kernel.h>
#include <zephyr/device.h>
#include <zephyr/drivers/gpio.h>
#include <zephyr/drivers/i2c.h>

static const struct gpio_dt_spec led = GPIO_DT_SPEC_GET(DT_ALIAS(led0), gpios);
static const struct device *const i2c = DEVICE_DT_GET(DT_NODELABEL(i2c1));

int main(void)
{
    if (!gpio_is_ready_dt(&led) || !device_is_ready(i2c)) { return -1; }
    gpio_pin_configure_dt(&led, GPIO_OUTPUT_ACTIVE);

    uint8_t reg = 0x00, val;
    int rc = i2c_write_read(i2c, 0x48, &reg, 1, &val, 1);   /* 7-bit address */
    (void)rc;
    for (;;) { gpio_pin_toggle_dt(&led); k_msleep(500); }
}
```

Header paths and API names change between releases; verify with the version's documentation.

## Threads and synchronization

Use `K_THREAD_DEFINE` or `k_thread_create`, with stack sizes in bytes, and communicate with `k_msgq`, `k_sem`, `k_mutex`, `k_fifo`, or work queues. Interrupt handlers call the ISR-safe functions only. Zephyr priorities are numerically lower for higher urgency, and cooperative priorities (negative numbers) are never preempted by other threads.

## Low power

Power management is enabled through Kconfig and per-device power states. Define the system-level power states in devicetree and enable the PM options. The kernel uses an idle policy to enter low-power states and handles the tick with the SoC's low-power timer on supported parts. Check the supported states for your SoC in its documentation, and measure.

## MCUboot

Zephyr integrates MCUboot as a bootloader image built together with the application through the sysbuild mechanism, with partitions defined in devicetree (a `boot_partition`, `slot0_partition`, `slot1_partition`, and a scratch partition for some swap modes). Enable it with a sysbuild configuration option, and the build signs the application image with the configured key. The exact option names and the workflow for confirming images (test and confirm) are in the documentation for your version. Verify that partition boundaries follow the flash erase layout of the SoC.

## Debugging

- Use `west debug` with the board's runner, or attach GDB to OpenOCD or a vendor server.
- Fatal errors print the exception frame, fault status, and thread name over the console; use these like the fault registers in `stm32-debug`.
- Logging with the logging subsystem is the first tool; use deferred mode so it does not block in time-critical paths.
- Stack overflows: enable the stack protection options listed in the documentation; they turn silent corruption into a reported fault.

## Common errors

| Symptom | Likely cause | Check |
|---|---|---|
| Board not found | Name changed between versions, board qualifiers | `west boards`; read the board documentation |
| Devicetree error: node not found | Wrong label, binding missing | Check labels in the generated tree |
| Build error about undefined Kconfig symbol | Option renamed or missing dependency | Run menuconfig; read the warnings |
| Device not ready | Node disabled, pinctrl missing, driver option off, init failed | Check status, pins, and Kconfig |
| Hard fault at boot | Clock configuration wrong, stack too small | Compare with the board's default clock settings; raise stack |
| Flash fails | Runner missing, probe not connected, wrong runner | `west flash --runner ...`; check the connection |
