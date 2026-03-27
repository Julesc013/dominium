Status: DERIVED
Last Reviewed: 2026-03-28
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: XI-5A
Replacement Target: bounded preflight archive repair record

# XI-5a Preflight Archive Fix

## Root Cause

The committed offline archive verify and baseline artifacts were stale relative to the current deterministic archive contents. The drift was triggered by the archived support surface `data/regression/ecosystem_verify_baseline.json`, which changed the archive projection, record, and bundle hashes.

## Exact Repair

Regenerated the bounded offline archive verification surfaces from the current deterministic archive behavior:

- `data/audit/offline_archive_verify.json`
- `docs/audit/OFFLINE_ARCHIVE_VERIFY.md`
- `data/regression/archive_baseline.json`
- `docs/audit/OFFLINE_ARCHIVE_BASELINE.md`

Then reran `validate --all FAST`, which regenerated:

- `data/audit/validation_report_FAST.json`
- `docs/audit/VALIDATION_REPORT_FAST.md`

## Before / After

- Before: `FAST = refused`
- After: `FAST = complete`

## Scope Guard

- No Xi-5a moves were executed.
- No runtime code or contracts changed.
- No archive verifier rules were weakened.
- No broad archive redesign was performed.
