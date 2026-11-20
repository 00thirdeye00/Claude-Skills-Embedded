---
name: embedded-release
description: Walk a go/no-go checklist for shipping firmware: build traceability, integrity, update safety, protection, and verification.
argument-hint: "<release description: product, MCU, update method, target date>"
disable-model-invocation: true
---

# /embedded-core:embedded-release

Produce and walk a go/no-go checklist for shipping firmware, including factory programming and field updates.

If no context is given, ask for the product, MCU, how devices are programmed in production, and whether firmware updates in the field.

## Workflow

1. **Collect release facts**: version, hardware revisions supported, update path, bootloader version, known issues.
2. **Walk** `references/release-checklist.md`, marking each item Pass, Fail, N/A, or Unknown.
3. **Flag blockers**: any Fail or Unknown on integrity, update safety, or protection settings blocks release.
4. **Report** with the output template and a clear recommendation.

## Output

```markdown
## Release Check: [product] v[version]

### Recommendation: GO / NO-GO / GO WITH CONDITIONS

### Checklist
| Area | Item | Status | Notes |
|---|---|---|---|

### Blockers
- [item and what must happen]

### Rollback plan
[how to recover a bad release in the field]
```

## Rules

- Treat Unknown as not passed until someone verifies it.
- Update safety covers power loss at any point of the update; test it, do not assume it.
- Archive the exact ELF, map file, toolchain version, and build configuration for every release.
- Production protection settings that cannot be undone need an explicit decision from the owner.

## Connectors

Optional (see `CONNECTORS.md`): when `~~source control`, `~~project tracker`, or `~~knowledge base` is connected, use it for diffs, tickets, and datasheets.
