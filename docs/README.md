# Dominium Documentation

Status: current.
Scope: high-level orientation and map.

Normative contracts live under `docs/architecture/` only. All other docs are
guidance, reference, or historical context.

## Core mental model

- The simulation kernel is the source of truth; perception layers are derived.
- Objective snapshots record authoritative state; subjective snapshots record views.
- Packs provide capabilities, data, and assets; executables do not embed content.
- Determinism and replay-first design are mandatory.

## Where to start

- `docs/architecture/WHAT_THIS_IS.md`
- `docs/architecture/WHAT_THIS_IS_NOT.md`
- `docs/architecture/INVARIANTS.md`
- `docs/architecture/CANONICAL_SYSTEM_MAP.md`
- `docs/architecture/CONTRACTS_INDEX.md`

## Documentation taxonomy

- `docs/architecture/` binding contracts and laws
- `docs/roadmap/` goals and coverage tests only
- `docs/content/` data and pack explanation only
- `docs/dev/` developer how-to only
- `docs/modding/` modding how-to only
- `docs/archive/` historical and superseded docs only

## Archival notes

Archived documents are kept for provenance only. Canonical contracts are in
`docs/architecture/`.
