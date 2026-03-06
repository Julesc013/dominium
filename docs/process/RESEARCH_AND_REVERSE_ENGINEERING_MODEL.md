# Research And Reverse Engineering Model

Status: AUTHORITATIVE
Last Updated: 2026-03-06
Scope: PROC-7 epistemic research, experimentation, and reverse engineering workflows.

## 1) Experiment

An experiment is a `ProcessDefinition` whose primary outputs are knowledge artifacts rather than production batches.

Required declarations:

- `hypothesis`
- controlled variables and measured variables
- measurement procedures
- expected outcome signatures

Experiment execution remains deterministic process-run lifecycle (`process_run_start`/`process_run_tick`/`process_run_end`) with canonical provenance.

## 2) Candidate Inference

Candidate process artifacts are derived-only outputs:

- `candidate_process_definition`
- `candidate_model_binding`

Inference inputs:

- experiment result artifacts
- reverse engineering records
- measurement artifacts

Inference must be deterministic, conservative under sparse evidence, and explainable with explicit confidence bounds.

## 3) Validation And Promotion

A candidate may be promoted to a real process definition only when all gates pass:

- replication runs >= policy threshold
- QC acceptance from PROC-3 policies
- stabilization/maturity thresholds from PROC-4

Promotion must emit a canonical record and may trigger optional certification request.

## 4) Reverse Engineering

Reverse engineering actions:

- `task.disassemble`
- `task.assay`
- `task.scan`

Default behavior is destructive (`destroyed=true`) unless policy/tool says otherwise.

Outputs:

- measurement artifacts
- inferred candidate artifacts
- canonical `reverse_engineering_record`

## 5) Epistemics And SIG

Knowledge is subject-bound and receipt-gated:

- produced artifacts become known through `knowledge_receipt`
- other subjects learn only via explicit SIG transmission/report receipt

No omniscient direct unlocks are permitted.

## 6) Budgeting And Determinism

Research and inference are budgeted deterministic workloads:

- stable owner/process ordering
- deterministic per-tick caps
- explicit defer logs under budget pressure

Named RNG is allowed only by explicit profile gate and must be proof-logged.
