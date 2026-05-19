Status: DERIVED
Last Reviewed: 2026-02-27
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to MAT-9 constitutional scope and canon.
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# MAT-9 Inspection System Baseline

## Request/Response Schemas
- `inspection_request`
  - requester, target kind/id, desired fidelity, tick/time range, max budget.
- `inspection_snapshot`
  - deterministic derived snapshot with achieved fidelity, hash anchors, inputs hash, sections, and fingerprint.
- `inspection_section`
  - bounded typed section payload with epistemic redaction marker.

## Section Registry
`inspection_section_registry` defines canonical section IDs:
- `section.material_stocks`
- `section.batches_summary`
- `section.flow_summary`
- `section.ag_progress`
- `section.maintenance_backlog`
- `section.failure_risk_summary`
- `section.commitments_summary`
- `section.events_summary`
- `section.reenactment_link`
- `section.micro_parts_summary`

## Caching Behavior
- Snapshot generation is derived-only and cache-backed.
- Cache identity uses deterministic input anchors and epistemic/fidelity parameters.
- Repeat queries for same inputs reuse cached snapshot hash.

## Degradation Rules
- Deterministic degrade order: `micro -> meso -> macro`.
- If strict budget is enabled and macro cannot be produced, request is refused.
- Non-strict mode returns best permitted lower fidelity.

## Epistemic Integration
- Law + authority + epistemic policy gates detail.
- Diegetic views are quantized/coarse and redact hidden micro identities.
- Lab/admin may access full details when law permits.

## Causality and History Integration
- Snapshot sections include commitment/event summaries.
- History queries use event stream indices and optional reenactment references.
- Inspection remains derived and never mutates canonical truth.

## Performance and Arbitration
- Section-level deterministic cost accounting.
- Budget enforcement supports deterministic degradation/refusal.
- Cache reuse prevents recomputation thrash under repeated inspections.

## MAT-10 Extension Points
- Cross-target multi-hop inspection bundles.
- Higher-density history timelines with deterministic pagination.
- Stress-path scheduling metrics and shard-aware inspection arbitration.

## Gate Snapshot (2026-02-27)
1. RepoX PASS
   - command: `py -3 tools/xstack/repox/check.py --repo-root . --profile STRICT`
   - result: `status=pass`, findings=0
2. AuditX run
   - command: `py -3 tools/xstack/auditx/check.py --repo-root . --profile STRICT`
   - result: `status=pass`, findings=950 (warn-level findings)
3. TestX PASS (MAT-9 required subset + guard presence)
   - command: `py -3 tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset testx.materials.inspection_snapshot_deterministic,testx.materials.cache_reuse_same_anchor,testx.materials.degrade_micro_to_meso_under_budget,testx.materials.epistemic_redaction_applied,testx.materials.history_query_deterministic,testx.materials.multiplayer_inspection_fairness,testx.materials.guardrail_declarations_present`
   - result: `status=pass`, selected_tests=7
4. strict build PASS
   - command: `cmake --build out/build/vs2026/verify --config Debug --target domino_engine dominium_game dominium_client`
   - result: build completed successfully
5. ui_bind --check PASS
   - command: `py -3 tools/xstack/ui_bind.py --repo-root . --check`
   - result: `result=complete`, checked_windows=21
