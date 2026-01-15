# Setup2 UI Contract Mapping (SR-7)

This document ties UI controls to `install_request.tlv` fields. Keep IDs stable.

## Request Fields (install_request.tlv)
- operation -> `DSK_TLV_TAG_REQUEST_OPERATION`
- scope -> `DSK_TLV_TAG_REQUEST_INSTALL_SCOPE`
- install_root -> `DSK_TLV_TAG_REQUEST_PREFERRED_INSTALL_ROOT`
- components -> `DSK_TLV_TAG_REQUEST_REQUESTED_COMPONENTS`
- exclude_components -> `DSK_TLV_TAG_REQUEST_EXCLUDED_COMPONENTS`
- ownership -> `DSK_TLV_TAG_REQUEST_OWNERSHIP_PREFERENCE`
- requested_splat -> `DSK_TLV_TAG_REQUEST_REQUESTED_SPLAT_ID`
- platform_triple -> `DSK_TLV_TAG_REQUEST_TARGET_PLATFORM_TRIPLE`
- payload_root -> `DSK_TLV_TAG_REQUEST_PAYLOAD_ROOT`
- options.policy_flags -> `DSK_TLV_TAG_REQUEST_POLICY_FLAGS`
- ui_mode -> `DSK_TLV_TAG_REQUEST_UI_MODE` (set by frontend)
- frontend_id -> `DSK_TLV_TAG_REQUEST_FRONTEND_ID` (set by frontend)

## Windows (VS Resource Editor)
Dialog: `IDD_DSK_SETUP_WIZARD` in `source/dominium/setup/frontends/adapters/windows_exe/dominium_setup_win_exe.rc`

| UI field | Control ID | TLV field | Notes |
| --- | --- | --- | --- |
| operation | `IDC_DSK_OPERATION_COMBO` | `DSK_TLV_TAG_REQUEST_OPERATION` | install/upgrade/repair/uninstall/verify/status |
| scope | `IDC_DSK_SCOPE_COMBO` | `DSK_TLV_TAG_REQUEST_INSTALL_SCOPE` | user/system/portable |
| install_root | `IDC_DSK_INSTALL_ROOT_EDIT` | `DSK_TLV_TAG_REQUEST_PREFERRED_INSTALL_ROOT` | blank = default |
| components | `IDC_DSK_COMPONENTS_EDIT` | `DSK_TLV_TAG_REQUEST_REQUESTED_COMPONENTS` | csv |
| exclude_components | `IDC_DSK_EXCLUDE_EDIT` | `DSK_TLV_TAG_REQUEST_EXCLUDED_COMPONENTS` | csv |
| ownership | `IDC_DSK_OWNERSHIP_COMBO` | `DSK_TLV_TAG_REQUEST_OWNERSHIP_PREFERENCE` | any/portable/pkg/steam |
| requested_splat | `IDC_DSK_REQUESTED_SPLAT_EDIT` | `DSK_TLV_TAG_REQUEST_REQUESTED_SPLAT_ID` | optional |
| platform_triple | `IDC_DSK_PLATFORM_EDIT` | `DSK_TLV_TAG_REQUEST_TARGET_PLATFORM_TRIPLE` | required |
| payload_root | `IDC_DSK_PAYLOAD_ROOT_EDIT` | `DSK_TLV_TAG_REQUEST_PAYLOAD_ROOT` | optional |
| options.deterministic | `IDC_DSK_DETERMINISTIC_CHECK` | `DSK_TLV_TAG_REQUEST_POLICY_FLAGS` | `DSK_POLICY_DETERMINISTIC` |
| options.offline | `IDC_DSK_OFFLINE_CHECK` | `DSK_TLV_TAG_REQUEST_POLICY_FLAGS` | `DSK_POLICY_OFFLINE` (reserved) |

## macOS (Xcode / Storyboard)
Storyboard: `source/dominium/setup/frontends/adapters/macos_pkg/xcode/DominiumSetupMacApp/Resources/Base.lproj/Main.storyboard`

| UI field | Storyboard Identifier | TLV field | Notes |
| --- | --- | --- | --- |
| operation | `operationPopup` | `DSK_TLV_TAG_REQUEST_OPERATION` | popup values match request strings |
| scope | `scopePopup` | `DSK_TLV_TAG_REQUEST_INSTALL_SCOPE` | popup values match request strings |
| install_root | `installRootField` | `DSK_TLV_TAG_REQUEST_PREFERRED_INSTALL_ROOT` | blank = default |
| components | `componentsField` | `DSK_TLV_TAG_REQUEST_REQUESTED_COMPONENTS` | csv |
| exclude_components | `excludeComponentsField` | `DSK_TLV_TAG_REQUEST_EXCLUDED_COMPONENTS` | csv |
| ownership | `ownershipPopup` | `DSK_TLV_TAG_REQUEST_OWNERSHIP_PREFERENCE` | any/portable/pkg/steam |
| requested_splat | `requestedSplatField` | `DSK_TLV_TAG_REQUEST_REQUESTED_SPLAT_ID` | optional |
| platform_triple | `platformField` | `DSK_TLV_TAG_REQUEST_TARGET_PLATFORM_TRIPLE` | required |
| payload_root | `payloadRootField` | `DSK_TLV_TAG_REQUEST_PAYLOAD_ROOT` | optional |
| options.deterministic | `deterministicCheck` | `DSK_TLV_TAG_REQUEST_POLICY_FLAGS` | `DSK_POLICY_DETERMINISTIC` |
| options.offline | `offlineCheck` | `DSK_TLV_TAG_REQUEST_POLICY_FLAGS` | `DSK_POLICY_OFFLINE` (reserved) |

## Linux TUI (Prompt Keys)
File: `source/dominium/setup/frontends/tui/dominium_setup_tui_main.cpp`

| UI field | Prompt key | Prompt text | TLV field |
| --- | --- | --- | --- |
| operation | `tui.operation_choice` | "Select operation" | `DSK_TLV_TAG_REQUEST_OPERATION` |
| components | `tui.components` | "Enter component ids or numbers" | `DSK_TLV_TAG_REQUEST_REQUESTED_COMPONENTS` |
| scope | `tui.scope_choice` | "Select scope" | `DSK_TLV_TAG_REQUEST_INSTALL_SCOPE` |
| install_root | `tui.install_root` | "Install root (blank for default)" | `DSK_TLV_TAG_REQUEST_PREFERRED_INSTALL_ROOT` |
| options.deterministic | `tui.deterministic` | `--deterministic` flag | `DSK_TLV_TAG_REQUEST_POLICY_FLAGS` |

## Validation Rules (Generic)
- Operation required -> "Operation is required."
- Scope required -> "Scope is required."
- Platform triple required -> "Platform triple is required."
- Install root must be a valid path when set -> "Install root must be a valid path."
- Components/exclude must be comma-separated IDs -> "Component lists must be comma-separated."
- Ownership must be one of any/portable/pkg/steam -> "Ownership must be one of any/portable/pkg/steam."
- Requested splat must exist in manifest -> "Requested splat is not allowed by the manifest."
