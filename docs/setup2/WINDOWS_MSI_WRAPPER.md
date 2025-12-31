# Windows MSI Wrapper (SR-7)

The MSI wrapper is a thin shell. It must not implement install logic. It only collects UI choices and invokes `dominium-setup2`.

## Property Mapping
- `DSK_OPERATION` -> `install_request.operation`
- `DSK_SCOPE` -> `install_request.install_scope`
- `DSK_INSTALL_ROOT` -> `install_request.preferred_install_root`
- `DSK_COMPONENTS` -> `install_request.requested_components` (CSV)
- `DSK_EXCLUDE_COMPONENTS` -> `install_request.excluded_components` (CSV)
- `DSK_FRONTEND_ID` -> `install_request.frontend_id`

## Expected Paths
- `DSK_REQUEST_PATH` -> `install_request.tlv`
- `DSK_PLAN_PATH` -> `install_plan.tlv`
- `DSK_AUDIT_PATH` -> `setup_audit.tlv`
- `DSK_STATE_PATH` -> `installed_state.tlv`
- `DSK_JOURNAL_PATH` -> `job_journal.tlv`

## Custom Action Contract
The custom action must only call `dominium-setup2`:
- `request make`
- `plan`
- `apply`

No registry/filesystem logic is permitted in the MSI action.

## Silent Install Example
```
msiexec /i DominiumSetup2.msi /qn DSK_OPERATION=install DSK_SCOPE=system DSK_INSTALL_ROOT="C:\\Dominium" /l*v setup2_msi.log
```
