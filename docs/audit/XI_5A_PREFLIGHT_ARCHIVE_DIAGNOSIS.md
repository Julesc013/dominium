Status: DERIVED
Last Reviewed: 2026-03-28
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: XI-5A
Replacement Target: bounded preflight archive repair record

# XI-5a Preflight Archive Diagnosis

## Summary

- Diagnosis: `archive baseline is stale relative to current deterministic archive behavior`
- Scope: offline archive arch-audit drift only
- Governing blocking surfaces:
  - `data/audit/offline_archive_verify.json`
  - `data/regression/archive_baseline.json`

## Root Cause

The offline archive arch-audit reruns a fresh deterministic archive build and compares that rerun to the committed archive verify and archive baseline surfaces.

The fresh rerun was deterministic, but it no longer matched the committed archive hashes because the archive bundles the current `data/regression/ecosystem_verify_baseline.json` support surface. That support surface had already changed in the working repository state, so the archived support-surface hash changed and cascaded into:

- archive projection hash
- archive record hash
- archive bundle hash
- offline archive verify fingerprint
- archive baseline fingerprint

## Evidence

- Previously committed archive bundle hash: `c4dc77363650f213a52f68f009fe262dc0889286b3f363e1f52b405345f01e4b`
- Fresh deterministic archive bundle hash: `a0e643963905d97f81079569439ef67734e45afa6f7e4f8c9d1bc12f38bd7fa6`
- Previously committed archive record hash: `3e688ac8f374fe7ee0141597a025899608ee46b1f36a82647089861dd153116a`
- Fresh deterministic archive record hash: `6381c84ca1e2ab6a2a740dd15908492fee70a37280bc1857c86bbe117c74aca9`
- Fresh rerun against the committed baseline refused with:
  - `archive_bundle_hash_mismatch`
  - `archive_record_hash_mismatch`

## Determinism Check

Two consecutive fresh reruns produced the same:

- archive bundle hash: `a0e643963905d97f81079569439ef67734e45afa6f7e4f8c9d1bc12f38bd7fa6`
- archive projection hash: `66bc99a4e5b758b90725290ab223e8d7638bbcbc8399ccf181bac90bdfe63bcd`
- archive record hash: `6381c84ca1e2ab6a2a740dd15908492fee70a37280bc1857c86bbe117c74aca9`
- verify fingerprint: `ed13f424cbd0e77d9f26b5358a6c89425ce11b6e75cee5592f4b96c8a25d763c`

This confirms stale committed archive surfaces, not archive nondeterminism.

## Non-Cause

`docs/audit/ARCHIVE_POLICY_BASELINE.md` is informational for archive policy and was not the governing surface for the failing arch-audit comparison. No archive-policy redesign was required for this repair.
