# Authority and Reconciliation


> SOURCE PATH: `docs/archive/conversations/_reconciliation/REPO_AUTHORITY_CROSSWALK_v0.md`


## Repo Authority Crosswalk v0

This crosswalk compares the derived synthesis to current authority surfaces. It does not promote any conversation claim.

| Authority Surface | Current Role | How The Synthesis Uses It | Promotion Effect |
| --- | --- | --- | --- |
| [constitution_v1.md](../../../canon/constitution_v1.md) | Highest architectural/execution contract | Establishes determinism, process mutation, authority, refusal, render separation, packs | None |
| [glossary_v1.md](../../../canon/glossary_v1.md) | Canonical vocabulary | Anchors terms such as Engine, Client, Contract, AuthorityContext, Domain | None |
| [AGENTS.md](../../../../AGENTS.md) | Agent governance and authority ordering | Prevents chat claims from overriding repo truth | None |
| [AUTHORITY_ORDER.md](../../../planning/AUTHORITY_ORDER.md) | Conflict resolution and precedence | Requires reconciliation before promotion | None |
| [SNAPSHOT_INTAKE_PROTOCOL.md](../../../planning/SNAPSHOT_INTAKE_PROTOCOL.md) | Source-role and provenance intake law | Treats conversation exports as materialized evidence only | None |
| [.aide/queue/current.toml](../../../../.aide/queue/current.toml) | Current queue and blocked scope | Blocks broad feature work despite old chat intent | None |
| [PROJECT_SYNTHESIS_BOOK_v0.md](../_synthesis/PROJECT_SYNTHESIS_BOOK_v0.md) | Derived synthesis | Human-readable historical project picture | None |

### Classification Counts

- `blocked_by_current_queue`: `10`
- `consistent_with_repo_but_not_formalized`: `41`
- `insufficient_evidence`: `46`
- `needs_user_decision`: `12`
- `rejected_noise`: `19`
- `stale_or_superseded`: `7`



> SOURCE PATH: `docs/archive/conversations/_reconciliation/CURRENT_CANON_ALIGNMENT_v0.md`


## Current Canon Alignment v0

This review identifies broad areas where the conversation-derived synthesis appears aligned with current canon, and where caution remains.

### Aligned Signals

- Determinism, replay, and provenance recur in the corpus and are directly supported by constitution axioms.
- Truth/perceived/render separation recurs in UI, renderer, and Workbench conversations and is explicitly canonical.
- Process-only mutation and law-gated authority are compatible with the archive's repeated refusal of UI-owned truth.
- Pack-driven integration recurs in content/provider/modding conversations and is canonical in high-level doctrine.
- AIDE/Codex/XStack as bounded repo-control surfaces aligns with AGENTS.md when they remain non-authoritative.

### Caution Areas

- Conversation claims about implementation sequencing must obey current queue constraints.
- Claims about renderer, native GUI, provider runtime, package runtime, gameplay, and release publication are blocked until stronger current authority opens them.
- Old language/platform/baseline claims require current verification before reuse.
- Synthesis terms not present in the glossary cannot become canonical without controlled glossary work.



> SOURCE PATH: `docs/archive/conversations/_reconciliation/BLOCKED_SCOPE_ALIGNMENT_v0.md`


## Blocked Scope Alignment v0

Current queue state blocks broad feature work. Conversation-derived claims that touch these areas remain historical unless a later reviewed task opens scope.

| Blocked Scope | Queue State | Candidate/Finding Signals | Required Disposition |
| --- | --- | ---: | --- |
| `broad_workbench_ui` | `BLOCKED` | `7` | `preserve_or_reconcile_only` |
| `gameplay` | `BLOCKED` | `35` | `preserve_or_reconcile_only` |
| `native_gui` | `BLOCKED` | `14` | `preserve_or_reconcile_only` |
| `package_runtime` | `BLOCKED` | `4` | `preserve_or_reconcile_only` |
| `provider_runtime` | `BLOCKED` | `21` | `preserve_or_reconcile_only` |
| `release_publication` | `BLOCKED` | `8` | `preserve_or_reconcile_only` |
| `renderer_implementation` | `BLOCKED` | `18` | `preserve_or_reconcile_only` |
| `runtime_module_loader` | `BLOCKED` | `5` | `preserve_or_reconcile_only` |

No row authorizes implementation. This is a guardrail for later claim review.



> SOURCE PATH: `docs/archive/conversations/_reconciliation/CLAIM_REVIEW_MATRIX_v0.md`


## Claim Review Matrix v0

Each row is a raw promotion candidate classified for review. None are promoted.


> Dense table summarized for the reader edition. See the source file, HTML output, or reference appendix source for full detail.

| ID | Source | Classification | Disposition | Claim |
| --- | --- | --- | --- | --- |
| `PROMOTE-0001` | `advanced_simulation_infrastructure` | `needs_user_decision` | `ask_or_reconcile_before_promotion` | The user then asked whether arbitrary placement was possible or whether the system was stuck to grids. The answer established that the engine should be grid-agnostic. [FACT] The user's question directly made arbitrary placement a major topic. [INFERENCE] Th... |
| `PROMOTE-0002` | `advanced_simulation_infrastructure` | `rejected_noise` | `preserve_as_history` | Finally, the chat shifted into archival mode: it produced a maximum-fidelity context transfer packet, then a downloadable report package, then an in-chat reader version. Those later outputs preserved the discussion for future aggregation. |
| `PROMOTE-0003` | `advanced_simulation_infrastructure` | `consistent_with_repo_but_not_formalized` | `candidate_for_reconciliation` | [INFERENCE] The conclusion was not a finalized implementation but a working architecture: each simulation domain should be deterministic, fixed-point, content-driven, versioned, replayable, and integrated through clear read/write boundaries. |
| `PROMOTE-0004` | `app_runtime_platform_renderers` | `consistent_with_repo_but_not_formalized` | `candidate_for_reconciliation` | The central topic was APP0: the application/runtime/platform/renderer layer of Dominium. This topic came up because the user provided a formal prompt defining what APP0 should do. |
| `PROMOTE-0005` | `app_runtime_platform_renderers` | `blocked_by_current_queue` | `needs_review_before_any_action` | The most important conclusion was that APP0 must remain outside the core simulation rules. **FACT:** the user explicitly forbade redesigning simulation rules, altering content definitions, changing life/civilization/economy logic, and introducing gameplay s... |
| `PROMOTE-0006` | `app_runtime_platform_renderers` | `needs_user_decision` | `ask_or_reconcile_before_promotion` | Future work must define the client's allowed dependency surface and whether it can access any simulation-adjacent prediction layer. |
| ... | 129 additional rows omitted from reader view |
