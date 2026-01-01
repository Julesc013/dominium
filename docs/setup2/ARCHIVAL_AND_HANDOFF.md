# Setup2 Archival and Handoff

This document defines how to archive Setup2 artifacts for long-term reproducibility and
how to handoff installs between operators/launchers without loss of auditability.

## Archival Package (Required)
Archive these artifacts together for any release or support case:
- `install_manifest.tlv`
- `install_request.tlv` (quick and custom as used)
- `install_plan.tlv`
- `installed_state.tlv`
- `setup_audit.tlv`
- `job_journal.tlv` and `txn_journal.tlv`
- payload artifacts referenced by the manifest (exact bytes)
- `SCHEMA_FREEZE_V1.md` and schema hash
- toolchain/build metadata (build preset, compiler, version)

All archived files must be byte-identical to the originals. Do not rewrite, normalize,
or reserialize TLVs.

## Reproducing an Install from Archive
1) Verify schema hash matches `docs/setup2/SCHEMA_FREEZE_V1.md`.
2) Verify payload digests match the archived manifest.
3) Run `dominium-setup2 plan --manifest <manifest> --request <request> --out-plan <plan>`.
4) Run `dominium-setup2 apply --plan <plan> --out-state <state> --out-audit <audit> --out-journal <journal>`.
5) Compare resulting `installed_state.tlv` and `setup_audit.tlv` to the archived versions.

Use `--deterministic 1` and fake services when possible to reproduce byte-identical
artifacts in a sandbox.

## Auditing an Old Install
- Validate state: `dominium-setup2 verify --state <installed_state.tlv>`
- Dump state: `dominium-setup2 state dump --in <installed_state.tlv> --out state.json --format json`
- Dump audit: `dominium-setup2 audit dump --in <setup_audit.tlv> --out audit.json --format json`
- Explain refusal: `dominium-setup2 explain-refusal --audit <setup_audit.tlv>`

## Migration and Forward Compatibility
- Setup2 may auto-migrate installed_state forward only. Backward migration is not automatic.
- If legacy state exists, use `dominium-setup2 import-legacy-state --in <legacy_state> --out <installed_state> --out-audit <audit>`.
- Preserve the original legacy state alongside the imported Setup2 state for audit trails.

## Handoff Between Operators/Launchers
- Always transfer the full archival package listed above.
- The launcher must read Setup2 `installed_state.tlv` first, and only fall back to legacy import if missing.
- Do not attempt to reconstruct missing artifacts from live installs; use archived TLVs.
