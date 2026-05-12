# Game Domains Root

Status: PROVISIONAL
Phase: CONVERGE-09

`game/domains/` owns Dominium-specific domain implementation: rules, process semantics, deterministic domain engines, and domain-owned simulation behavior.

Domains do not own schemas, registries, capabilities, or protocols as authority; those belong under `contracts/`. Domains do not own authored packs, datasets, or content payloads; those belong under `content/`. Domains do not own human documentation as authority; domain docs belong under `docs/domains/` or existing docs surfaces until CONVERGE-12. Domains do not own runtime adapters, product entrypoints, generated outputs, or install/runtime store state.

Domain code may consume engine substrate and contracts, but it must not mutate truth outside lawful deterministic Process execution. Domain implementation must preserve fixed-point truth where applicable, named RNG streams, stable ordering, deterministic reductions, and process-only mutation.

No presentation state belongs in domain truth. UI, render, AppShell, platform, storage, IPC, and diagnostics adapters belong under `runtime/`; thin product composition belongs under `apps/`.

Root-level domain folders retired in CONVERGE-09 must not be recreated as active source roots. New domain material must be split by ownership across `contracts/`, `game/domains/`, `content/`, `docs/domains/`, and `tests/`.
