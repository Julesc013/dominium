Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Retro Consistency Audit Framework

Status: Canonical (ARCH-REF-1)
Version: 1.0.0

## Retro Consistency Principle
- New subsystem work must not coexist with overlapping legacy logic.
- Every major subsystem update must:
  1. Identify overlapping code and data contracts.
  2. Migrate/unify overlapping behavior into existing core abstractions.
  3. Add mechanical enforcement preventing reintroduction.

## Mandatory Prompt Structure
All future major subsystem prompts must include:

`PHASE 0 — Retro-Consistency Audit`
- overlap detection
- schema conflicts
- process duplication
- state duplication
- policy conflicts
- ledger bypass risk
- nondeterminism risk
- migration plan

## Replacement Over Addition Rule
- Additions that duplicate existing abstractions are forbidden.
- Migration/unification must occur before introducing new subsystem logic.

## No Silent Bypass Rule
- Any bypass path (including admin/meta-law) must:
  - emit a ledger exception entry
  - be recorded in run-meta
  - remain replayable via deterministic logs

## Deterministic Drift Prevention
- Refactors must preserve:
  - deterministic hash anchors
  - replay equivalence
  - ledger totals and conservation accounting
- If equivalence cannot be proven, change must refuse merge under strict lanes.

## Tooling Boundary
- Enforcement runs in RepoX/AuditX/TestX and documentation workflow only.
- Framework logic must not add runtime production cost or runtime behavior branches.
