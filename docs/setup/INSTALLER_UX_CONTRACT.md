# Installer UX Contract (Canonical)

This document defines the canonical installer flow across all platforms.
It is authoritative for MSI/EXE, macOS, Linux, ZIP, and legacy installers.
Setup Core is the only install logic authority. Frontends only collect choices and emit a `dsu_invocation`.

## Canonical step order

1. Detect existing install
2. Select operation (install / upgrade / repair / uninstall)
3. Select scope (user / system / portable)
4. Select install root(s)
5. Component selection
6. Summary (choices + digest preview)
7. Execute

Frontends may present steps differently (wizard, expert panel, TUI, CLI prompts),
but they must preserve the logical order and the same required fields.

## Required fields, defaults, and constraints

Required fields:

- `operation`
- `scope`
- `platform_triple`
- `install_roots` (required for install/upgrade; optional for repair/uninstall when state supplies it)
- `selected_components` and `excluded_components` (may be empty)
- `policy_flags`
- `ui_mode` (informational)
- `frontend_id` (informational)

Defaults:

- `operation`: if no installed state is detected, default to `install`; otherwise default to `upgrade`.
- `scope`: if the manifest declares exactly one scope for the target platform, default to that scope; otherwise require explicit selection.
- `install_roots`: if the manifest declares exactly one root for the selected scope and platform, default to that root; otherwise require explicit selection.
- `selected_components` / `excluded_components`: if both are empty, use manifest defaults (`DEFAULT_SELECTED` components plus dependencies).
- `policy_flags`: all false unless explicitly set (deterministic is true by default for Setup Core).
- `policy_flags.enable_shortcuts`, `policy_flags.enable_file_assoc`, `policy_flags.enable_url_handlers` default to false unless explicitly set.

Constraints:

- `operation` must be one of: `install`, `upgrade`, `repair`, `uninstall`.
- `scope` must be one of: `user`, `system`, `portable`.
- `platform_triple` must be non-empty and match the build target.
- `install_roots` must be non-empty for install/upgrade; for repair/uninstall it must match the installed state.
- `selected_components` and `excluded_components` must be disjoint and reference known component IDs.
- `policy_flags.legacy_mode` restricts the operation vocabulary (see `docs/setup/LEGACY_INSTALLER_MODEL.md`).

## Validation rules and failure messages (generic)

Frontends must surface these failures deterministically (exact text may be localized,
but must map to the same error codes):

- Missing or corrupt installed state: `Installed state is missing or corrupt.`
- Unknown operation: `Unsupported operation.`
- Unsupported scope for this package: `Scope is not supported for this package.`
- Install root not allowed for the selected scope/platform: `Install root is not allowed for this scope and platform.`
- Unknown component ID: `Unknown component id.`
- Component listed in both selected and excluded: `Component selection is invalid.`
- Legacy mode rejects the operation: `Legacy mode does not support this operation.`
- Empty resolved set after validation: `No components selected.`

## Mapping: UX fields -> Setup Core invocation

| UX field | `dsu_invocation` field | Notes |
| --- | --- | --- |
| Operation | `operation` | Required |
| Scope | `scope` | Required |
| Platform | `platform_triple` | Required, build target |
| Install root(s) | `install_roots` | Required for install/upgrade |
| Component selection | `selected_components` / `excluded_components` | Optional lists |
| Offline mode | `policy_flags.offline` | Optional |
| Deterministic mode | `policy_flags.deterministic` | Optional; default true |
| Allow prerelease | `policy_flags.allow_prerelease` | Optional |
| Legacy mode | `policy_flags.legacy_mode` | Optional |
| Enable shortcuts | `policy_flags.enable_shortcuts` | Optional |
| Enable file associations | `policy_flags.enable_file_assoc` | Optional |
| Enable URL handlers | `policy_flags.enable_url_handlers` | Optional |
| UI type | `ui_mode` | Informational only |
| Frontend id | `frontend_id` | Informational only |

## Parity rule (locked)

If two frontends produce the same `dsu_invocation` payload, the resulting plan digest
must be identical (modulo declared platform path mappings). No frontend may inject
install logic or reorder decisions beyond canonical validation and normalization.

See also:

- `docs/setup/INVOCATION_PAYLOAD.md`
- `docs/setup/SETUP_CORE_ARCHITECTURE.md`
