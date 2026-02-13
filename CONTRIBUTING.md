# Contributing to Dominium

This document is the contributor entrypoint for code, data, schema, and governance changes in this repository.

For constitutional architecture rules, start with `docs/architecture/ARCH0_CONSTITUTION.md` and `docs/architecture/CANON_INDEX.md`.

## Repository Structure

Primary directories:

- `engine/` - deterministic simulation substrate (C89)
- `game/` - gameplay/meaning layer (C++98)
- `client/`, `server/`, `launcher/`, `setup/`, `tools/` - product executables
- `schema/` - schema contracts
- `data/` - registries, packs, and canonical data
- `repo/repox/` - static governance rules
- `tests/` - TestX suites and invariants
- `scripts/dev/gate.py` - FAST/STRICT/FULL gate entrypoint
- `tools/xstack/core/` - planner, impact graph, scheduler, cache

## Workflow for Code Changes

1. Identify the owning contract in `docs/architecture/` and `docs/governance/`.
2. Update schema/registry contracts first when behavior shape changes.
3. Keep ownership boundaries intact (Client presentation-only, Setup install mutator, Server authority path).
4. Add or update tests in `tests/invariant/` and `tests/integration/`.
5. Run gate profiles (below) before committing.

## Build and Verify

Configure/build verify lane:

```bash
cmake --preset verify
cmake --build --preset verify
```

Run gate profiles:

```bash
python scripts/dev/gate.py verify --repo-root .
python scripts/dev/gate.py strict --repo-root .
python scripts/dev/gate.py full --repo-root .
```

Profile behavior is defined in `data/registries/gate_policy.json` and documented in `docs/governance/GATE_THROUGHPUT_POLICY.md`.

## FAST / STRICT / FULL Expectations

- `verify` -> FAST (incremental impacted checks)
- `strict` -> STRICT (deeper structural + impacted runtime checks)
- `full` -> FULL (sharded comprehensive lane)

XStack planning and impact analysis:

- `tools/xstack/core/impact_graph.py`
- `tools/xstack/core/plan.py`
- `data/registries/testx_groups.json`
- `data/registries/auditx_groups.json`

## Determinism Requirements

All accepted changes must preserve deterministic behavior:

- no wall-clock/random side effects in canonical paths
- stable ordering for canonical artifacts
- explicit refusal codes for invalid transitions
- deterministic hashing for plans/artifacts where applicable

Relevant references:

- `docs/governance/TESTX_ARCHITECTURE.md`
- `docs/governance/AUDITX_MODEL.md`
- `docs/governance/XSTACK_INCREMENTAL_MODEL.md`

## Code Style and Language Constraints

- C code in deterministic core: **C89/C90**
- C++ code in game/product layers: **C++98**
- Keep compatibility with configured toolchain constraints in `CMakePresets.json`

Use existing style and naming conventions in touched modules; avoid introducing new formatting regimes in isolated edits.

## Updating Schemas

When changing or adding schemas:

1. Add/modify schema under `schema/`.
2. Update linked registries under `data/registries/`.
3. Keep identifiers stable; never silently repurpose IDs.
4. Update governance/tests if schema shape changes affect enforcement.

Primary references:

- `schema/SCHEMA_VERSIONING.md`
- `schema/SCHEMA_VALIDATION.md`
- `docs/SCHEMA_EVOLUTION.md`

## Updating Registries

For registry changes:

1. Edit the target file in `data/registries/`.
2. Preserve schema IDs, registry IDs, and deterministic ordering.
3. Run gate verify/strict to ensure RepoX/TestX coverage.
4. Update docs when introducing new canonical keys or IDs.

## Adding Domain Packs (Data-First)

Domain additions are pack-driven, not hardcoded mode logic.

Typical flow:

1. Create/update pack content under `data/packs/<pack_id>/`.
2. Provide/update `pack_manifest.json` and `pack.manifest`.
3. Register new process/material/scenario/worldgen entries in relevant registries (for example `data/registries/process_registry.json` or `data/registries/worldgen_module_registry.json`).
4. Ensure capabilities and law constraints are explicit in profile/law registries.
5. Add TestX coverage for new refusal/selection behavior.

## Writing Tests

Use existing suites:

- Invariants: `tests/invariant/`
- Integration: `tests/integration/`
- Grouped execution: `scripts/dev/run_xstack_group_tests.py`

If your change affects XStack routing, update:

- `data/registries/testx_groups.json`
- `data/registries/auditx_groups.json`

and corresponding tests:

- `tests/invariant/test_testx_group_mapping.py`
- `tests/invariant/test_auditx_group_mapping.py`

## Updating Documentation and Architectural Artifacts

When changing contracts or behavior:

1. Update docs in `docs/` in the same change.
2. Keep terms aligned with `docs/GLOSSARY.md`.
3. Cross-link to schema/registry paths, not vague concepts.
4. Regenerate derived audit docs only when the underlying run actually changed.

## Pull Request Checklist

- [ ] Scope matches architecture ownership boundaries
- [ ] Schema/registry updates included where required
- [ ] Determinism assumptions documented and tested
- [ ] FAST and STRICT gate profiles pass locally
- [ ] Documentation updated with accurate paths/IDs
