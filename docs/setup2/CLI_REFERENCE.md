# Setup2 CLI Reference (SR-4)

Executable: `dominium-setup2`

## Commands
- `validate-manifest --in <file>`
- `validate-request --in <file>`
- `dump-splats --json`
- `select-splat --manifest <file> --request <file> [--json]`
- `plan --manifest <file> --request <file> --out-plan <file> [--json]`
- `dump-plan --plan <file> [--json]`
- `resolve --manifest <file> --request <file> [--json]`
- `run --manifest <file> --request <file> --out-state <file> --out-audit <file> [--out-plan <file>] [--out-log <file>] [--json]`

## Options
- `--use-fake-services <sandbox_root>`: use fake services backend rooted at `sandbox_root`.

## Examples
- `dominium-setup2 validate-manifest --in manifest.tlv`
- `dominium-setup2 plan --manifest manifest.tlv --request request.tlv --out-plan plan.tlv --json`
- `dominium-setup2 resolve --manifest manifest.tlv --request request.tlv --json`
- `dominium-setup2 dump-plan --plan plan.tlv --json`
