# STM32 GPIO and EXTI

HAL names are shown for orientation; confirm against your HAL version. Register-level details and available pin features depend on the part.

## Contents
- GPIO modes and settings
- Atomic pin access
- EXTI mapping and configuration
- Debounce
- Wake-up from low-power modes
- Failure modes

## GPIO modes and settings

| Setting | Options | Notes |
|---|---|---|
| Mode | Input, general-purpose output, alternate function, analog | Analog disconnects the digital input buffer and gives the lowest leakage |
| Output type | Push-pull, open-drain | Open-drain needs a pull-up for the high level |
| Pull | None, pull-up, pull-down | Internal resistors are weak (tens of kilohms); use external ones for buses |
| Speed | Low to very high | Higher speed means faster edges and more EMI; choose the lowest that meets timing |
| Alternate function | AF number from the datasheet table | Pin and function pairs are fixed by silicon |

Enable the port clock before configuring. After reset most pins are inputs or analog (family dependent), and the debug pins keep their debug function.

## Atomic pin access

Use the bit set/reset register (HAL `HAL_GPIO_WritePin` does this) instead of read-modify-write on the output data register, so an interrupt cannot interleave and lose another pin's update.

## EXTI mapping and configuration

- EXTI line `n` can listen to pin `n` of one port at a time. A system-configuration register selects the port per line, so PA3 and PB3 cannot both use line 3.
- Choose rising, falling, or both edges, and interrupt or event mode.
- Several lines share a vector on many families (for example lines 5 to 9 and 10 to 15), so the handler must check which line is pending.
- Set the NVIC priority, enable the interrupt, and clear the pending flag (HAL: `HAL_GPIO_EXTI_IRQHandler` clears it and calls `HAL_GPIO_EXTI_Callback(GPIO_Pin)`; newer families use separate rising and falling callbacks).
- Configure the pin and the EXTI before enabling the interrupt, so initialization does not cause a spurious trigger. Clear any pending flag after configuring.

```c
GPIO_InitTypeDef g = {0};
__HAL_RCC_GPIOC_CLK_ENABLE();
g.Pin  = GPIO_PIN_13;
g.Mode = GPIO_MODE_IT_FALLING;      /* button to ground */
g.Pull = GPIO_PULLUP;
HAL_GPIO_Init(GPIOC, &g);
HAL_NVIC_SetPriority(EXTI15_10_IRQn, 6, 0);   /* priority numbers: respect the RTOS limit */
HAL_NVIC_EnableIRQ(EXTI15_10_IRQn);
```

The vector name and the way to enable it differ per family.

## Debounce

Mechanical contacts bounce for several milliseconds. Options: on the first edge disable the EXTI interrupt and start a timer for 10 to 50 ms, then sample the pin; or sample the pin periodically in a task and require a stable value for N samples; or use a hardware RC filter plus a Schmitt-trigger input.

## Wake-up from low-power modes

An EXTI line configured as interrupt or event can wake the device from Sleep and Stop modes. Standby and Shutdown wake through dedicated wake-up pins, not general EXTI lines. Clear the wake flags before entering the mode, and re-check the pin state after waking, because a short pulse may have ended.

## Failure modes

| Symptom | Likely cause | Check |
|---|---|---|
| Pin does not toggle | Port clock off, wrong mode, pin held by another function (AF, debug), wrong pin | Read the mode and AF registers; check the schematic |
| Output level wrong | Open-drain without pull-up, load too heavy, pin conflicts | Measure on the pin; check output type and load |
| EXTI never fires | Line not mapped to the port, interrupt not enabled, wrong vector, edge setting | Check the line-to-port mapping, NVIC enable, handler name |
| Fires repeatedly | Pending flag not cleared, noisy or floating input, bounce | Clear the flag, add a pull, add debounce |
| Wrong line fires | Shared vector not demultiplexed | Check which pending flag is set |
| High current in sleep | Floating inputs, driven pins fighting external circuits | Set unused pins to analog; review external pull-ups |
