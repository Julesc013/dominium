Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# PROC8 Retro-Consistency Audit

Status: AUDIT
Last Updated: 2026-03-07
Scope: Software/firmware pipeline modeling through PROC process discipline.

## Existing Build/Packaging/Signing Surfaces

Observed related deterministic infrastructure:

- COMPILE process path exists:
  - `process.compile_request_submit`
  - `src/meta/compile/compile_engine.py`
  - `tools/xstack/sessionx/process_runtime.py`
- Existing process lifecycle and quality/QC frameworks exist:
  - `src/process/process_run_engine.py`
  - `src/process/qc/qc_engine.py`
  - `src/process/capsules/*`
  - `src/process/drift/*`
- SIG transport/receipt pathways are available in runtime for deterministic artifact distribution.

## Existing Signing Logic

No dedicated software package signing process path exists yet in PROC runtime. Existing credential/certificate patterns are present in SYS/SIG, but software signing is not modeled as a first-class process step.

## Magic Compile / Bypass Audit

No explicit `process.software_pipeline_*` process handlers were present.

Risk surfaces identified:

1. Direct binary/package artifact writes outside process handlers.
2. Deploy paths that do not require signature artifacts.
3. Build shortcuts bypassing COMPILE proof/equivalence artifacts.
4. Test/QC subset evaluation happening ad hoc instead of deterministic policy-driven pathways.

## Migration Plan (PROC-8)

1. Add software pipeline schemas and registries:
   - software pipeline profile
   - software artifacts
   - deployment records
   - toolchain and template registries
2. Add deterministic software pipeline engine under `src/process/software/`.
3. Wire runtime process handler:
   - `process.software_pipeline_execute`
   - compile/test/package/sign/deploy sequence
   - proof hash chain refresh
4. Add explain and inspection section coverage for pipeline failures/status.
5. Add replay tool and TestX coverage for deterministic pipeline behavior and signature gating.
6. Add RepoX/AuditX enforcement:
   - no magic build
   - signing required
   - deploy through SIG.
