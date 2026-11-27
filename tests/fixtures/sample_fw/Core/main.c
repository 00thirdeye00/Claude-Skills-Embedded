void init(void) {
  HAL_NVIC_SetPriority(FDCAN1_IT0_IRQn, 5, 0);
  HAL_NVIC_SetPriority(I2C1_EV_IRQn, 6, 0);
}
