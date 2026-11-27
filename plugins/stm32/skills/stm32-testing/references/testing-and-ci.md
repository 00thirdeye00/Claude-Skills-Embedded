# Testing and CI for STM32 firmware

Tool versions and commands change; pin the versions you have checked.

## Contents
- Host tests with a fake port
- Host build with CMake
- On-target tests
- Hardware-in-the-loop
- Static analysis and build checks
- CI example
- Coverage

## Host tests with a fake port

Drivers should depend on a small interface (see the driver bring-up template) so tests can replace the bus.

```c
/* test double for the bus port */
static uint8_t fake_regs[256];
static int fake_read(void *ctx, uint8_t reg, uint8_t *buf, uint16_t len)
{ (void)ctx; for (uint16_t i = 0; i < len; i++) buf[i] = fake_regs[(uint8_t)(reg + i)]; return 0; }
static int fake_write(void *ctx, uint8_t reg, const uint8_t *buf, uint16_t len)
{ (void)ctx; for (uint16_t i = 0; i < len; i++) fake_regs[(uint8_t)(reg + i)] = buf[i]; return 0; }
static void fake_delay(uint32_t ms) { (void)ms; }

void test_init_reads_id(void)
{
    fake_regs[DEV_REG_WHO_AM_I] = DEV_WHO_AM_I_VALUE;
    dev_t d = { .bus = { fake_read, fake_write, fake_delay, 0 } };
    TEST_ASSERT_EQUAL(DEV_OK, dev_init(&d));
}

void test_init_rejects_wrong_id(void)
{
    fake_regs[DEV_REG_WHO_AM_I] = 0x00;
    dev_t d = { .bus = { fake_read, fake_write, fake_delay, 0 } };
    TEST_ASSERT_EQUAL(DEV_ERR_ID, dev_init(&d));
}
```

Also test error injection (the fake returns an error), timeouts, and boundary values.

## Host build with CMake

```cmake
cmake_minimum_required(VERSION 3.20)
project(fw_host_tests C)
enable_testing()
include(FetchContent)
FetchContent_Declare(unity GIT_REPOSITORY https://github.com/ThrowTheSwitch/Unity.git GIT_TAG <pinned-release-tag>)
FetchContent_MakeAvailable(unity)
add_executable(test_dev tests/test_dev.c src/drivers/dev/dev.c)
target_include_directories(test_dev PRIVATE src/drivers/dev)
target_link_libraries(test_dev PRIVATE unity)
target_compile_options(test_dev PRIVATE -Wall -Wextra -Werror)
add_test(NAME test_dev COMMAND test_dev)
```

Replace the tag with a release you have checked. Other frameworks (Ceedling, CppUTest, GoogleTest) work the same way.

## On-target tests

Run the same framework on the board, print results over UART, RTT, or semihosting, and have a script on the PC read and parse them. Use it for peripherals, DMA, interrupt timing, and flash operations. Keep these tests deterministic and short, and flash them with the same tool used for the product.

## Hardware-in-the-loop

A rig typically has the board, a debug probe, a power control (relay or programmable supply), signal sources and loads, and a PC script that flashes, runs scenarios, reads results, and archives logs. Include power-cycle and reset tests, bus fault injection, and update-path tests (interrupt power during an update).

## Static analysis and build checks

- Compile with strict warnings (`-Wall -Wextra -Wconversion -Wshadow`) and treat them as errors in CI.
- Run a static analyzer (cppcheck or clang-tidy) and, if your standard requires it, a MISRA checker.
- Record the output of `arm-none-eabi-size`, and fail the build on unexpected growth beyond a threshold.
- Collect `-fstack-usage` output and review large frames.

## CI example

```yaml
name: firmware-ci
on: [push, pull_request]
jobs:
  build-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install tools
        run: sudo apt-get update && sudo apt-get install -y gcc-arm-none-eabi cmake cppcheck
      - name: Host unit tests
        run: cmake -S . -B build-host && cmake --build build-host && ctest --test-dir build-host --output-on-failure
      - name: Static analysis
        run: cppcheck --enable=warning,performance,portability --error-exitcode=1 -q src
      - name: Firmware build
        run: cmake -S . -B build-fw -DCMAKE_TOOLCHAIN_FILE=cmake/arm-none-eabi.cmake && cmake --build build-fw
      - name: Size report
        run: arm-none-eabi-size build-fw/firmware.elf
      - uses: actions/upload-artifact@v4
        with: { name: firmware, path: build-fw/firmware.* }
```

Adjust paths, the toolchain file, and the build targets to your project. Hardware tests run on a self-hosted runner attached to the rig.

## Coverage

Build host tests with `--coverage` and produce reports with gcov or gcovr. Coverage shows untested code, not correctness; use it to find gaps in error paths.
