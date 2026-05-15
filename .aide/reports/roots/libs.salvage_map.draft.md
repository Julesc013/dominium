# libs Draft Salvage Map

## Status: Draft / Not Approved

- Apply allowed: `false`
- Approval status: `not_approved`
- Entry count: 108

## Recommended Fates

- `convert`: 5
- `preserve_unknown`: 103

## Candidate Future Target Locations

No target paths are approved. Future targets must be selected by an approved move plan.

## High-Risk Files

- `libs/CMakeLists.txt`
- `libs/appcore/CMakeLists.txt`
- `libs/appcore/command/command_dispatch.c`
- `libs/appcore/command/command_registry.c`
- `libs/appcore/command/command_registry.h`
- `libs/appcore/discover/appcore_discover.c`
- `libs/appcore/discover/appcore_discover.h`
- `libs/appcore/invoke/appcore_invoke.c`
- `libs/appcore/invoke/appcore_invoke.h`
- `libs/appcore/output/appcore_output.c`
- `libs/appcore/output/appcore_output.h`
- `libs/appcore/profile/appcore_profile.c`
- `libs/appcore/profile/appcore_profile.h`
- `libs/appcore/repox/appcore_repox.c`
- `libs/appcore/repox/appcore_repox.h`
- `libs/appcore/ui_bind/ui_accessibility_map.c`
- `libs/appcore/ui_bind/ui_accessibility_map.h`
- `libs/appcore/ui_bind/ui_command_binding_table.c`
- `libs/appcore/ui_bind/ui_command_binding_table.h`
- `libs/appcore/ui_bind/ui_localisation_usage_report.json`
- `libs/appcore/validate/appcore_validate.c`
- `libs/appcore/validate/appcore_validate.h`
- `libs/build_identity/build_identity.c`
- `libs/build_identity/CMakeLists.txt`
- `libs/build_identity/include/dom_build_identity/build_identity.h`

## preserve_unknown Files

- `libs/appcore`
- `libs/appcore/command`
- `libs/appcore/command/command_dispatch.c`
- `libs/appcore/command/command_registry.c`
- `libs/appcore/command/command_registry.h`
- `libs/appcore/discover`
- `libs/appcore/discover/appcore_discover.c`
- `libs/appcore/discover/appcore_discover.h`
- `libs/appcore/invoke`
- `libs/appcore/invoke/appcore_invoke.c`
- `libs/appcore/invoke/appcore_invoke.h`
- `libs/appcore/output`
- `libs/appcore/output/appcore_output.c`
- `libs/appcore/output/appcore_output.h`
- `libs/appcore/profile`
- `libs/appcore/profile/appcore_profile.c`
- `libs/appcore/profile/appcore_profile.h`
- `libs/appcore/repox`
- `libs/appcore/repox/appcore_repox.c`
- `libs/appcore/repox/appcore_repox.h`
- `libs/appcore/ui_bind`
- `libs/appcore/ui_bind/ui_accessibility_map.c`
- `libs/appcore/ui_bind/ui_accessibility_map.h`
- `libs/appcore/ui_bind/ui_command_binding_table.c`
- `libs/appcore/ui_bind/ui_command_binding_table.h`

## References Requiring Future Rewrite

- Raw references recorded: 816

## Validators Required Before Any Move

- AIDE salvage-map check
- repo layout strict validator
- root allowlist strict validator
- distribution/component validators
- docs/build/UI/ABI checks as applicable

## Blockers Before Move

- No approved salvage map.
- No approved move map.
- No reference rewrite plan.
- No rollback evidence packet.
