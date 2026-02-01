Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Tools Observability

Tools reuse the read-only adapter and output formatting helpers.

## Inspect
- `tools inspect` opens the read-only adapter and prints core + topology
  summary via `dom_app_ro_print_inspector_bundle`.
- If topology is unsupported, the command fails loudly with a non-zero exit.

## Validate
- `tools validate` runs `dom_app_compat_check` only; no gameplay validation.
- Supports `--format text|json`.

## Replay
- `tools replay` is unsupported in APR4 and exits non-zero.

## Output
- `--format` is accepted only for `inspect` and `validate`.
- JSON output uses stable ordering and explicit field names.