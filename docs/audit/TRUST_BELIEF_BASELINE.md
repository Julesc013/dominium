# TRUST_BELIEF_BASELINE

Status: BASELINE  
Last Updated: 2026-03-03  
Scope: SIG-5 deterministic trust graph and belief dynamics.

## 1) Trust Graph Model

- Added canonical SIG-5 schemas:
  - `schema/signals/trust_edge.schema`
  - `schema/signals/trust_graph.schema`
  - `schema/signals/belief_policy.schema`
  - `schema/signals/verification_result.schema`
- Added policy registries:
  - `data/registries/belief_policy_registry.json`
  - `data/registries/trust_update_rule_registry.json`
- Added deterministic trust engine:
  - `src/signals/trust/trust_engine.py`
  - `src/signals/trust/__init__.py`

Core behavior:
- Directed edge trust (`from_subject_id -> to_subject_id`) with bounded weight `[0,1]`.
- Deterministic update rule application (`update.linear_adjust`, `update.simple_bayesian_stub`).
- Deterministic decay tick via policy.

## 2) Acceptance Rules

Receipt creation now applies belief policy acceptance:
- `process_signal_transport_tick` derives receipt trust from trust edge `(recipient -> sender)`.
- `process_knowledge_acquire` writes acceptance metadata:
  - `extensions.accepted`
  - `extensions.acceptance_threshold`
  - `extensions.belief_policy_id`
  - `extensions.confidence_tag`

Support for authenticated trust boost is policy-driven and deterministic through belief policy extensions.

## 3) Verification Processes

Added deterministic verification process:
- `process_message_verify_claim`

Behavior:
- Produces `verification_result` rows.
- Uses explicit evidence/certificates (or entitlement-gated observer path).
- Calls `process_trust_update` when sender attribution exists.
- Emits deterministic decision log entries for both verify-claim and trust-update paths.

## 4) Propagation Integration

Aggregation policies now support trust-informed propagation:
- `acceptance_mode: accepted_only` to filter inputs to accepted artifacts.
- `acceptance_mode: include_all` / `include_all_with_confidence` with confidence tags in summaries.
- Optional `receipt_subject_id` for subject-scoped acceptance filtering.

Implementation:
- `src/signals/aggregation/aggregation_engine.py`

## 5) UX and Inspection

Added inspection sections:
- `section.trust.edges_summary`
- `section.inbox.acceptance_summary`

Integrated in:
- `data/registries/inspection_section_registry.json`
- `src/inspection/inspection_engine.py`

These sections expose coarse trust/acceptance summaries by default and richer detail with hidden-state entitlement.

## 6) Enforcement

RepoX additions:
- `INV-NO-OMNISCIENT-TRUST-UPDATES`
- `INV-VERIFICATION-PROCESS-ONLY`

AuditX additions:
- `E172_TRUTH_BASED_TRUST_SMELL` (`TruthBasedTrustSmell`)
- `E173_UNLOGGED_TRUST_CHANGE_SMELL` (`UnloggedTrustChangeSmell`)

## 7) TestX Coverage (SIG-5)

Added and passing:
1. `testx.signals.trust_update_deterministic`
2. `testx.signals.receipt_weighted_by_trust`
3. `testx.signals.acceptance_threshold`
4. `testx.signals.verification_updates_trust`
5. `testx.signals.decay_tick_deterministic`

## 8) Gate Results (2026-03-03)

1. RepoX
- Command: `python tools/xstack/repox/check.py --repo-root . --profile FAST`
- Result: `status=pass` (warnings present, including topology declarations and pre-existing repository warnings)

2. AuditX
- Command: `python tools/xstack/auditx/check.py --repo-root . --profile FAST`
- Result: `status=pass` (repository warning findings remain)

3. TestX (SIG-5 subset)
- Command: `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset testx.signals.trust_update_deterministic,testx.signals.receipt_weighted_by_trust,testx.signals.acceptance_threshold,testx.signals.verification_updates_trust,testx.signals.decay_tick_deterministic`
- Result: `status=pass` (5 selected, 5 passed)

4. strict build
- Command: `python tools/xstack/run.py --repo-root . --skip-testx strict`
- Result: `status=refusal` due existing strict-lane failures outside SIG-5 scope (including CompatX findings and packaging lab-build refusal)

5. topology map update
- Command: `python tools/governance/tool_topology_generate.py --repo-root . --out-json docs/audit/TOPOLOGY_MAP.json --out-md docs/audit/TOPOLOGY_MAP.md`
- Result: `complete` (`node_count=2623`, `edge_count=150139`, fingerprint `8326e9d67782e344458d8075b74152f14a3d7ffb75c8ec1fba90e63093f75623`)

## 9) Extension Notes

- SIG-6 institutional legitimacy can consume trust edges and verification history directly.
- MIL/ECO misinformation campaigns can layer on accepted/untrusted receipt metadata without bypassing SIG transport or trust process paths.
- Domain-specific trust contexts should extend via `extensions` and registry policy, not bespoke runtime branches.
