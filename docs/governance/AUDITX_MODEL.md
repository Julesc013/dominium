Status: DERIVED
Last Reviewed: 2026-02-15
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `docs/canon/constitution_v1.md` and `docs/canon/glossary_v1.md`.
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# AuditX Model

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


## Purpose
AuditX is Dominium's semantic health layer. It complements, but does not replace, structural enforcement and runtime proof systems.

## Responsibility Split
- `RepoX`: structural and policy invariants, enforcement-oriented.
- `TestX`: executable behavior verification and determinism regressions.
- `AuditX`: semantic analysis, drift detection, architecture risk surfacing, and governance promotion candidates.

## Non-Gating Default
- AuditX is non-gating by default.
- AuditX findings never fail a build by themselves unless explicitly promoted into RepoX or TestX.
- `auditx verify` returns success when scan execution succeeds, independent of findings volume/severity.

## Promotion Path
Promotion is explicit and tracked:
1. AuditX finding is emitted and triaged.
2. Repeated/high-confidence findings are promoted to either:
   - RepoX invariant (`INV-*`) for static enforcement, or
   - TestX regression test for behavioral proof.
3. Promotion rationale is recorded in audit artifacts.

## Determinism Contract
- Graph build traversal is deterministic.
- Analyzer execution order is deterministic.
- Finding ordering and fingerprint generation are deterministic.
- JSON report serialization uses stable key ordering.
- Nondeterministic run metadata (timestamps) is isolated and excluded from finding fingerprint computation.

## Changed-Only Behavior
- `auditx scan --changed-only` scopes graph/build/analyzers to changed files.
- If git is unavailable, AuditX returns deterministic refusal:
  - `refusal.git_unavailable`
- Changed-only mode never mutates runtime code and never bypasses deterministic ordering.

## Enforcement Mode Stub
- `auditx enforce` exists as a stub only.
- Default result: deterministic refusal `refusal.not_enabled`.
- Future enforcement promotion must be wired through RepoX/TestX policy, not ad hoc in AuditX.

## Scope Constraints
- AuditX does not mutate runtime semantics.
- AuditX does not auto-fix files.
- AuditX does not introduce simulation primitives.

## Output Contract
Primary output root: `docs/audit/auditx/`
- `FINDINGS.json`
- `FINDINGS.md`
- `SUMMARY.md`
- `INVARIANT_MAP.json`

Optional derived support artifacts may be emitted but must remain deterministic.

## Analyzer Model
- Analyzers are modular plugins over a shared repository analysis graph.
- Minimum baseline analyzers:
  - A1 OrphanedCodeAnalyzer
  - A2 OwnershipBoundaryAnalyzer
  - A3 CanonDriftAnalyzer
  - A4 SchemaUsageAnalyzer
  - A5 CapabilityMisuseAnalyzer
  - A6 UIBypassAnalyzer
  - A7 LegacyContaminationAnalyzer
  - A8 DerivedArtifactFreshnessAnalyzer

## Cross-References
- `docs/governance/REPOX_RULESETS.md`
- `docs/governance/TESTX_ARCHITECTURE.md`
- `docs/testing/xstack_profiles.md`
- `docs/audit/auditx/README.md`
