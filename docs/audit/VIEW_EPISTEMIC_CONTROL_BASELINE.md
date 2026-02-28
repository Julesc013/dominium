# CTRL-6 View & Epistemic Control Baseline

Status: Baseline generated for CTRL-6 (view + epistemic unification).
Date: 2026-03-01

## 1) View Policies

Source registry: `data/registries/view_policy_registry.json`

- `view.first_person_diegetic`
- `view.third_person_diegetic`
- `view.spectator_limited`
- `view.freecam_lab`
- `view.observer_truth`
- `view.replay`

All view changes are expected to route through `action.view.change_policy -> process.view_bind` and resolve under control policy + server/law constraints.

## 2) Epistemic Policies

Source registry: `data/registries/epistemic_policy_registry.json`

CTRL-6 canonical policy IDs integrated:

- `epistemic.diegetic_default`
- `epistemic.admin_full`
- `epistemic.rank_restricted`
- `epistemic.replay_readonly`

Legacy-compatible rows remain present and are resolved via compat aliases/extensions where required by existing content.

## 3) Downgrade Rules

Deterministic downgrade ordering remains centralized through negotiation kernel axis order:

1. abstraction
2. view
3. epistemic
4. fidelity
5. budget

View downgrade behavior (ranked + policy constraints):

- `freecam -> third_person -> first_person` when allowed set forbids requested freecam.
- If no legal fallback exists, refusal is emitted.
- Downgrade reasons include:
  - `downgrade.policy_disallows`
  - `downgrade.rank_fairness`

All downgrade/refusal outcomes are logged via DecisionLog; no silent downgrade path is intended.

## 4) Replay Constraints

Replay policy guard in control plane enforces read-only behavior.

Allowed replay-safe controls:

- `action.view.change`
- `action.view.change_policy`
- `action.replay.*`
- `action.fidelity.request`

Mutation attempts in replay are refused with:

- `refusal.ctrl.replay_mutation_forbidden`

## 5) Migration Summary

Implemented CTRL-6 migration outcomes:

- Camera/view binding introduced through deterministic `view_engine` (`process.view_bind`).
- Legacy camera process IDs are adapter-routed via control-plane/runtime path to `process.view_bind`.
- Epistemic gating resolution is bound to active `view_binding` + epistemic policy registry.
- Inspection, reenactment, and interior instrumentation outputs apply epistemic caps/redaction from resolved policy.
- Replay mutation hard-stop enforced at control-plane resolution.
- RepoX and AuditX enforcement added for camera bypass and renderer-truth boundaries.

## 6) Gate Results

Executed gate commands:

- `python tools/xstack/repox/check.py --profile STRICT`
- `python tools/xstack/auditx/check.py --profile STRICT`
- `python tools/xstack/testx/runner.py --profile STRICT --subset test_view_negotiation_deterministic,test_freecam_forbidden_in_ranked,test_replay_cannot_mutate_truth,test_epistemic_redaction_in_view,test_camera_binding_deterministic,testx.view.camera_bind_replay_determinism,testx.view.ranked_profile_forbids_free_view,testx.view.requires_embodiment_refusal,testx.materials.epistemic_redaction_applied,testx.materials.epistemic_gating_of_reenactment_detail`
- `python tools/xstack/run.py strict`
- `python tools/governance/tool_topology_generate.py --repo-root . --out-json docs/audit/TOPOLOGY_MAP.json --out-md docs/audit/TOPOLOGY_MAP.md`

Observed outcomes:

- RepoX STRICT: `fail` (current blockers not introduced by CTRL-6 changes):
  - `repox.reserved_word_flag_misuse` at `tools/xstack/sessionx/process_runtime.py:647`
  - audit-risk threshold warning in `docs/audit/auditx/FINDINGS.json`
- AuditX STRICT: `pass` (scan completed; findings emitted)
- TestX CTRL-6 subset: `pass` (10/10 selected tests)
- Strict profile (`tools/xstack/run.py strict`): `refusal` due pre-existing broader workspace gate failures (CompatX/TestX/Packaging/RepoX), not isolated to CTRL-6 deltas.
- Topology map: regenerated successfully (`docs/audit/TOPOLOGY_MAP.json`, `docs/audit/TOPOLOGY_MAP.md`).

