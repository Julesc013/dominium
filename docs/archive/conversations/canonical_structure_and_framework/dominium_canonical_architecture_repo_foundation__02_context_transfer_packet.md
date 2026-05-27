## 29. Context Transfer Packet for a Future Chat

### 29.1 Ultra-Condensed Bootstrap Brief

We are continuing from a long Dominium architecture/repository chat. The main project is Dominium, a game/product family built on a reusable Domino substrate/framework. The central problem was months of directory-structure churn blocking development. The user strongly rejected new top-level roots, `src/`/`source/` wrappers, generic junk drawers, and vague structure. The settled top-level roots are `apps`, `engine`, `game`, `runtime`, `contracts`, `content`, `docs`, `tests`, `tools`, `scripts`, `cmake`, `external`, `release`, and `archive`, plus `.aide`, `.github`, `.vscode`, and `.aide.local.example`. Do not add `framework`, `modules`, `plugins`, `profiles`, `labs`, or `sdk` roots.

The current doctrine is: path is not identity; implementation is not contract; UI is not authority; generated output is not source truth. Stable identity lives in contracts, manifests, registries, stable IDs, public headers, artifacts, compatibility corpus, and release metadata. Implementations live in folders and may be replaced behind tests.

Domino Framework is not a new root. It is the collection of public surfaces, ABI headers, contracts, service/provider law, and conformance tests. Engine/runtime are the reference implementation. Dominium game lives in `game`, `content`, and `apps`. Workbench is a production/editing/validation/evidence environment over shared commands/views/documents/evidence, not an authority.

The repo has reportedly undergone actual cleanup commits and now has credible canonical structure with warnings. Full release proof remains not green. Future assistants must verify live status before acting. The next likely tasks are targeted proof hygiene, presentation/projection conformance, provider wedges, and full-gate audits—not broad root redesign.

### 29.2 Source Hierarchy

1. Direct user statements in this chat.
2. Explicit decisions accepted by the user.
3. Current task/register/audit summaries provided by the user.
4. Constraints/preferences register in this report.
5. Artifact ledger and generated files.
6. Inferences clearly labelled.
7. Assistant suggestions not explicitly accepted.
8. General model knowledge, verified if current-world facts matter.

### 29.3 Operating Rules for Future Assistants

Preserve FACT / INFERENCE / UNCERTAIN / PROJECT-CONTEXT labels. Do not assume access to the old chat. Do not re-ask answered questions. Verify stale repo/library/tool facts before relying on them. Do not treat tentative brainstorms as final decisions. Do not repeat rejected roots or vendor-shaped structures. Preserve artifacts and uncertainty. Use structured outputs for continuation.

### 29.4 Active Workstreams

Active workstreams include canonical structure residuals, framework/public surface governance, provider architecture, Workbench/product spine, full-gate proof hygiene, third-party provider fencing, and chat/spec preservation.

### 29.5 Current Priorities

1. Verify current live repo status from fresh export.
2. If fast strict/RepoX is blocked, repair stale evidence/marker debt.
3. If proof gates are clean, continue `PROJECTION-CONFORMANCE-01` or `PRESENTATION-CONTRACT-01`.
4. Avoid broad root cleanup unless a hard validator fails.

### 29.6 Current Open Questions

See Open Questions Register, especially full CTest status, pack internal layout, Lua version, AIDE state classification, and current queue.

### 29.7 Recommended First Action

Ask the user for or generate a fresh tracked-only repo status/export, then verify whether fast strict and RepoX are green. If they are green, proceed with `PROJECTION-CONFORMANCE-01`. If not, repair stale generated evidence/marker debt first.
