# Architecture: sample

Last updated: 2026-11-23. Target: STM32G474RE, FreeRTOS.

## Modules
| Module | Layer | Purpose | Public header | Depends on | Used by | Status |
|---|---|---|---|---|---|---|
| bsp | BSP | Clocks, pins, HAL port | src/bsp/bsp.h | none | imu, can_comm | stable |
| imu | Driver | IMU driver | src/drivers/imu/imu.h | bsp | app | in progress |
| can_comm | Service | CAN messaging | src/services/can_comm/can_comm.h | bsp | app | in progress |
| app | Application | Tasks and wiring | src/app/app.h | imu, can_comm | none | planned |

## Resource map
### Pins
| Pin | Function | AF | Owner module | Notes |
|---|---|---|---|---|
| PB8 | I2C1_SCL | AF4 | imu | 2.2k pull-up |
| PB9 | I2C1_SDA | AF4 | imu | 2.2k pull-up |
| PA12 | FDCAN1_TX | AF9 | can_comm | |
### Interrupts
| IRQ | Priority | Owner | Context rule |
|---|---|---|---|
| FDCAN1_IT0_IRQn | 5 | can_comm | FromISR API only |
| I2C1_EV_IRQn | 6 | imu | FromISR API only |
