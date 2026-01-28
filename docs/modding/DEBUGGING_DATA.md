# Debugging Data (TOOLS-1)

This guide shows how to validate, inspect, and debug data-only packs without changing code or mutating simulation state.

## Validate a pack
Use `pack_validate` for pack manifests, dependencies, and unit annotations.

```bash
python tools/pack/pack_validate.py --pack-root data/packs/org.dominium.core.units --format json
```

Common issues and fixes:
- `capability_missing`: add a pack that provides the missing capability.
- `namespace_invalid`: ensure IDs are lowercase reverse-DNS.

## Validate FAB data
Use `fab_validate` to check FAB schema integrity. If you pass a pack root (or validate a pack's `data/fab_pack.json` directly), it will also enforce maturity labels in `docs/README.md`.

```bash
python tools/fab/fab_validate.py --input data/packs/org.dominium.core.parts.basic/data/fab_pack.json --format json
```

## Explain refusals
Use `refusal_explain` to map refusals back to schema paths and suggested fixes.

```bash
python tools/inspect/refusal_explain.py --input tmp/fab_validate.json --data data/packs/org.dominium.core.parts.basic/data/fab_pack.json --format json
```

## Inspect capabilities
Use `capability_inspect` to see what a set of packs provides and requires.

```bash
python tools/pack/capability_inspect.py --pack-id org.dominium.core.ecology.basic --pack-id org.dominium.core.population.basic --format json
```

## Diff data safely
Use `fab_diff` to compare two FAB packs.

```bash
python tools/fab/fab_diff.py --left data/packs/org.dominium.core.parts.basic --right data/packs/org.dominium.core.parts.extended --format json
```

## Coverage status
Use `coverage_inspect` to see which coverage levels (C-A..C-H) are satisfied by a selection.

```bash
python tools/coverage/coverage_inspect.py --pack-id org.dominium.core.ecology.basic --format json
```

## Determinism rules
- Always run tools headless via CLI.
- Do not depend on UI-only logic.
- Expect identical output across platforms given the same inputs.
