---
name: stm32-security
description: Plan STM32 firmware security: threat model, read-out protection and debug policy, secure boot and signed updates, TrustZone on Cortex-M33 parts, key storage, and crypto peripherals.
argument-hint: "<product, threats, part (TrustZone or not), update method>"
disable-model-invocation: true
---

# /stm32:stm32-security

Build a security plan for an STM32 product and list what must be configured and verified.

## Steps

1. **Threat model first**: what is protected (firmware IP, keys, data, device identity, safety), against whom (casual user, skilled attacker with physical access, remote attacker), and the consequences. Security work without this wastes effort.
2. **Match the part to the needs**: debug protection levels, secure boot support, TrustZone, hardware crypto, secure storage. Use `references/security-notes.md` and confirm in the part's reference manual and security application notes.
3. **Choose controls**: debug and read-out policy, secure boot chain and key handling, signed and anti-rollback updates, secure or non-secure partitioning, key storage, authenticated communication.
4. **Plan lifecycle**: development, production provisioning, field return, end of life. Decide how keys get onto devices and how a compromised key is revoked.
5. **List verification**: tests an attacker would try (debug access, flash readout, fault injection if relevant, malformed updates, downgrade).

## Output

```markdown
## Security Plan: [product]

### Threat model
| Asset | Threat | Impact | Priority |
|---|---|---|---|

### Controls
| Control | Mechanism | Config to apply | Verified by |
|---|---|---|---|

### Lifecycle and keys
- [provisioning, storage, rotation, revocation]

### Residual risks
- [..]
```

## Rules

- Never apply irreversible protection (highest read-out level, TrustZone enable with debug locks, key programming) without explicit confirmation and a tested recovery plan.
- Do not store secrets in source, logs, or generic flash; do not invent key sizes or schemes; choose standard algorithms and libraries.
- This is design guidance, not a certification or a guarantee; recommend expert review for products with significant risk.
- Option-byte names and behavior vary by family; confirm in the reference manual.
