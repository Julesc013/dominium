# Research & Reverse Engineering Baseline

Status: BASELINE  
Last Updated: 2026-03-06  
Scope: PROC-7 deterministic experiment execution, candidate inference, promotion gates, destructive reverse engineering, epistemic diffusion, proof/replay, enforcement, and TestX coverage.

## 1) Experiment Workflow

Implemented in:

- `src/process/research/experiment_engine.py`
- `tools/xstack/sessionx/process_runtime.py` (`process.experiment_run_start`, `process.experiment_run_complete`)

Behavior:

- Experiments are explicit process runs with deterministic experiment bindings.
- Completion emits deterministic `experiment_result` artifacts from measurement rows.
- Experiment completion links run/process/version and updates deterministic research hash chains:
  - `experiment_result_hash_chain`
  - `experiment_run_binding_hash_chain`
  - `candidate_process_hash_chain`
  - `candidate_model_binding_hash_chain`

Epistemics:

- Experiment result artifacts issue subject-bound knowledge receipts.
- Optional SIG publication is explicit and policy-gated (`publish_report_via_sig`).

## 2) Candidate Inference

Implemented in:

- `src/process/research/inference_engine.py`

Behavior:

- Candidate artifacts are derived-only and deterministic from experiment/reverse evidence.
- Deterministic ordering:
  - evidence rows sorted by stable IDs
  - candidate IDs and bindings produced by canonical hashes
- Confidence is conservative and evidence-driven.

Artifacts:

- `candidate_process_definition_rows` (derived)
- `candidate_model_binding_rows` (derived)

Budgeting:

- Inference jobs are budgeted by policy (`max_inference_jobs_per_tick`) and can be deferred with logged decisions.

## 3) Promotion Criteria

Implemented in:

- `tools/xstack/sessionx/process_runtime.py` (`process.candidate_promote_to_defined`)
- `src/process/research/inference_engine.py` (`evaluate_candidate_promotion`)

Promotion requires deterministic thresholds:

- replication count >= required threshold (policy default or explicit input)
- QC pass rate >= threshold
- stabilization score >= threshold

On success:

- canonical promotion record emitted (`candidate_promotion_record_rows`)
- promoted process definition materialized (versioned)
- optional certification request report can be emitted

On failure:

- explicit refusal (`refusal.process.candidate.promotion_denied`)

## 4) Reverse Engineering & Epistemic Diffusion

Implemented in:

- `tools/xstack/sessionx/process_runtime.py` (`process.reverse_engineering_action`)

Behavior:

- Reverse methods: `disassemble`, `assay`, `scan`
- Destructive behavior is policy-controlled (`allow_destructive_reverse_engineering`)
- Canonical reverse records emitted:
  - `reverse_engineering_record_rows`
- Subject receives deterministic knowledge receipts for produced observation artifacts.

SIG diffusion:

- Experiment results are emitted as REPORT artifacts and can be distributed via channel transport.
- No omniscient unlock path is introduced; knowledge remains receipt-bound unless shared.

## 5) Proof & Replay

Replay tools:

- `tools/process/tool_replay_experiment_window.py`
- `tools/process/tool_replay_reverse_engineering_window.py`

Verified hash-chain surfaces:

- experiment replay:
  - `experiment_result_hash_chain`
  - `experiment_run_binding_hash_chain`
  - `candidate_process_hash_chain`
  - `candidate_model_binding_hash_chain`
- reverse replay:
  - `reverse_engineering_record_hash_chain`
  - `candidate_process_hash_chain`
  - `candidate_model_binding_hash_chain`
  - `candidate_promotion_hash_chain`

## 6) TestX Coverage (PROC-7)

Added/passing tests:

- `test_experiment_result_deterministic`
- `test_candidate_inference_deterministic`
- `test_promotion_requires_replication`
- `test_reverse_engineering_destroys_when_policy`
- `test_replay_research_hash_match`

Command:

- `python tools/xstack/testx_all.py --profile FAST --subset test_experiment_result_deterministic,test_candidate_inference_deterministic,test_promotion_requires_replication,test_reverse_engineering_destroys_when_policy,test_replay_research_hash_match`
- status: `pass` (`selected_tests=5`)

## 7) Gate Status Snapshot

Topology map update:

- command: `python tools/governance/tool_topology_generate.py --repo-root . --out-json docs/audit/TOPOLOGY_MAP.json --out-md docs/audit/TOPOLOGY_MAP.md`
- status: `complete`
- deterministic_fingerprint: `475dc80ce716e53efb2ecfa5111bdbd6d49cf3199d27d8bb9fa15ef34166cd43`

RepoX STRICT:

- command: `python tools/xstack/repox/check.py --repo-root . --profile STRICT`
- status: `refusal` (`findings=37`)
- blockers include pre-existing/global governance findings (RWAM declarations, topology declarations, existing promoted hard-fail mappings, worktree hygiene).

AuditX STRICT:

- command: `python tools/xstack/auditx/check.py --repo-root . --profile STRICT`
- status: `fail` (`promoted_blockers=3`)
- promoted blockers observed include pre-existing/global smells (`E240`, `E285`, `E293`).

Strict build:

- command: `python tools/xstack/run.py strict --repo-root . --cache on`
- status: `refusal` (exit_code `2`)
- failed/refused stages include `compatx`, `repox`, `auditx`, `testx`, and `packaging.verify` from global repository state.

## 8) Readiness for PROC-8 (Software/Firmware Pipelines)

- [x] Deterministic experiment lifecycle integrated with process runtime
- [x] Derived-only candidate inference with conservative confidence
- [x] Deterministic promotion gates enforce replication evidence
- [x] Destructive reverse engineering is explicit and policy-gated
- [x] Proof/replay windows cover experiment and reverse-engineering chains
- [ ] Repository-wide strict gates globally green (blocked by pre-existing/global findings outside PROC-7 delta)

