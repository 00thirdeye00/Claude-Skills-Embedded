# STM32 I2C configuration

HAL names are shown for orientation; confirm against your HAL version. The I2C peripheral differs between families; check the manual for the part.

## Contents
- Peripheral generations
- Pin and clock setup
- Transfer functions
- Error handling
- Bus recovery
- Slave mode
- Failure modes

## Peripheral generations

- **Older peripheral** (for example on F1, F2, F4, L1): speed set by clock-control and rise-time registers; has known errata and sensitive state handling. Check the errata sheet and keep timeouts and recovery in the code.
- **Newer peripheral** (for example on F0, F3, F7, G0, G4, L0, L4, H7): speed set by a timing register that encodes prescaler, setup, hold, and clock-high and clock-low periods. Generate the value for the kernel clock and target speed with the vendor configuration tool or the formulas in the reference manual. The value changes whenever the kernel clock changes, and the analog and digital filters shift the effective timing.

## Pin and clock setup

- Configure SCL and SDA as alternate function, open-drain, with the AF from the datasheet. Use external pull-ups sized for the bus (see the protocols reference); internal pull-ups are too weak for most buses.
- Enable the port and I2C clocks. Select the I2C kernel clock where the family has a mux.
- Fast-mode plus on some families needs an extra enable bit in the system configuration registers for the pins.

## Transfer functions

| Purpose | HAL example |
|---|---|
| Write bytes | `HAL_I2C_Master_Transmit` |
| Read bytes | `HAL_I2C_Master_Receive` |
| Register write or read (address then data, repeated start) | `HAL_I2C_Mem_Write`, `HAL_I2C_Mem_Read` |
| Presence check or bus scan | `HAL_I2C_IsDeviceReady` |
| Interrupt and DMA variants | `..._IT`, `..._DMA` with completion callbacks |

The HAL expects the 7-bit address shifted left by one. Use a timeout on blocking calls. For interrupt and DMA modes, a second transfer must wait for the first to finish.

## Error handling

Read the error code after a failed call. Typical codes: acknowledge failure (device absent, busy, wrong address), bus error (misplaced start or stop, noise), arbitration lost (multi-master or noise), overrun, and timeout. For each, decide whether to retry, recover the bus, or report a fault.

## Bus recovery

If a slave holds SDA low after an interrupted transfer, release it by clocking SCL up to nine times until SDA goes high, then generate a stop, then reinitialize the peripheral.

```c
static void i2c_bus_recover(GPIO_TypeDef *scl_port, uint16_t scl_pin,
                            GPIO_TypeDef *sda_port, uint16_t sda_pin)
{
    GPIO_InitTypeDef g = {0};
    g.Mode = GPIO_MODE_OUTPUT_OD; g.Pull = GPIO_NOPULL; g.Speed = GPIO_SPEED_FREQ_LOW;
    g.Pin = scl_pin; HAL_GPIO_Init(scl_port, &g);
    g.Pin = sda_pin; HAL_GPIO_Init(sda_port, &g);
    HAL_GPIO_WritePin(sda_port, sda_pin, GPIO_PIN_SET);

    for (int i = 0; i < 9; i++) {
        HAL_GPIO_WritePin(scl_port, scl_pin, GPIO_PIN_SET);
        delay_us(5);
        if (HAL_GPIO_ReadPin(sda_port, sda_pin) == GPIO_PIN_SET) break;
        HAL_GPIO_WritePin(scl_port, scl_pin, GPIO_PIN_RESET);
        delay_us(5);
    }
    /* Generate STOP: SDA rises while SCL is high. */
    HAL_GPIO_WritePin(scl_port, scl_pin, GPIO_PIN_RESET); delay_us(5);
    HAL_GPIO_WritePin(sda_port, sda_pin, GPIO_PIN_RESET); delay_us(5);
    HAL_GPIO_WritePin(scl_port, scl_pin, GPIO_PIN_SET);   delay_us(5);
    HAL_GPIO_WritePin(sda_port, sda_pin, GPIO_PIN_SET);   delay_us(5);
    /* Then deinitialize and reinitialize the I2C peripheral and its pins. */
}
```

`delay_us` is a short microsecond delay you provide (timer or cycle counter based).

## Slave mode

Set the own address, enable address-match interrupts, and use the HAL listen functions. Handle clock stretching (the slave may hold SCL while it prepares data), the direction flag, and the stop condition callback. Keep the address callback short.

## Failure modes

| Symptom | Likely cause | Check |
|---|---|---|
| ACK failure on a known device | Address not shifted, wrong address, device in reset or unpowered, wrong pins | Scan the bus; decode the address byte |
| Busy flag stuck | Aborted transfer, slave holding SDA | Run recovery; reset the peripheral |
| Works at 100 kHz only | Timing value wrong for the clock, pull-ups too weak | Regenerate timing; scope rise time |
| Timeouts after a clock change | Timing register not regenerated | Recompute for the new kernel clock |
| Corrupted reads | No repeated start where the device needs one, wrong register width | Compare transaction with the datasheet |
| Hangs inside an interrupt-driven transfer | Missing timeout, callback not re-arming | Add timeouts; check callbacks and state |
