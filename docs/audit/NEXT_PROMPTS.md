Status: DERIVED
Last Reviewed: 2026-02-08
Supersedes: none
Superseded By: none

# Next Prompts (Atomic, Ordered)

1) `PACK-REF-INTEGRITY-0`
- Scope: `data/packs/`
- Goal: resolve missing FAB references in the 14 failing packs, no semantic changes.

2) `PACK-DEPS-CANON-0`
- Scope: `data/packs/`, `schema/pack_manifest.schema`, `tools/pack/pack_validate.py`
- Goal: canonicalize dependency field usage and add deterministic validation messaging.

3) `STUB-CLASSIFY-0`
- Scope: `engine/`, `game/`, `launcher/`, `setup/`, `libs/ui_backends/`, `tools/`
- Goal: classify temporary stubs into acceptable scaffolding vs forbidden authoritative paths and add report enforcement.

4) `INVENTORY-STABILIZE-0`
- Scope: `tools/audit/`, `scripts/audit/`, `docs/audit/INVENTORY_MACHINE.json`
- Goal: remove transient build/test artifacts from machine inventory to make diffs deterministic.

5) `TEST-COVERAGE-SEMANTIC-MAP-0`
- Scope: `tests/`, `docs/audit/TEST_COVERAGE_MATRIX.md`
- Goal: map invariant/capability expectations to concrete tests beyond prefix-only coverage inventory.
