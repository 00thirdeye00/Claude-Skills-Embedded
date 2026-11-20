---
name: stm32-release
description: Check an STM32 release and production setup: option bytes, read-out protection policy, image integrity, watchdog, and programming flow.
argument-hint: "<product, STM32 part, production process, security and update needs>"
disable-model-invocation: true
---

# /stm32:stm32-release

Check an STM32 firmware release and its production setup.

If details are missing, ask for the part, whether a bootloader and field updates exist, the security policy for debug access, and how devices are programmed in production.

## Steps

1. **Apply the generic checklist.** With `embedded-core` installed, use `/embedded-core:embedded-release`; otherwise use the items summarized here.
2. **Review option bytes** with `references/option-bytes-and-protection.md`. List each setting, its intended value, and why.
3. **Review image details**: linker regions versus the part, version string, CRC or signature, vector table address, bootloader compatibility.
4. **Review production**: programming tool and script, unique data per unit, post-programming verification, and a test that read-back protection works as intended.
5. **Decide**: list blockers, and give GO, NO-GO, or GO WITH CONDITIONS.

## Output

```markdown
## STM32 Release Check: [product] v[version]

### Recommendation: GO / NO-GO / GO WITH CONDITIONS

### Option bytes
| Setting | Intended value | Verified | Reason |
|---|---|---|---|

### Image and layout
| Item | Status | Notes |
|---|---|---|

### Production
| Step | Status | Notes |
|---|---|---|

### Blockers and conditions
- [..]
```

## Rules

- Do not apply or recommend applying irreversible protection (the highest read-out protection level) without explicit confirmation from the user, who must confirm it was tested on sacrificial units first.
- Take option-byte names, encodings, and consequences from the reference manual for the exact part; encodings differ between families.
- Treat anything unverified as not passed.

## Connectors

Optional (see `CONNECTORS.md`): when `~~source control`, `~~project tracker`, or `~~knowledge base` is connected, use it for diffs, tickets, and datasheets.
