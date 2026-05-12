Status: PROVISIONAL
Phase: CONVERGE-02
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
