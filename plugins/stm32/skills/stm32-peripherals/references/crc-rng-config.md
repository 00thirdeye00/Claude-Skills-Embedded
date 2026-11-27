# STM32 CRC unit and random number generator

Features differ by family. Confirm in the reference manual.

## CRC unit
- The unit computes a CRC with a configurable polynomial on some families and a fixed 32-bit polynomial on others, and feeds data as words (with byte and halfword access variants).
- Parameters that decide the result: polynomial, initial value, input reflection, output reflection, and final XOR. Many parts default to a non-reflected 32-bit CRC with initial value 0xFFFFFFFF, which does **not** match the common software CRC-32 (reflected, initial 0xFFFFFFFF, final XOR 0xFFFFFFFF). On parts with reflection options, set them to match; on parts without, compute the same variant in software on the host.
- Pad data to the word size the hardware expects, and use the same byte order on both sides.
- Test with a known vector on both the host tool and the device before relying on it for image integrity.
- Reset the unit before each independent computation, and protect it with a lock if several tasks use it.

## Random number generator
- Needs its kernel clock configured (often a dedicated 48 MHz-class clock) and enabled; without it no data is produced.
- Check the data-ready flag, and the clock-error and seed-error flags; handle errors by waiting or reinitializing, and never use a value read while an error flag is set.
- Use it to seed a cryptographically secure generator or for nonces; follow the security guidance for your protocol and the family's documentation on certification and limits.
- Do not assume unlimited throughput; read at the documented rate.

## Failure modes
| Symptom | Likely cause | Check |
|---|---|---|
| CRC differs from the PC tool | Reflection, initial value, final XOR, word versus byte feeding | Compare parameters; test a known vector |
| CRC changes between runs | Unit not reset, shared use | Reset before each computation, lock |
| RNG returns nothing | Clock not enabled or wrong source | Kernel clock and enable bit |
| RNG error flags | Clock too slow, seed error | Clock configuration, reinitialize |
