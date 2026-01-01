# Setup2 Reproducible Builds

Setup2 artifacts and outputs are designed to be reproducible when deterministic mode is enabled.

## Deterministic mode
- CLI: `--deterministic 1` (default).
- Policy flag: `DSK_POLICY_DETERMINISTIC`.
- `run_id` is `0` and outputs are byte-identical for identical inputs.

## Build guidance
- Pin compiler and SDK versions.
- Avoid embedding timestamps or build paths in artifacts.
- Use stable archive ordering and fixed metadata.

## Verification
- `ctest -R setup2_conformance`
- `ctest -R setup2_conformance_repeat` (byte-identical artifacts across runs)
