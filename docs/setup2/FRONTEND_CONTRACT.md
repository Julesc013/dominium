# Setup2 Frontend Contract

Frontends are thin: they emit `install_request.tlv`, call the kernel, and report results.

## Allowed Frontend Responsibilities
- Gather user choices (GUI/TUI/CLI).
- Load and store TLVs.
- Pass service vtables into the kernel.
- Render progress and errors.

## Prohibited Frontend Responsibilities
- No install logic (no planning, resolving, or execution decisions).
- No direct side effects beyond file IO through services.

## Required Request Fields
- `operation`
- `install_scope`
- `ui_mode`
- `target_platform_triple`
- `frontend_id`
- Optional: `requested_splat_id`, component include/exclude lists, policy flags.

## Output Artifacts
- `install_plan.tlv`
- `installed_state.tlv`
- `setup_audit.tlv`
- `job_journal.tlv`
- `txn_journal.tlv`

## Exit Codes
- `0` on success.
- Non-zero values are produced by `dsk_error_to_exit_code`.
- JSON outputs must include `status_code`.

## Determinism
- Default is deterministic (`--deterministic 1`).
- No timestamps or nondeterministic fields in deterministic mode.
- All JSON outputs use stable key ordering.
