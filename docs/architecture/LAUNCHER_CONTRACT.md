# Launcher Contract (DIST2)

Status: binding.
Scope: launcher behavior and third-party launcher support.

## Required behavior
- Launchers manipulate `data/` only, never binaries.
- Preflight checks must refuse explicitly on missing capabilities.
- Launchers must support `--data-root` relocation.
- Third-party launchers are supported by contract.

## Refusal paths
- Missing packs or lockfiles -> explicit refusal or frozen mode.
- Invalid data root -> explicit refusal.

## See also
- `docs/arch/DISTRIBUTION_LAYOUT.md`
- `docs/arch/LOCKFILES.md`
