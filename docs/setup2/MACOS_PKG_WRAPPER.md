# macOS PKG Wrapper (SR-7)

The PKG wrapper installs a minimal payload and invokes `dominium-setup2` in `postinstall`.

## Scripts
- `source/dominium/setup/frontends/adapters/macos_pkg/packaging/postinstall`
  - Generates `install_request.tlv`
  - Builds `install_plan.tlv`
  - Invokes `apply`

Outputs (default):
- `install_request.tlv` and `install_plan.tlv` in `TMPDIR`
- `setup_audit.tlv`, `installed_state.tlv`, `job_journal.tlv` in `TMPDIR`

## Environment Overrides
- `DSK_MANIFEST_PATH`
- `DSK_REQUEST_PATH`
- `DSK_PLAN_PATH`
- `DSK_AUDIT_PATH`
- `DSK_STATE_PATH`
- `DSK_JOURNAL_PATH`
- `DSK_FRONTEND_ID`
- `DSK_DETERMINISTIC`
- `DSK_DRY_RUN=1` (skip side effects)

## Example
```
sudo DSK_DRY_RUN=1 dominium-setup2 apply --plan /tmp/install_plan.tlv --out-audit /tmp/setup_audit.tlv --out-journal /tmp/job_journal.tlv --dry-run
```
