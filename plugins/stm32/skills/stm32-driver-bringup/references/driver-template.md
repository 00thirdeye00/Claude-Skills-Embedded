# Driver structure template

HAL function names and signatures vary between HAL versions; confirm against your HAL headers.

## Contents
- Layers
- Bus port interface
- I2C port using HAL
- SPI port using HAL
- Device driver skeleton
- Bring-up order and checks

## Layers

```
application  ->  device API (init, read_sample, set_mode)
device driver ->  bus port (read_reg, write_reg, delay)
bus port      ->  HAL (HAL_I2C_Mem_Read, HAL_SPI_TransmitReceive, ...)
```

## Bus port interface

```c
typedef struct {
    int  (*read)(void *ctx, uint8_t reg, uint8_t *buf, uint16_t len);
    int  (*write)(void *ctx, uint8_t reg, const uint8_t *buf, uint16_t len);
    void (*delay_ms)(uint32_t ms);
    void *ctx;                         /* bus-specific context */
} dev_bus_t;                           /* return 0 on success, negative on error */
```

## I2C port using HAL

```c
typedef struct { I2C_HandleTypeDef *hi2c; uint8_t addr7; uint32_t timeout_ms; } i2c_port_t;

static int i2c_read(void *ctx, uint8_t reg, uint8_t *buf, uint16_t len)
{
    i2c_port_t *p = ctx;
    HAL_StatusTypeDef s = HAL_I2C_Mem_Read(p->hi2c, (uint16_t)(p->addr7 << 1),
                                           reg, I2C_MEMADD_SIZE_8BIT, buf, len, p->timeout_ms);
    return (s == HAL_OK) ? 0 : -1;
}

static int i2c_write(void *ctx, uint8_t reg, const uint8_t *buf, uint16_t len)
{
    i2c_port_t *p = ctx;
    HAL_StatusTypeDef s = HAL_I2C_Mem_Write(p->hi2c, (uint16_t)(p->addr7 << 1),
                                            reg, I2C_MEMADD_SIZE_8BIT, (uint8_t *)buf, len, p->timeout_ms);
    return (s == HAL_OK) ? 0 : -1;
}
```

HAL expects the 7-bit address shifted left by one.

## SPI port using HAL

```c
typedef struct { SPI_HandleTypeDef *hspi; GPIO_TypeDef *cs_port; uint16_t cs_pin; uint32_t timeout_ms; } spi_port_t;

static int spi_read(void *ctx, uint8_t reg, uint8_t *buf, uint16_t len)
{
    spi_port_t *p = ctx;
    uint8_t cmd = reg | 0x80u;                      /* read flag: device specific */
    HAL_GPIO_WritePin(p->cs_port, p->cs_pin, GPIO_PIN_RESET);
    HAL_StatusTypeDef s = HAL_SPI_Transmit(p->hspi, &cmd, 1, p->timeout_ms);
    if (s == HAL_OK) s = HAL_SPI_Receive(p->hspi, buf, len, p->timeout_ms);
    HAL_GPIO_WritePin(p->cs_port, p->cs_pin, GPIO_PIN_SET);
    return (s == HAL_OK) ? 0 : -1;
}
```

The read flag and command format come from the device datasheet.

## Device driver skeleton

```c
typedef enum { DEV_OK = 0, DEV_ERR_BUS = -1, DEV_ERR_ID = -2, DEV_ERR_TIMEOUT = -3 } dev_status_t;

#define DEV_REG_WHO_AM_I   0x0Fu       /* example values: take from the datasheet */
#define DEV_WHO_AM_I_VALUE 0x33u

typedef struct { dev_bus_t bus; /* config and state fields */ } dev_t;

dev_status_t dev_init(dev_t *d)
{
    uint8_t id = 0;
    d->bus.delay_ms(10);                                   /* power-up time from datasheet */
    if (d->bus.read(d->bus.ctx, DEV_REG_WHO_AM_I, &id, 1) != 0) return DEV_ERR_BUS;
    if (id != DEV_WHO_AM_I_VALUE) return DEV_ERR_ID;
    /* write configuration registers in the datasheet order; read back critical ones */
    return DEV_OK;
}
```

## Bring-up order and checks

1. **Power and reset:** supply within range, reset released, power-up delay respected.
2. **Bus signals:** idle levels, clock frequency, and chip select or address visible on a scope or logic analyzer.
3. **Presence:** ACK on I2C, or a valid ID register on I2C or SPI.
4. **Write and read back** a harmless configuration register.
5. **Features one by one,** checking each against the datasheet's expected result.
6. **Failure paths:** unplug the device, force a bus error, and confirm the driver returns an error and the bus recovers.
7. **Performance:** measure transaction time; move to DMA or interrupts if the blocking time is too large.
