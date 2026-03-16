Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# PROC7 Retro-Consistency Audit

Status: AUDIT
Last Updated: 2026-03-06
Scope: PROC-7 research, experimentation, and reverse engineering discipline.

## Existing Experiment-Like Actions

Observed deterministic experiment-adjacent pathways:

- `process.formalization_infer`
- `process.formalization_accept_candidate`
- `process.spec_check_compliance`
- `process.pollution_measure`

These pathways already produce artifacts and deterministic records, but they are not unified under process research semantics (`experiment_definition`, `experiment_result`, `candidate_process_definition`, `reverse_engineering_record`).

## Existing Discovery Mechanisms

Current discovery/inference capabilities are scoped to formalization/network workflows and do not expose process-specific candidate promotion gates:

- inference candidates exist for formalization/networking domains
- no process-level replication-gated promotion from candidate to `process_definition`
- no dedicated reverse-engineering canonical record for destructive disassembly/assay/scan

## Magic Unlock Audit

No dedicated PROC-7 “magic unlock” process flag was found. Existing unlock/maturity checks are governed by PROC-4/PROC-6 state transitions and records.

Risk surfaces to guard in PROC-7:

- direct writes to promoted process definitions without replication/QC checks
- candidate creation pathways that bypass derived-artifact generation
- reverse-engineering actions granting global knowledge without receipts

## Migration Plan

1. Add explicit research schemas and policy registry.
2. Add deterministic experiment and inference engines (`src/process/research/*`).
3. Add canonical promotion and reverse-engineering process handlers in runtime.
4. Add epistemic receipts + SIG report publication hooks for experiment results.
5. Enforce with RepoX/AuditX (`INV-NO-MAGIC-UNLOCKS-RESEARCH`, `INV-CANDIDATE-DERIVED-ONLY`, `INV-PROMOTION-REQUIRES-REPLICATION`).
