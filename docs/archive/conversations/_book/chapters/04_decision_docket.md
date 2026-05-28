# Decision Docket


> SOURCE PATH: `docs/archive/conversations/_decision/DECISION_SUMMARY_v0.md`


## Decision Summary v0

Summary of the generated decision docket. No decision is accepted here.

### Counts

- Total decisions: `30`
- `Workbench/AIDE/Codex/tooling`: `6`
- `architecture/boundaries`: `12`
- `provider/content/packs`: `5`
- `release/setup/launcher`: `2`
- `renderer/UI/platform`: `3`
- `world/time/civilization simulation`: `2`

### Owner Counts

- `future_queue_decision`: `18`
- `user_decision`: `12`

### Recommended Defaults

- `defer_pending_user_decision`: `12`
- `defer_until_queue_opens`: `10`
- `keep_blocked`: `8`

### Top 10 Decisions

- `DECISION-0001` `architecture/boundaries`: What disposition should be chosen for this unresolved claim: The user then asked whether arbitrary placement was possible or whether the system was stuck to grids. The answer established that the engine should be grid-agnostic. [FACT] The...?
- `DECISION-0002` `architecture/boundaries`: Should this conversation-derived claim remain archive-only until `gameplay` is explicitly opened?
- `DECISION-0003` `architecture/boundaries`: What disposition should be chosen for this unresolved claim: Future work must define the client's allowed dependency surface and whether it can access any simulation-adjacent prediction layer.?
- `DECISION-0004` `architecture/boundaries`: Should this conversation-derived claim remain archive-only until `provider_runtime` is explicitly opened?
- `DECISION-0005` `provider/content/packs`: Should this conversation-derived claim remain archive-only until `provider_runtime` is explicitly opened?
- `DECISION-0006` `world/time/civilization simulation`: Should this conversation-derived claim become a future review item, remain historical, or be deferred: The assistant formalized this as the Perfect Earth Calendar, later called HPC-E. The final structure is clear, though the exact leap rule remains unresolved.?
- `DECISION-0007` `architecture/boundaries`: What disposition should be chosen for this unresolved claim: Before relying on this chat as project authority, a future assistant or human reviewer must confirm whether Dominium is actually intended to be simulation-heavy, whether strict...?
- `DECISION-0008` `renderer/UI/platform`: Should this conversation-derived claim become a future review item, remain historical, or be deferred: The key thing to remember: this chat produced the standards and prompts for future work; it did not verify or change the project. The next assistant must inspect the actual repo...?
- `DECISION-0009` `architecture/boundaries`: What disposition should be chosen for this unresolved claim: This chat was about preserving and re-grounding Dominium's architecture around a very old constitutional contract, then checking whether the current GitHub repository still foll...?
- `DECISION-0010` `architecture/boundaries`: Should this conversation-derived claim remain archive-only until `provider_runtime` is explicitly opened?

### Safe Near-Term Docs-Only Clarifications

- None in this docket. Current generated decisions are user decisions, queue decisions, or deferrals.
- Items touching blocked queue scope must remain explanatory or deferred; no implementation scope is opened.

### Recommended Deferrals

- `DECISION-0001`: What disposition should be chosen for this unresolved claim: The user then asked whether arbitrary placement was possible or whether the system was stuck to grids. The answer established that the engine should be grid-agnostic. [FACT] The...?
- `DECISION-0002`: Should this conversation-derived claim remain archive-only until `gameplay` is explicitly opened?
- `DECISION-0003`: What disposition should be chosen for this unresolved claim: Future work must define the client's allowed dependency surface and whether it can access any simulation-adjacent prediction layer.?
- `DECISION-0004`: Should this conversation-derived claim remain archive-only until `provider_runtime` is explicitly opened?
- `DECISION-0005`: Should this conversation-derived claim remain archive-only until `provider_runtime` is explicitly opened?
- `DECISION-0006`: Should this conversation-derived claim become a future review item, remain historical, or be deferred: The assistant formalized this as the Perfect Earth Calendar, later called HPC-E. The final structure is clear, though the exact leap rule remains unresolved.?
- `DECISION-0007`: What disposition should be chosen for this unresolved claim: Before relying on this chat as project authority, a future assistant or human reviewer must confirm whether Dominium is actually intended to be simulation-heavy, whether strict...?
- `DECISION-0008`: Should this conversation-derived claim become a future review item, remain historical, or be deferred: The key thing to remember: this chat produced the standards and prompts for future work; it did not verify or change the project. The next assistant must inspect the actual repo...?
- `DECISION-0009`: What disposition should be chosen for this unresolved claim: This chat was about preserving and re-grounding Dominium's architecture around a very old constitutional contract, then checking whether the current GitHub repository still foll...?
- `DECISION-0010`: Should this conversation-derived claim remain archive-only until `provider_runtime` is explicitly opened?
- `DECISION-0011`: Should this conversation-derived claim remain archive-only until `provider_runtime` is explicitly opened?
- `DECISION-0012`: Should this conversation-derived claim remain archive-only until `native_gui` is explicitly opened?



> SOURCE PATH: `docs/archive/conversations/_decision/DECISION_DOCKET_v0.md`


## Decision Docket v0

This docket turns unresolved conversation-derived claims into review questions. It does not decide or promote them.

Decision items: `30`

### architecture/boundaries

#### `DECISION-0001`

- Source promotion/claim IDs: `PROMOTE-0001`
- Source conversations: `advanced_simulation_infrastructure`
- Question: What disposition should be chosen for this unresolved claim: The user then asked whether arbitrary placement was possible or whether the system was stuck to grids. The answer established that the engine should be grid-agnostic. [FACT] The...?
- Why it matters: The claim frames unresolved future work or a decision boundary.
- Current repo authority status: conversation-derived advisory claim; current repo authority not modified
- Queue status: `not directly blocked by queue keyword match`
- Recommended default: `defer_pending_user_decision`
- Decision owner: `user_decision`
- Risk if unresolved: Semantic drift or blocked-scope leakage if treated as current truth too early.
- Evidence needed: Check canon, glossary, AGENTS.md, current queue, target current docs, and source conversation before any promotion.
- Options:
  - `promote_later_after_authority_review`
  - `preserve_as_history`
  - `defer`
- Consequences:
  - promote_later_after_authority_review: creates a future docs-only or planning review task; still does not authorize implementation.
  - preserve_as_history: keeps the archive readable but removes pressure to patch current docs.
  - defer: leaves the claim unresolved until stronger authority or user decision exists.

#### `DECISION-0002`

- Source promotion/claim IDs: `PROMOTE-0005`
- Source conversations: `app_runtime_platform_renderers`
- Question: Should this conversation-derived claim remain archive-only until `gameplay` is explicitly opened?
- Why it matters: The claim touches currently blocked scope: gameplay.
- Current repo authority status: conversation-derived advisory claim; current repo authority not modified
- Queue status: `gameplay`
- Recommended default: `defer_until_queue_opens`
- Decision owner: `future_queue_decision`
- Risk if unresolved: Semantic drift or blocked-scope leakage if treated as current truth too early.
- Evidence needed: Check canon, glossary, AGENTS.md, current queue, target current docs, and source conversation before any promotion.
- Options:
  - `promote_later_after_authority_review`
  - `preserve_as_history`
  - `defer`
- Consequences:
  - promote_later_after_authority_review: creates a future docs-only or planning review task; still does not authorize implementation.
  - preserve_as_history: keeps the archive readable but removes pressure to patch current docs.
  - defer: leaves the claim unresolved until stronger authority or user decision exists.

#### `DECISION-0003`

- Source promotion/claim IDs: `PROMOTE-0006`
- Source conversations: `app_runtime_platform_renderers`
- Question: What disposition should be chosen for this unresolved claim: Future work must define the client's allowed dependency surface and whether it can access any simulation-adjacent prediction layer.?
- Why it matters: The claim frames unresolved future work or a decision boundary.
- Current repo authority status: conversation-derived advisory claim; current repo authority not modified
- Queue status: `not directly blocked by queue keyword match`
- Recommended default: `defer_pending_user_decision`
- Decision owner: `user_decision`
- Risk if unresolved: Semantic drift or blocked-scope leakage if treated as current truth too early.
- Evidence needed: Check canon, glossary, AGENTS.md, current queue, target current docs, and source conversation before any promotion.
- Options:
  - `promote_later_after_authority_review`
  - `preserve_as_history`
  - `defer`
- Consequences:
  - promote_later_after_authority_review: creates a future docs-only or planning review task; still does not authorize implementation.
  - preserve_as_history: keeps the archive readable but removes pressure to patch current docs.
  - defer: leaves the claim unresolved until stronger authority or user decision exists.

#### `DECISION-0004`

- Source promotion/claim IDs: `PROMOTE-0015`
- Source conversations: `architecture_ui_providers`
- Question: Should this conversation-derived claim remain archive-only until `provider_runtime` is explicitly opened?
- Why it matters: The claim touches currently blocked scope: provider_runtime.
- Current repo authority status: conversation-derived advisory claim; current repo authority not modified
- Queue status: `provider_runtime`
- Recommended default: `defer_until_queue_opens`
- Decision owner: `future_queue_decision`
- Risk if unresolved: Semantic drift or blocked-scope leakage if treated as current truth too early.
- Evidence needed: Check canon, glossary, AGENTS.md, current queue, target current docs, and source conversation before any promotion.
- Options:
  - `promote_later_after_authority_review`
  - `preserve_as_history`
  - `defer`
- Consequences:
  - promote_later_after_authority_review: creates a future docs-only or planning review task; still does not authorize implementation.
  - preserve_as_history: keeps the archive readable but removes pressure to patch current docs.
  - defer: leaves the claim unresolved until stronger authority or user decision exists.

#### `DECISION-0007`

- Source promotion/claim IDs: `PROMOTE-0025`
- Source conversations: `development_routes`
- Question: What disposition should be chosen for this unresolved claim: Before relying on this chat as project authority, a future assistant or human reviewer must confirm whether Dominium is actually intended to be simulation-heavy, whether strict...?
- Why it matters: The claim frames unresolved future work or a decision boundary.
- Current repo authority status: conversation-derived advisory claim; current repo authority not modified
- Queue status: `not directly blocked by queue keyword match`
- Recommended default: `defer_pending_user_decision`
- Decision owner: `user_decision`
- Risk if unresolved: Semantic drift or blocked-scope leakage if treated as current truth too early.
- Evidence needed: Check canon, glossary, AGENTS.md, current queue, target current docs, and source conversation before any promotion.
- Options:
  - `promote_later_after_authority_review`
  - `preserve_as_history`
  - `defer`
- Consequences:
  - promote_later_after_authority_review: creates a future docs-only or planning review task; still does not authorize implementation.
  - preserve_as_history: keeps the archive readable but removes pressure to patch current docs.
  - defer: leaves the claim unresolved until stronger authority or user decision exists.

#### `DECISION-0009`

- Source promotion/claim IDs: `PROMOTE-0043`
- Source conversations: `Dominium_Complete_Conversation`
- Question: What disposition should be chosen for this unresolved claim: This chat was about preserving and re-grounding Dominium's architecture around a very old constitutional contract, then checking whether the current GitHub repository still foll...?
- Why it matters: The claim frames unresolved future work or a decision boundary.
- Current repo authority status: conversation-derived advisory claim; current repo authority not modified
- Queue status: `not directly blocked by queue keyword match`
- Recommended default: `defer_pending_user_decision`
- Decision owner: `user_decision`
- Risk if unresolved: Semantic drift or blocked-scope leakage if treated as current truth too early.
- Evidence needed: Check canon, glossary, AGENTS.md, current queue, target current docs, and source conversation before any promotion.
- Options:
  - `promote_later_after_authority_review`
  - `preserve_as_history`
  - `defer`
- Consequences:
  - promote_later_after_authority_review: creates a future docs-only or planning review task; still does not authorize implementation.
  - preserve_as_history: keeps the archive readable but removes pressure to patch current docs.
  - defer: leaves the claim unresolved until stronger authority or user decision exists.

#### `DECISION-0010`

- Source promotion/claim IDs: `PROMOTE-0049`
- Source conversations: `dominium_full_conversation`
- Question: Should this conversation-derived claim remain archive-only until `provider_runtime` is explicitly opened?
- Why it matters: The claim touches currently blocked scope: provider_runtime.
- Current repo authority status: conversation-derived advisory claim; current repo authority not modified
- Queue status: `provider_runtime`
- Recommended default: `defer_until_queue_opens`
- Decision owner: `future_queue_decision`
- Risk if unresolved: Semantic drift or blocked-scope leakage if treated as current truth too early.
- Evidence needed: Check canon, glossary, AGENTS.md, current queue, target current docs, and source conversation before any promotion.
- Options:
  - `promote_later_after_authority_review`
  - `preserve_as_history`
  - `defer`
- Consequences:
  - promote_later_after_authority_review: creates a future docs-only or planning review task; still does not authorize implementation.
  - preserve_as_history: keeps the archive readable but removes pressure to patch current docs.
  - defer: leaves the claim unresolved until stronger authority or user decision exists.

#### `DECISION-0014`

- Source promotion/claim IDs: `PROMOTE-0069`
- Source conversations: `Framework_Open_Source_Provider`
- Question: Should this conversation-derived claim remain archive-only until `provider_runtime` is explicitly opened?
- Why it matters: The claim touches currently blocked scope: provider_runtime.
- Current repo authority status: conversation-derived advisory claim; current repo authority not modified
- Queue status: `provider_runtime`
- Recommended default: `defer_until_queue_opens`
- Decision owner: `future_queue_decision`
- Risk if unresolved: Semantic drift or blocked-scope leakage if treated as current truth too early.
- Evidence needed: Check canon, glossary, AGENTS.md, current queue, target current docs, and source conversation before any promotion.
- Options:
  - `promote_later_after_authority_review`
  - `preserve_as_history`
  - `defer`
- Consequences:
  - promote_later_after_authority_review: creates a future docs-only or planning review task; still does not authorize implementation.
  - preserve_as_history: keeps the archive readable but removes pressure to patch current docs.
  - defer: leaves the claim unresolved until stronger authority or user decision exists.

#### `DECISION-0015`

- Source promotion/claim IDs: `PROMOTE-0075`
- Source conversations: `Language_Platform_Architecture`
- Question: Should this conversation-derived claim remain archive-only until `provider_runtime` is explicitly opened?
- Why it matters: The claim touches currently blocked scope: provider_runtime.
- Current repo authority status: conversation-derived advisory claim; current repo authority not modified
- Queue status: `provider_runtime`
- Recommended default: `defer_until_queue_opens`
- Decision owner: `future_queue_decision`
- Risk if unresolved: Semantic drift or blocked-scope leakage if treated as current truth too early.
- Evidence needed: Check canon, glossary, AGENTS.md, current queue, target current docs, and source conversation before any promotion.
- Options:
  - `promote_later_after_authority_review`
  - `preserve_as_history`
  - `defer`
- Consequences:
  - promote_later_after_authority_review: creates a future docs-only or planning review task; still does not authorize implementation.
  - preserve_as_history: keeps the archive readable but removes pressure to patch current docs.
  - defer: leaves the claim unresolved until stronger authority or user decision exists.

#### `DECISION-0018`

- Source promotion/claim IDs: `PROMOTE-0113`
- Source conversations: `testx_repox_governance`
- Question: What disposition should be chosen for this unresolved claim: The user then asked whether the implementation was industry-accepted and what could be improved. The response framed the approach as closer to game engines, operating systems, a...?
- Why it matters: The claim frames unresolved future work or a decision boundary.
- Current repo authority status: conversation-derived advisory claim; current repo authority not modified
- Queue status: `not directly blocked by queue keyword match`
- Recommended default: `defer_pending_user_decision`
- Decision owner: `user_decision`
- Risk if unresolved: Semantic drift or blocked-scope leakage if treated as current truth too early.
- Evidence needed: Check canon, glossary, AGENTS.md, current queue, target current docs, and source conversation before any promotion.
- Options:
  - `promote_later_after_authority_review`
  - `preserve_as_history`
  - `defer`
- Consequences:
  - promote_later_after_authority_review: creates a future docs-only or planning review task; still does not authorize implementation.
  - preserve_as_history: keeps the archive readable but removes pressure to patch current docs.
  - defer: leaves the claim unresolved until stronger authority or user decision exists.

#### `DECISION-0019`

- Source promotion/claim IDs: `PROMOTE-0120`
- Source conversations: `UE6_Domino_Deterministic_Universe`
- Question: Should this conversation-derived claim remain archive-only until `gameplay` is explicitly opened?
- Why it matters: The claim touches currently blocked scope: gameplay.
- Current repo authority status: conversation-derived advisory claim; current repo authority not modified
- Queue status: `gameplay`
- Recommended default: `defer_until_queue_opens`
- Decision owner: `future_queue_decision`
- Risk if unresolved: Semantic drift or blocked-scope leakage if treated as current truth too early.
- Evidence needed: Check canon, glossary, AGENTS.md, current queue, target current docs, and source conversation before any promotion.
- Options:
  - `promote_later_after_authority_review`
  - `preserve_as_history`
  - `defer`
- Consequences:
  - promote_later_after_authority_review: creates a future docs-only or planning review task; still does not authorize implementation.
  - preserve_as_history: keeps the archive readable but removes pressure to patch current docs.
  - defer: leaves the claim unresolved until stronger authority or user decision exists.

#### `DECISION-0024`

- Source promotion/claim IDs: `blocked_scope:gameplay`
- Source conversations: `current queue plus conversation audit findings`
- Question: Should `gameplay` remain blocked for all conversation-derived work until a future reviewed queue phase opens it?
- Why it matters: The current queue marks `gameplay` as `BLOCKED` and the corpus produced `35` related candidate/finding signals.
- Current repo authority status: .aide/queue/current.toml is current repo authority for this scope gate.
- Queue status: `gameplay: BLOCKED`
- Recommended default: `keep_blocked`
- Decision owner: `future_queue_decision`
- Risk if unresolved: Implementation or live-doc scope could be opened by historical momentum rather than current authority.
- Evidence needed: Review current queue, blocked-scope alignment, and any target prompt before changing disposition.
- Options:
  - `keep_blocked`
  - `docs_only_crosswalk`
  - `defer`
- Consequences:
  - keep_blocked: prevents old conversation claims from opening implementation scope.
  - docs_only_crosswalk: allows explanatory archive/current-doc mapping without implementation or promotion.
  - defer: postpones judgment until the queue is revised.

### Workbench/AIDE/Codex/tooling

#### `DECISION-0011`

- Source promotion/claim IDs: `PROMOTE-0056`
- Source conversations: `Domino_Dominium_Workbench`
- Question: Should this conversation-derived claim remain archive-only until `provider_runtime` is explicitly opened?
- Why it matters: The claim touches currently blocked scope: provider_runtime.
- Current repo authority status: conversation-derived advisory claim; current repo authority not modified
- Queue status: `provider_runtime`
- Recommended default: `defer_until_queue_opens`
- Decision owner: `future_queue_decision`
- Risk if unresolved: Semantic drift or blocked-scope leakage if treated as current truth too early.
- Evidence needed: Check canon, glossary, AGENTS.md, current queue, target current docs, and source conversation before any promotion.
- Options:
  - `promote_later_after_authority_review`
  - `preserve_as_history`
  - `defer`
- Consequences:
  - promote_later_after_authority_review: creates a future docs-only or planning review task; still does not authorize implementation.
  - preserve_as_history: keeps the archive readable but removes pressure to patch current docs.
  - defer: leaves the claim unresolved until stronger authority or user decision exists.

#### `DECISION-0012`

- Source promotion/claim IDs: `PROMOTE-0057`
- Source conversations: `Domino_Dominium_Workbench`
- Question: Should this conversation-derived claim remain archive-only until `native_gui` is explicitly opened?
- Why it matters: The claim touches currently blocked scope: native_gui.
- Current repo authority status: conversation-derived advisory claim; current repo authority not modified
- Queue status: `native_gui`
- Recommended default: `defer_until_queue_opens`
- Decision owner: `future_queue_decision`
- Risk if unresolved: Semantic drift or blocked-scope leakage if treated as current truth too early.
- Evidence needed: Check canon, glossary, AGENTS.md, current queue, target current docs, and source conversation before any promotion.
- Options:
  - `promote_later_after_authority_review`
  - `preserve_as_history`
  - `defer`
- Consequences:
  - promote_later_after_authority_review: creates a future docs-only or planning review task; still does not authorize implementation.
  - preserve_as_history: keeps the archive readable but removes pressure to patch current docs.
  - defer: leaves the claim unresolved until stronger authority or user decision exists.

#### `DECISION-0013`

- Source promotion/claim IDs: `PROMOTE-0065`
- Source conversations: `Foundation_Workbench_Codex`
- Question: Should this conversation-derived claim remain archive-only until `provider_runtime` is explicitly opened?
- Why it matters: The claim touches currently blocked scope: provider_runtime.
- Current repo authority status: conversation-derived advisory claim; current repo authority not modified
- Queue status: `provider_runtime`
- Recommended default: `defer_until_queue_opens`
- Decision owner: `future_queue_decision`
- Risk if unresolved: Semantic drift or blocked-scope leakage if treated as current truth too early.
- Evidence needed: Check canon, glossary, AGENTS.md, current queue, target current docs, and source conversation before any promotion.
- Options:
  - `promote_later_after_authority_review`
  - `preserve_as_history`
  - `defer`
- Consequences:
  - promote_later_after_authority_review: creates a future docs-only or planning review task; still does not authorize implementation.
  - preserve_as_history: keeps the archive readable but removes pressure to patch current docs.
  - defer: leaves the claim unresolved until stronger authority or user decision exists.

#### `DECISION-0020`

- Source promotion/claim IDs: `PROMOTE-0121`
- Source conversations: `ui_editor_tool_editor_planning`
- Question: What disposition should be chosen for this unresolved claim: The most important thing to remember is that this chat was a planning and prompt-generation chat, not proof of implementation. **UNCERTAIN / UNVERIFIED:** No generated prompt is...?
- Why it matters: The claim frames unresolved future work or a decision boundary.
- Current repo authority status: conversation-derived advisory claim; current repo authority not modified
- Queue status: `not directly blocked by queue keyword match`
- Recommended default: `defer_pending_user_decision`
- Decision owner: `user_decision`
- Risk if unresolved: Semantic drift or blocked-scope leakage if treated as current truth too early.
- Evidence needed: Check canon, glossary, AGENTS.md, current queue, target current docs, and source conversation before any promotion.
- Options:
  - `promote_later_after_authority_review`
  - `preserve_as_history`
  - `defer`
- Consequences:
  - promote_later_after_authority_review: creates a future docs-only or planning review task; still does not authorize implementation.
  - preserve_as_history: keeps the archive readable but removes pressure to patch current docs.
  - defer: leaves the claim unresolved until stronger authority or user decision exists.

#### `DECISION-0021`

- Source promotion/claim IDs: `PROMOTE-0123`
- Source conversations: `ui_editor_tool_editor_planning`
- Question: Should this conversation-derived claim become a future review item, remain historical, or be deferred: The user uploaded screenshot bundles for setup and launcher. **UNCERTAIN / UNVERIFIED:** The screenshots were not inspected in this chat. The assistant still produced a logical...?
- Why it matters: The claim frames unresolved future work or a decision boundary.
- Current repo authority status: conversation-derived advisory claim; current repo authority not modified
- Queue status: `not directly blocked by queue keyword match`
- Recommended default: `defer_pending_user_decision`
- Decision owner: `user_decision`
- Risk if unresolved: Semantic drift or blocked-scope leakage if treated as current truth too early.
- Evidence needed: Check canon, glossary, AGENTS.md, current queue, target current docs, and source conversation before any promotion.
- Options:
  - `promote_later_after_authority_review`
  - `preserve_as_history`
  - `defer`
- Consequences:
  - promote_later_after_authority_review: creates a future docs-only or planning review task; still does not authorize implementation.
  - preserve_as_history: keeps the archive readable but removes pressure to patch current docs.
  - defer: leaves the claim unresolved until stronger authority or user decision exists.

#### `DECISION-0023`

- Source promotion/claim IDs: `blocked_scope:broad_workbench_ui`
- Source conversations: `current queue plus conversation audit findings`
- Question: Should `broad_workbench_ui` remain blocked for all conversation-derived work until a future reviewed queue phase opens it?
- Why it matters: The current queue marks `broad_workbench_ui` as `BLOCKED` and the corpus produced `7` related candidate/finding signals.
- Current repo authority status: .aide/queue/current.toml is current repo authority for this scope gate.
- Queue status: `broad_workbench_ui: BLOCKED`
- Recommended default: `keep_blocked`
- Decision owner: `future_queue_decision`
- Risk if unresolved: Implementation or live-doc scope could be opened by historical momentum rather than current authority.
- Evidence needed: Review current queue, blocked-scope alignment, and any target prompt before changing disposition.
- Options:
  - `keep_blocked`
  - `docs_only_crosswalk`
  - `defer`
- Consequences:
  - keep_blocked: prevents old conversation claims from opening implementation scope.
  - docs_only_crosswalk: allows explanatory archive/current-doc mapping without implementation or promotion.
  - defer: postpones judgment until the queue is revised.

### renderer/UI/platform

#### `DECISION-0008`

- Source promotion/claim IDs: `PROMOTE-0028`
- Source conversations: `documentation_standards_readme`
- Question: Should this conversation-derived claim become a future review item, remain historical, or be deferred: The key thing to remember: this chat produced the standards and prompts for future work; it did not verify or change the project. The next assistant must inspect the actual repo...?
- Why it matters: The claim frames unresolved future work or a decision boundary.
- Current repo authority status: conversation-derived advisory claim; current repo authority not modified
- Queue status: `not directly blocked by queue keyword match`
- Recommended default: `defer_pending_user_decision`
- Decision owner: `user_decision`
- Risk if unresolved: Semantic drift or blocked-scope leakage if treated as current truth too early.
- Evidence needed: Check canon, glossary, AGENTS.md, current queue, target current docs, and source conversation before any promotion.
- Options:
  - `promote_later_after_authority_review`
  - `preserve_as_history`
  - `defer`
- Consequences:
  - promote_later_after_authority_review: creates a future docs-only or planning review task; still does not authorize implementation.
  - preserve_as_history: keeps the archive readable but removes pressure to patch current docs.
  - defer: leaves the claim unresolved until stronger authority or user decision exists.

#### `DECISION-0025`

- Source promotion/claim IDs: `blocked_scope:native_gui`
- Source conversations: `current queue plus conversation audit findings`
- Question: Should `native_gui` remain blocked for all conversation-derived work until a future reviewed queue phase opens it?
- Why it matters: The current queue marks `native_gui` as `BLOCKED` and the corpus produced `14` related candidate/finding signals.
- Current repo authority status: .aide/queue/current.toml is current repo authority for this scope gate.
- Queue status: `native_gui: BLOCKED`
- Recommended default: `keep_blocked`
- Decision owner: `future_queue_decision`
- Risk if unresolved: Implementation or live-doc scope could be opened by historical momentum rather than current authority.
- Evidence needed: Review current queue, blocked-scope alignment, and any target prompt before changing disposition.
- Options:
  - `keep_blocked`
  - `docs_only_crosswalk`
  - `defer`
- Consequences:
  - keep_blocked: prevents old conversation claims from opening implementation scope.
  - docs_only_crosswalk: allows explanatory archive/current-doc mapping without implementation or promotion.
  - defer: postpones judgment until the queue is revised.

#### `DECISION-0029`

- Source promotion/claim IDs: `blocked_scope:renderer_implementation`
- Source conversations: `current queue plus conversation audit findings`
- Question: Should `renderer_implementation` remain blocked for all conversation-derived work until a future reviewed queue phase opens it?
- Why it matters: The current queue marks `renderer_implementation` as `BLOCKED` and the corpus produced `18` related candidate/finding signals.
- Current repo authority status: .aide/queue/current.toml is current repo authority for this scope gate.
- Queue status: `renderer_implementation: BLOCKED`
- Recommended default: `keep_blocked`
- Decision owner: `future_queue_decision`
- Risk if unresolved: Implementation or live-doc scope could be opened by historical momentum rather than current authority.
- Evidence needed: Review current queue, blocked-scope alignment, and any target prompt before changing disposition.
- Options:
  - `keep_blocked`
  - `docs_only_crosswalk`
  - `defer`
- Consequences:
  - keep_blocked: prevents old conversation claims from opening implementation scope.
  - docs_only_crosswalk: allows explanatory archive/current-doc mapping without implementation or promotion.
  - defer: postpones judgment until the queue is revised.

### provider/content/packs

#### `DECISION-0005`

- Source promotion/claim IDs: `PROMOTE-0020`
- Source conversations: `canonical_structure_and_framework`
- Question: Should this conversation-derived claim remain archive-only until `provider_runtime` is explicitly opened?
- Why it matters: The claim touches currently blocked scope: provider_runtime.
- Current repo authority status: conversation-derived advisory claim; current repo authority not modified
- Queue status: `provider_runtime`
- Recommended default: `defer_until_queue_opens`
- Decision owner: `future_queue_decision`
- Risk if unresolved: Semantic drift or blocked-scope leakage if treated as current truth too early.
- Evidence needed: Check canon, glossary, AGENTS.md, current queue, target current docs, and source conversation before any promotion.
- Options:
  - `promote_later_after_authority_review`
  - `preserve_as_history`
  - `defer`
- Consequences:
  - promote_later_after_authority_review: creates a future docs-only or planning review task; still does not authorize implementation.
  - preserve_as_history: keeps the archive readable but removes pressure to patch current docs.
  - defer: leaves the claim unresolved until stronger authority or user decision exists.

#### `DECISION-0017`

- Source promotion/claim IDs: `PROMOTE-0097`
- Source conversations: `Portability_Assurance_Future_Proof`
- Question: Should this conversation-derived claim become a future review item, remain historical, or be deferred: The actual repo was not inspected. The exact accepted directory structure, API policy, DDAP profile, compatibility promises, and first pilot module remain unresolved.?
- Why it matters: The claim frames unresolved future work or a decision boundary.
- Current repo authority status: conversation-derived advisory claim; current repo authority not modified
- Queue status: `not directly blocked by queue keyword match`
- Recommended default: `defer_pending_user_decision`
- Decision owner: `user_decision`
- Risk if unresolved: Semantic drift or blocked-scope leakage if treated as current truth too early.
- Evidence needed: Check canon, glossary, AGENTS.md, current queue, target current docs, and source conversation before any promotion.
- Options:
  - `promote_later_after_authority_review`
  - `preserve_as_history`
  - `defer`
- Consequences:
  - promote_later_after_authority_review: creates a future docs-only or planning review task; still does not authorize implementation.
  - preserve_as_history: keeps the archive readable but removes pressure to patch current docs.
  - defer: leaves the claim unresolved until stronger authority or user decision exists.

#### `DECISION-0026`

- Source promotion/claim IDs: `blocked_scope:package_runtime`
- Source conversations: `current queue plus conversation audit findings`
- Question: Should `package_runtime` remain blocked for all conversation-derived work until a future reviewed queue phase opens it?
- Why it matters: The current queue marks `package_runtime` as `BLOCKED` and the corpus produced `4` related candidate/finding signals.
- Current repo authority status: .aide/queue/current.toml is current repo authority for this scope gate.
- Queue status: `package_runtime: BLOCKED`
- Recommended default: `keep_blocked`
- Decision owner: `future_queue_decision`
- Risk if unresolved: Implementation or live-doc scope could be opened by historical momentum rather than current authority.
- Evidence needed: Review current queue, blocked-scope alignment, and any target prompt before changing disposition.
- Options:
  - `keep_blocked`
  - `docs_only_crosswalk`
  - `defer`
- Consequences:
  - keep_blocked: prevents old conversation claims from opening implementation scope.
  - docs_only_crosswalk: allows explanatory archive/current-doc mapping without implementation or promotion.
  - defer: postpones judgment until the queue is revised.

#### `DECISION-0027`

- Source promotion/claim IDs: `blocked_scope:provider_runtime`
- Source conversations: `current queue plus conversation audit findings`
- Question: Should `provider_runtime` remain blocked for all conversation-derived work until a future reviewed queue phase opens it?
- Why it matters: The current queue marks `provider_runtime` as `BLOCKED` and the corpus produced `21` related candidate/finding signals.
- Current repo authority status: .aide/queue/current.toml is current repo authority for this scope gate.
- Queue status: `provider_runtime: BLOCKED`
- Recommended default: `keep_blocked`
- Decision owner: `future_queue_decision`
- Risk if unresolved: Implementation or live-doc scope could be opened by historical momentum rather than current authority.
- Evidence needed: Review current queue, blocked-scope alignment, and any target prompt before changing disposition.
- Options:
  - `keep_blocked`
  - `docs_only_crosswalk`
  - `defer`
- Consequences:
  - keep_blocked: prevents old conversation claims from opening implementation scope.
  - docs_only_crosswalk: allows explanatory archive/current-doc mapping without implementation or promotion.
  - defer: postpones judgment until the queue is revised.

#### `DECISION-0030`

- Source promotion/claim IDs: `blocked_scope:runtime_module_loader`
- Source conversations: `current queue plus conversation audit findings`
- Question: Should `runtime_module_loader` remain blocked for all conversation-derived work until a future reviewed queue phase opens it?
- Why it matters: The current queue marks `runtime_module_loader` as `BLOCKED` and the corpus produced `5` related candidate/finding signals.
- Current repo authority status: .aide/queue/current.toml is current repo authority for this scope gate.
- Queue status: `runtime_module_loader: BLOCKED`
- Recommended default: `keep_blocked`
- Decision owner: `future_queue_decision`
- Risk if unresolved: Implementation or live-doc scope could be opened by historical momentum rather than current authority.
- Evidence needed: Review current queue, blocked-scope alignment, and any target prompt before changing disposition.
- Options:
  - `keep_blocked`
  - `docs_only_crosswalk`
  - `defer`
- Consequences:
  - keep_blocked: prevents old conversation claims from opening implementation scope.
  - docs_only_crosswalk: allows explanatory archive/current-doc mapping without implementation or promotion.
  - defer: postpones judgment until the queue is revised.

### world/time/civilization simulation

#### `DECISION-0006`

- Source promotion/claim IDs: `PROMOTE-0024`
- Source conversations: `Chronology_Celestial_Systems`
- Question: Should this conversation-derived claim become a future review item, remain historical, or be deferred: The assistant formalized this as the Perfect Earth Calendar, later called HPC-E. The final structure is clear, though the exact leap rule remains unresolved.?
- Why it matters: The claim frames unresolved future work or a decision boundary.
- Current repo authority status: conversation-derived advisory claim; current repo authority not modified
- Queue status: `not directly blocked by queue keyword match`
- Recommended default: `defer_pending_user_decision`
- Decision owner: `user_decision`
- Risk if unresolved: Semantic drift or blocked-scope leakage if treated as current truth too early.
- Evidence needed: Check canon, glossary, AGENTS.md, current queue, target current docs, and source conversation before any promotion.
- Options:
  - `promote_later_after_authority_review`
  - `preserve_as_history`
  - `defer`
- Consequences:
  - promote_later_after_authority_review: creates a future docs-only or planning review task; still does not authorize implementation.
  - preserve_as_history: keeps the archive readable but removes pressure to patch current docs.
  - defer: leaves the claim unresolved until stronger authority or user decision exists.

#### `DECISION-0022`

- Source promotion/claim IDs: `PROMOTE-0125`
- Source conversations: `Universe_Explorer_Planning`
- Question: Should this conversation-derived claim become a future review item, remain historical, or be deferred: A major theme was that useful local inventions must become portable, standardized, industrialized, and institutionally adopted. The repo now has a Formalization Chain spec and P...?
- Why it matters: The claim frames unresolved future work or a decision boundary.
- Current repo authority status: conversation-derived advisory claim; current repo authority not modified
- Queue status: `not directly blocked by queue keyword match`
- Recommended default: `defer_pending_user_decision`
- Decision owner: `user_decision`
- Risk if unresolved: Semantic drift or blocked-scope leakage if treated as current truth too early.
- Evidence needed: Check canon, glossary, AGENTS.md, current queue, target current docs, and source conversation before any promotion.
- Options:
  - `promote_later_after_authority_review`
  - `preserve_as_history`
  - `defer`
- Consequences:
  - promote_later_after_authority_review: creates a future docs-only or planning review task; still does not authorize implementation.
  - preserve_as_history: keeps the archive readable but removes pressure to patch current docs.
  - defer: leaves the claim unresolved until stronger authority or user decision exists.

### release/setup/launcher

#### `DECISION-0016`

- Source promotion/claim IDs: `PROMOTE-0076`
- Source conversations: `launcher_app_layer`
- Question: Should this conversation-derived claim become a future review item, remain historical, or be deferred: Someone reading this report should understand one central thing: this chat is not about inventing new launcher features anymore. It is about preserving boundaries, making the la...?
- Why it matters: The claim frames unresolved future work or a decision boundary.
- Current repo authority status: conversation-derived advisory claim; current repo authority not modified
- Queue status: `not directly blocked by queue keyword match`
- Recommended default: `defer_pending_user_decision`
- Decision owner: `user_decision`
- Risk if unresolved: Semantic drift or blocked-scope leakage if treated as current truth too early.
- Evidence needed: Check canon, glossary, AGENTS.md, current queue, target current docs, and source conversation before any promotion.
- Options:
  - `promote_later_after_authority_review`
  - `preserve_as_history`
  - `defer`
- Consequences:
  - promote_later_after_authority_review: creates a future docs-only or planning review task; still does not authorize implementation.
  - preserve_as_history: keeps the archive readable but removes pressure to patch current docs.
  - defer: leaves the claim unresolved until stronger authority or user decision exists.

#### `DECISION-0028`

- Source promotion/claim IDs: `blocked_scope:release_publication`
- Source conversations: `current queue plus conversation audit findings`
- Question: Should `release_publication` remain blocked for all conversation-derived work until a future reviewed queue phase opens it?
- Why it matters: The current queue marks `release_publication` as `BLOCKED` and the corpus produced `8` related candidate/finding signals.
- Current repo authority status: .aide/queue/current.toml is current repo authority for this scope gate.
- Queue status: `release_publication: BLOCKED`
- Recommended default: `keep_blocked`
- Decision owner: `future_queue_decision`
- Risk if unresolved: Implementation or live-doc scope could be opened by historical momentum rather than current authority.
- Evidence needed: Review current queue, blocked-scope alignment, and any target prompt before changing disposition.
- Options:
  - `keep_blocked`
  - `docs_only_crosswalk`
  - `defer`
- Consequences:
  - keep_blocked: prevents old conversation claims from opening implementation scope.
  - docs_only_crosswalk: allows explanatory archive/current-doc mapping without implementation or promotion.
  - defer: postpones judgment until the queue is revised.



> SOURCE PATH: `docs/archive/conversations/_decision/DECISION_OPTIONS_MATRIX_v0.md`


## Decision Options Matrix v0

Matrix view of available decision options. Tables support review but do not replace the docket explanations.


> Dense table summarized for the reader edition. See the source file, HTML output, or reference appendix source for full detail.

| ID | Group | Owner | Queue Status | Recommended Default | Options |
| --- | --- | --- | --- | --- | --- |
| `DECISION-0001` | architecture/boundaries | `user_decision` | `not directly blocked by queue keyword match` | `defer_pending_user_decision` | `promote_later_after_authority_review`, `preserve_as_history`, `defer` |
| `DECISION-0002` | architecture/boundaries | `future_queue_decision` | `gameplay` | `defer_until_queue_opens` | `promote_later_after_authority_review`, `preserve_as_history`, `defer` |
| `DECISION-0003` | architecture/boundaries | `user_decision` | `not directly blocked by queue keyword match` | `defer_pending_user_decision` | `promote_later_after_authority_review`, `preserve_as_history`, `defer` |
| `DECISION-0004` | architecture/boundaries | `future_queue_decision` | `provider_runtime` | `defer_until_queue_opens` | `promote_later_after_authority_review`, `preserve_as_history`, `defer` |
| `DECISION-0005` | provider/content/packs | `future_queue_decision` | `provider_runtime` | `defer_until_queue_opens` | `promote_later_after_authority_review`, `preserve_as_history`, `defer` |
| `DECISION-0006` | world/time/civilization simulation | `user_decision` | `not directly blocked by queue keyword match` | `defer_pending_user_decision` | `promote_later_after_authority_review`, `preserve_as_history`, `defer` |
| ... | 24 additional rows omitted from reader view |



> SOURCE PATH: `docs/archive/conversations/_decision/DEFERRED_DECISIONS_v0.md`


## Deferred Decisions v0

These decisions should stay deferred unless a human or stronger repo authority opens them.

### `DECISION-0001`

- Group: `architecture/boundaries`
- Question: What disposition should be chosen for this unresolved claim: The user then asked whether arbitrary placement was possible or whether the system was stuck to grids. The answer established that the engine should be grid-agnostic. [FACT] The...?
- Recommended default: `defer_pending_user_decision`
- Queue status: `not directly blocked by queue keyword match`
- Evidence that would resolve it: Check canon, glossary, AGENTS.md, current queue, target current docs, and source conversation before any promotion.

### `DECISION-0002`

- Group: `architecture/boundaries`
- Question: Should this conversation-derived claim remain archive-only until `gameplay` is explicitly opened?
- Recommended default: `defer_until_queue_opens`
- Queue status: `gameplay`
- Evidence that would resolve it: Check canon, glossary, AGENTS.md, current queue, target current docs, and source conversation before any promotion.

### `DECISION-0003`

- Group: `architecture/boundaries`
- Question: What disposition should be chosen for this unresolved claim: Future work must define the client's allowed dependency surface and whether it can access any simulation-adjacent prediction layer.?
- Recommended default: `defer_pending_user_decision`
- Queue status: `not directly blocked by queue keyword match`
- Evidence that would resolve it: Check canon, glossary, AGENTS.md, current queue, target current docs, and source conversation before any promotion.

### `DECISION-0004`

- Group: `architecture/boundaries`
- Question: Should this conversation-derived claim remain archive-only until `provider_runtime` is explicitly opened?
- Recommended default: `defer_until_queue_opens`
- Queue status: `provider_runtime`
- Evidence that would resolve it: Check canon, glossary, AGENTS.md, current queue, target current docs, and source conversation before any promotion.

### `DECISION-0005`

- Group: `provider/content/packs`
- Question: Should this conversation-derived claim remain archive-only until `provider_runtime` is explicitly opened?
- Recommended default: `defer_until_queue_opens`
- Queue status: `provider_runtime`
- Evidence that would resolve it: Check canon, glossary, AGENTS.md, current queue, target current docs, and source conversation before any promotion.

### `DECISION-0006`

- Group: `world/time/civilization simulation`
- Question: Should this conversation-derived claim become a future review item, remain historical, or be deferred: The assistant formalized this as the Perfect Earth Calendar, later called HPC-E. The final structure is clear, though the exact leap rule remains unresolved.?
- Recommended default: `defer_pending_user_decision`
- Queue status: `not directly blocked by queue keyword match`
- Evidence that would resolve it: Check canon, glossary, AGENTS.md, current queue, target current docs, and source conversation before any promotion.

### `DECISION-0007`

- Group: `architecture/boundaries`
- Question: What disposition should be chosen for this unresolved claim: Before relying on this chat as project authority, a future assistant or human reviewer must confirm whether Dominium is actually intended to be simulation-heavy, whether strict...?
- Recommended default: `defer_pending_user_decision`
- Queue status: `not directly blocked by queue keyword match`
- Evidence that would resolve it: Check canon, glossary, AGENTS.md, current queue, target current docs, and source conversation before any promotion.

### `DECISION-0008`

- Group: `renderer/UI/platform`
- Question: Should this conversation-derived claim become a future review item, remain historical, or be deferred: The key thing to remember: this chat produced the standards and prompts for future work; it did not verify or change the project. The next assistant must inspect the actual repo...?
- Recommended default: `defer_pending_user_decision`
- Queue status: `not directly blocked by queue keyword match`
- Evidence that would resolve it: Check canon, glossary, AGENTS.md, current queue, target current docs, and source conversation before any promotion.

### `DECISION-0009`

- Group: `architecture/boundaries`
- Question: What disposition should be chosen for this unresolved claim: This chat was about preserving and re-grounding Dominium's architecture around a very old constitutional contract, then checking whether the current GitHub repository still foll...?
- Recommended default: `defer_pending_user_decision`
- Queue status: `not directly blocked by queue keyword match`
- Evidence that would resolve it: Check canon, glossary, AGENTS.md, current queue, target current docs, and source conversation before any promotion.

### `DECISION-0010`

- Group: `architecture/boundaries`
- Question: Should this conversation-derived claim remain archive-only until `provider_runtime` is explicitly opened?
- Recommended default: `defer_until_queue_opens`
- Queue status: `provider_runtime`
- Evidence that would resolve it: Check canon, glossary, AGENTS.md, current queue, target current docs, and source conversation before any promotion.

### `DECISION-0011`

- Group: `Workbench/AIDE/Codex/tooling`
- Question: Should this conversation-derived claim remain archive-only until `provider_runtime` is explicitly opened?
- Recommended default: `defer_until_queue_opens`
- Queue status: `provider_runtime`
- Evidence that would resolve it: Check canon, glossary, AGENTS.md, current queue, target current docs, and source conversation before any promotion.

### `DECISION-0012`

- Group: `Workbench/AIDE/Codex/tooling`
- Question: Should this conversation-derived claim remain archive-only until `native_gui` is explicitly opened?
- Recommended default: `defer_until_queue_opens`
- Queue status: `native_gui`
- Evidence that would resolve it: Check canon, glossary, AGENTS.md, current queue, target current docs, and source conversation before any promotion.

### `DECISION-0013`

- Group: `Workbench/AIDE/Codex/tooling`
- Question: Should this conversation-derived claim remain archive-only until `provider_runtime` is explicitly opened?
- Recommended default: `defer_until_queue_opens`
- Queue status: `provider_runtime`
- Evidence that would resolve it: Check canon, glossary, AGENTS.md, current queue, target current docs, and source conversation before any promotion.

### `DECISION-0014`

- Group: `architecture/boundaries`
- Question: Should this conversation-derived claim remain archive-only until `provider_runtime` is explicitly opened?
- Recommended default: `defer_until_queue_opens`
- Queue status: `provider_runtime`
- Evidence that would resolve it: Check canon, glossary, AGENTS.md, current queue, target current docs, and source conversation before any promotion.

### `DECISION-0015`

- Group: `architecture/boundaries`
- Question: Should this conversation-derived claim remain archive-only until `provider_runtime` is explicitly opened?
- Recommended default: `defer_until_queue_opens`
- Queue status: `provider_runtime`
- Evidence that would resolve it: Check canon, glossary, AGENTS.md, current queue, target current docs, and source conversation before any promotion.

### `DECISION-0016`

- Group: `release/setup/launcher`
- Question: Should this conversation-derived claim become a future review item, remain historical, or be deferred: Someone reading this report should understand one central thing: this chat is not about inventing new launcher features anymore. It is about preserving boundaries, making the la...?
- Recommended default: `defer_pending_user_decision`
- Queue status: `not directly blocked by queue keyword match`
- Evidence that would resolve it: Check canon, glossary, AGENTS.md, current queue, target current docs, and source conversation before any promotion.

### `DECISION-0017`

- Group: `provider/content/packs`
- Question: Should this conversation-derived claim become a future review item, remain historical, or be deferred: The actual repo was not inspected. The exact accepted directory structure, API policy, DDAP profile, compatibility promises, and first pilot module remain unresolved.?
- Recommended default: `defer_pending_user_decision`
- Queue status: `not directly blocked by queue keyword match`
- Evidence that would resolve it: Check canon, glossary, AGENTS.md, current queue, target current docs, and source conversation before any promotion.

### `DECISION-0018`

- Group: `architecture/boundaries`
- Question: What disposition should be chosen for this unresolved claim: The user then asked whether the implementation was industry-accepted and what could be improved. The response framed the approach as closer to game engines, operating systems, a...?
- Recommended default: `defer_pending_user_decision`
- Queue status: `not directly blocked by queue keyword match`
- Evidence that would resolve it: Check canon, glossary, AGENTS.md, current queue, target current docs, and source conversation before any promotion.

### `DECISION-0019`

- Group: `architecture/boundaries`
- Question: Should this conversation-derived claim remain archive-only until `gameplay` is explicitly opened?
- Recommended default: `defer_until_queue_opens`
- Queue status: `gameplay`
- Evidence that would resolve it: Check canon, glossary, AGENTS.md, current queue, target current docs, and source conversation before any promotion.

### `DECISION-0020`

- Group: `Workbench/AIDE/Codex/tooling`
- Question: What disposition should be chosen for this unresolved claim: The most important thing to remember is that this chat was a planning and prompt-generation chat, not proof of implementation. **UNCERTAIN / UNVERIFIED:** No generated prompt is...?
- Recommended default: `defer_pending_user_decision`
- Queue status: `not directly blocked by queue keyword match`
- Evidence that would resolve it: Check canon, glossary, AGENTS.md, current queue, target current docs, and source conversation before any promotion.

### `DECISION-0021`

- Group: `Workbench/AIDE/Codex/tooling`
- Question: Should this conversation-derived claim become a future review item, remain historical, or be deferred: The user uploaded screenshot bundles for setup and launcher. **UNCERTAIN / UNVERIFIED:** The screenshots were not inspected in this chat. The assistant still produced a logical...?
- Recommended default: `defer_pending_user_decision`
- Queue status: `not directly blocked by queue keyword match`
- Evidence that would resolve it: Check canon, glossary, AGENTS.md, current queue, target current docs, and source conversation before any promotion.

### `DECISION-0022`

- Group: `world/time/civilization simulation`
- Question: Should this conversation-derived claim become a future review item, remain historical, or be deferred: A major theme was that useful local inventions must become portable, standardized, industrialized, and institutionally adopted. The repo now has a Formalization Chain spec and P...?
- Recommended default: `defer_pending_user_decision`
- Queue status: `not directly blocked by queue keyword match`
- Evidence that would resolve it: Check canon, glossary, AGENTS.md, current queue, target current docs, and source conversation before any promotion.

### `DECISION-0023`

- Group: `Workbench/AIDE/Codex/tooling`
- Question: Should `broad_workbench_ui` remain blocked for all conversation-derived work until a future reviewed queue phase opens it?
- Recommended default: `keep_blocked`
- Queue status: `broad_workbench_ui: BLOCKED`
- Evidence that would resolve it: Review current queue, blocked-scope alignment, and any target prompt before changing disposition.

### `DECISION-0024`

- Group: `architecture/boundaries`
- Question: Should `gameplay` remain blocked for all conversation-derived work until a future reviewed queue phase opens it?
- Recommended default: `keep_blocked`
- Queue status: `gameplay: BLOCKED`
- Evidence that would resolve it: Review current queue, blocked-scope alignment, and any target prompt before changing disposition.

### `DECISION-0025`

- Group: `renderer/UI/platform`
- Question: Should `native_gui` remain blocked for all conversation-derived work until a future reviewed queue phase opens it?
- Recommended default: `keep_blocked`
- Queue status: `native_gui: BLOCKED`
- Evidence that would resolve it: Review current queue, blocked-scope alignment, and any target prompt before changing disposition.

### `DECISION-0026`

- Group: `provider/content/packs`
- Question: Should `package_runtime` remain blocked for all conversation-derived work until a future reviewed queue phase opens it?
- Recommended default: `keep_blocked`
- Queue status: `package_runtime: BLOCKED`
- Evidence that would resolve it: Review current queue, blocked-scope alignment, and any target prompt before changing disposition.

### `DECISION-0027`

- Group: `provider/content/packs`
- Question: Should `provider_runtime` remain blocked for all conversation-derived work until a future reviewed queue phase opens it?
- Recommended default: `keep_blocked`
- Queue status: `provider_runtime: BLOCKED`
- Evidence that would resolve it: Review current queue, blocked-scope alignment, and any target prompt before changing disposition.

### `DECISION-0028`

- Group: `release/setup/launcher`
- Question: Should `release_publication` remain blocked for all conversation-derived work until a future reviewed queue phase opens it?
- Recommended default: `keep_blocked`
- Queue status: `release_publication: BLOCKED`
- Evidence that would resolve it: Review current queue, blocked-scope alignment, and any target prompt before changing disposition.

### `DECISION-0029`

- Group: `renderer/UI/platform`
- Question: Should `renderer_implementation` remain blocked for all conversation-derived work until a future reviewed queue phase opens it?
- Recommended default: `keep_blocked`
- Queue status: `renderer_implementation: BLOCKED`
- Evidence that would resolve it: Review current queue, blocked-scope alignment, and any target prompt before changing disposition.

### `DECISION-0030`

- Group: `provider/content/packs`
- Question: Should `runtime_module_loader` remain blocked for all conversation-derived work until a future reviewed queue phase opens it?
- Recommended default: `keep_blocked`
- Queue status: `runtime_module_loader: BLOCKED`
- Evidence that would resolve it: Review current queue, blocked-scope alignment, and any target prompt before changing disposition.
