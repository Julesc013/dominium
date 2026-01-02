# Setup SPLAT Registry (SR-3)

## Registry ordering
- IDs are sorted lexicographically (bytewise) when listed and selected.

## Deprecated IDs
- `splat_dos`
- `splat_macos_classic`
- `splat_win16_win3x`
- `splat_win32_9x`

## Removed IDs
- `splat_win32_nt4`
- `splat_macos_ppc`

## SPLAT entries
### splat_dos
- supported_platform_triples: `dos`
- supported_scopes: `portable`
- supported_ui_modes: `cli`
- supports_atomic_swap: `no`
- supports_resume: `no`
- supports_pkg_ownership: `no`
- supports_portable_ownership: `yes`
- supports_actions: none
- default_root_convention: `portable`
- elevation_required: `never`
- rollback_semantics: `none`
- is_deprecated: `yes`

### splat_linux_deb
- supported_platform_triples: `linux_deb`
- supported_scopes: `system`
- supported_ui_modes: `tui`, `cli`
- supports_atomic_swap: `no`
- supports_resume: `no`
- supports_pkg_ownership: `yes`
- supports_portable_ownership: `no`
- supports_actions: `pkgmgr_hooks`
- default_root_convention: `linux_prefix`
- elevation_required: `always`
- rollback_semantics: `partial`
- is_deprecated: `no`

### splat_linux_portable
- supported_platform_triples: `linux_portable`
- supported_scopes: `portable`
- supported_ui_modes: `tui`, `cli`
- supports_atomic_swap: `yes`
- supports_resume: `yes`
- supports_pkg_ownership: `no`
- supports_portable_ownership: `yes`
- supports_actions: none
- default_root_convention: `portable`
- elevation_required: `never`
- rollback_semantics: `full`
- is_deprecated: `no`

### splat_linux_rpm
- supported_platform_triples: `linux_rpm`
- supported_scopes: `system`
- supported_ui_modes: `tui`, `cli`
- supports_atomic_swap: `no`
- supports_resume: `no`
- supports_pkg_ownership: `yes`
- supports_portable_ownership: `no`
- supports_actions: `pkgmgr_hooks`
- default_root_convention: `linux_prefix`
- elevation_required: `always`
- rollback_semantics: `partial`
- is_deprecated: `no`

### splat_macos_classic
- supported_platform_triples: `macos_classic`
- supported_scopes: `system`
- supported_ui_modes: `gui`
- supports_atomic_swap: `no`
- supports_resume: `no`
- supports_pkg_ownership: `no`
- supports_portable_ownership: `no`
- supports_actions: none
- default_root_convention: `macos_applications`
- elevation_required: `never`
- rollback_semantics: `none`
- is_deprecated: `yes`

### splat_macos_pkg
- supported_platform_triples: `macos_pkg`
- supported_scopes: `system`
- supported_ui_modes: `gui`, `cli`
- supports_atomic_swap: `no`
- supports_resume: `no`
- supports_pkg_ownership: `yes`
- supports_portable_ownership: `no`
- supports_actions: `codesign_hooks`, `shortcuts`
- default_root_convention: `macos_applications`
- elevation_required: `always`
- rollback_semantics: `partial`
- is_deprecated: `no`

### splat_portable
- supported_platform_triples: `*`
- supported_scopes: `portable`
- supported_ui_modes: `gui`, `tui`, `cli`
- supports_atomic_swap: `yes`
- supports_resume: `yes`
- supports_pkg_ownership: `no`
- supports_portable_ownership: `yes`
- supports_actions: none
- default_root_convention: `portable`
- elevation_required: `never`
- rollback_semantics: `full`
- is_deprecated: `no`

### splat_steam
- supported_platform_triples: `steam`
- supported_scopes: `user`
- supported_ui_modes: `gui`, `cli`
- supports_atomic_swap: `no`
- supports_resume: `no`
- supports_pkg_ownership: `no`
- supports_portable_ownership: `no`
- supports_actions: `steam_hooks`
- default_root_convention: `steam_library`
- elevation_required: `never`
- rollback_semantics: `partial`
- is_deprecated: `no`

### splat_win16_win3x
- supported_platform_triples: `win16_win3x`
- supported_scopes: `portable`
- supported_ui_modes: `cli`
- supports_atomic_swap: `no`
- supports_resume: `no`
- supports_pkg_ownership: `no`
- supports_portable_ownership: `yes`
- supports_actions: none
- default_root_convention: `windows_program_files`
- elevation_required: `never`
- rollback_semantics: `none`
- is_deprecated: `yes`

### splat_win32_9x
- supported_platform_triples: `win32_9x`
- supported_scopes: `user`, `system`
- supported_ui_modes: `gui`, `cli`
- supports_atomic_swap: `no`
- supports_resume: `no`
- supports_pkg_ownership: `no`
- supports_portable_ownership: `no`
- supports_actions: `shortcuts`
- default_root_convention: `windows_program_files`
- elevation_required: `never`
- rollback_semantics: `none`
- is_deprecated: `yes`

### splat_win32_nt5
- supported_platform_triples: `win32_nt5`
- supported_scopes: `user`, `system`
- supported_ui_modes: `gui`, `tui`, `cli`
- supports_atomic_swap: `no`
- supports_resume: `no`
- supports_pkg_ownership: `no`
- supports_portable_ownership: `no`
- supports_actions: `shortcuts`, `file_assoc`, `url_handlers`
- default_root_convention: `windows_program_files`
- elevation_required: `optional`
- rollback_semantics: `partial`
- is_deprecated: `no`
