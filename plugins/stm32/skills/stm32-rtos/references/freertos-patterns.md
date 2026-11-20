# FreeRTOS patterns on STM32

API names follow the native FreeRTOS API. In the CMSIS-RTOS v2 wrapper use the equivalent calls; check the wrapper documentation.

## Contents
- ISR to task with a notification
- ISR to task with a queue
- UART DMA with idle-line detection
- Shared bus protection
- Blocking driver calls with a completion semaphore
- Periodic task timing

## ISR to task with a notification

A notification is the lightest way to wake one task from an interrupt.

```c
static TaskHandle_t s_worker;

void HAL_GPIO_EXTI_Callback(uint16_t pin)          /* interrupt context */
{
    BaseType_t woken = pdFALSE;
    vTaskNotifyGiveFromISR(s_worker, &woken);
    portYIELD_FROM_ISR(woken);
}

static void worker_task(void *arg)
{
    for (;;) {
        ulTaskNotifyTake(pdTRUE, portMAX_DELAY);   /* returns the number of pending events */
        /* handle the event */
    }
}
```

This interrupt must be at or below the maximum syscall priority.

## ISR to task with a queue

```c
typedef struct { uint16_t start; uint16_t len; } rx_chunk_t;
static QueueHandle_t s_q;                           /* xQueueCreate(8, sizeof(rx_chunk_t)) */

void isr_post(uint16_t start, uint16_t len)
{
    BaseType_t woken = pdFALSE;
    rx_chunk_t c = { start, len };
    if (xQueueSendFromISR(s_q, &c, &woken) != pdPASS) { /* count the drop */ }
    portYIELD_FROM_ISR(woken);
}
```

Queues copy items, so pass small descriptors (indices into a buffer) rather than large payloads.

## UART DMA with idle-line detection

Receive into a circular DMA buffer. In the receive-event callback (called on idle, half, and full events), compute the new bytes from the position, post a descriptor to a queue, and let a task parse. Process only the new range, and handle the wrap-around by splitting into two copies. Count overruns when the queue is full.

## Shared bus protection

Use a mutex per bus (not a binary semaphore) so priority inheritance applies, and take it with a timeout:

```c
static SemaphoreHandle_t s_i2c_mutex;               /* xSemaphoreCreateMutex() */

int sensor_read(uint8_t reg, uint8_t *buf, uint16_t n)
{
    if (xSemaphoreTake(s_i2c_mutex, pdMS_TO_TICKS(100)) != pdTRUE) return -1;
    int rc = bus_read(reg, buf, n);
    xSemaphoreGive(s_i2c_mutex);
    return rc;
}
```

Mutexes cannot be taken from an ISR.

## Blocking driver calls with a completion semaphore

Start the interrupt or DMA transfer, then wait for the completion callback to give a binary semaphore, with a timeout:

```c
static SemaphoreHandle_t s_done;                    /* xSemaphoreCreateBinary() */

int i2c_read_blocking(uint16_t addr, uint8_t *buf, uint16_t n)
{
    if (HAL_I2C_Master_Receive_IT(&hi2c1, addr << 1, buf, n) != HAL_OK) return -1;
    return (xSemaphoreTake(s_done, pdMS_TO_TICKS(50)) == pdTRUE) ? 0 : -2;   /* timeout */
}

void HAL_I2C_MasterRxCpltCallback(I2C_HandleTypeDef *h)
{
    BaseType_t woken = pdFALSE;
    xSemaphoreGiveFromISR(s_done, &woken);
    portYIELD_FROM_ISR(woken);
}
```

On timeout, abort the transfer and recover the bus before the next use. The task waits without consuming the CPU.

## Periodic task timing

Use the absolute-delay call for fixed-rate tasks so execution time does not accumulate as drift:

```c
TickType_t last = xTaskGetTickCount();
for (;;) {
    vTaskDelayUntil(&last, pdMS_TO_TICKS(10));
    /* periodic work */
}
```

Check for overruns by comparing the elapsed time with the period, and count them.
