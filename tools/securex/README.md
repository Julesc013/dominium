Status: DERIVED
Last Reviewed: 2026-02-11
Supersedes: none
Superseded By: none

# SecureX

SecureX is the trust and integrity validation toolchain.

## Commands

- `python tools/securex/securex.py verify --repo-root .`
- `python tools/securex/securex.py sign-pack --pack-path <pack> --signer-id <id> --key-id <kid> --key-material <secret> --output <sig.json>`
- `python tools/securex/securex.py verify-pack --pack-path <pack> --signature-json <sig.json> --key-material <secret>`
- `python tools/securex/securex.py integrity-manifest --repo-root .`
- `python tools/securex/securex.py boundary-check --repo-root .`
- `python tools/securex/securex.py privilege-check --repo-root .`
- `python tools/securex/securex.py repro-build-check --left <artifact-or-dir> --right <artifact-or-dir>`

## Outputs

- `docs/audit/security/FINDINGS.json` (CANONICAL)
- `docs/audit/security/INTEGRITY_MANIFEST.json` (CANONICAL)
- `docs/audit/security/RUN_META.json` (RUN_META)
