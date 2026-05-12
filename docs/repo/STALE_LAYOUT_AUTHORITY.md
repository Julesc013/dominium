Status: PROVISIONAL
Phase: CONVERGE-07
Supersedes: none
Superseded By: none
Stability: provisional

# Stale Layout Authority

Dominium has older documents that describe or claim authority over physical repository layout. Several are useful for history, intent, or migration planning, but they must not compete with the CONVERGE source-layout contracts.

Current convergence authority:

- machine-readable source layout: `contracts/repo/layout.contract.toml`
- machine-readable root allowlist: `contracts/repo/root_allowlist.toml`
- human target explanation: `docs/repo/REPO_LAYOUT_TARGET.md`

Existing older layout docs are retained as legacy, planning, or reference material unless a later task reconciles them. CONVERGE-02 performs no physical moves.

| Document | Current role | CONVERGE-02 treatment | Future action |
| --- | --- | --- | --- |
| `README.md` | User-facing overview that still references older top-level product roots. | Add a short convergence note; not layout authority. | Refresh after physical layout convergence. |
| `docs/architecture/ARCH_REPO_LAYOUT.md` | Legacy architecture layout reference with stale concrete paths. | Mark with a CONVERGE-02 notice pointing to current contracts. | Reconcile or archive after layout contract hardening. |
| `docs/architecture/DIRECTORY_CONTEXT.md` | Legacy directory context that still claims authoritative layout status. | Mark with a CONVERGE-02 notice pointing to current contracts. | Reconcile or archive after stale-doc cleanup. |
| `docs/restructure/FUTURE_LAYOUT_PROPOSAL.md` | Planning input for restructure with a proposed future layout. | Mark as planning/reference input, not current authority. | Mine useful migration constraints in later phases. |
| `docs/architecture/CANON_INDEX.md` | Legacy canon index that may list stale layout docs as canonical. | Treat as a stale-authority input for layout scope until reconciled. | Reconcile during stale-doc authority cleanup. |
| `docs/repo/REPO_LAYOUT_TARGET.md` | Human explanation of target source layout. | Current human explanation. | Keep aligned with layout contracts. |
| `contracts/repo/layout.contract.toml` | Machine-readable source layout convergence contract. | Current machine-readable layout authority. | Refine during CONVERGE-03 and later. |
| `contracts/repo/root_allowlist.toml` | Machine-readable root-level allowlist. | Current root allowlist authority. | Harden after transitional roots are resolved. |

Do not use any legacy document alone to choose new paths. Future phases must consume the contracts, inventory, move map, and ownership rules before moving or creating roots.

## CONVERGE-03 Move-Map Note

`tools/migration/root_move_map.json` is the operational planning artifact for future physical moves. `docs/repo/MOVE_MAP.md` explains it for human readers. Older layout docs are not move maps and must not be used alone to decide migration targets, shims, split requirements, or phase order.

## CONVERGE-05 Archive Path Note

Older docs may still mention root-level `attic/`, `legacy/`, or `quarantine/` as current roots. After CONVERGE-05 those path claims are stale for current source-layout purposes:

- `attic/` is retired; retained material lives under `archive/historical/attic/`.
- `legacy/` is retired; retained material lives under `archive/legacy/`.
- `quarantine/` is retired; retained material lives under `archive/quarantine/`.

Historical references may remain as history. New path decisions must use the layout contract, root allowlist, inventory, and move map.

## CONVERGE-06 Contract Path Note

Older docs may still mention root-level `schema/` or `schemas/` as current roots. After CONVERGE-06 those path claims are stale for current source-layout purposes:

- `schema/` is retired; retained schema law lives under `contracts/schemas/`.
- `schemas/` is retired; retained schema projections live under `contracts/schemas/`.

The CONVERGE-03 move map is the operational planning artifact for physical moves. Old layout docs are not move maps and must not be used alone to decide whether contract, registry, compatibility, or lock material should move.

## CONVERGE-07 Runtime Path Note

Older docs may still mention root-level `app/`, `appshell/`, `ui/`, or `diag/` as current roots. After CONVERGE-07 those path claims are stale for current source-layout purposes:

- `app/` is retired; retained app runtime source lives under `runtime/app/`.
- `appshell/` is retired; retained AppShell source lives under `runtime/appshell/`.
- `ui/` is retired; retained shared UI runtime source lives under `runtime/ui/`.
- `diag/` is retired; retained diagnostic source lives under `runtime/diagnostics/`.

The move map remains the operational planning artifact. Old layout docs are not move maps and must not be used alone to decide whether runtime, AppShell, platform, render, UI, network, or diagnostic material should move.

## CONVERGE-09 Domain Path Note

Older docs may still mention root-level domain folders such as `geo/`, `chem/`, `worldgen/`, `materials/`, `field/`, `fields/`, `process/`, or `signals/` as current source roots. After CONVERGE-09, moved implementation source lives under `game/domains/`, and those root-level path claims are stale for current source-layout purposes.

`tools/migration/root_move_map.json` and `docs/repo/DOMAIN_SPLIT_REPORT.md` record the operational domain split state. Old layout docs are not move maps and must not be used alone to decide whether domain material belongs in `contracts/`, `game/domains/`, `content/`, `docs/domains/`, or `tests/`.
