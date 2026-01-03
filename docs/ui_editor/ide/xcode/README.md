# Xcode Pre-build Script (UI Preview)

Add a Run Script phase to `dominium-ui-preview-host-macos` with a command like:

```sh
set -e

ROOT_DIR="${SRCROOT}"
UI_DOC="${ROOT_DIR}/tools/launcher/ui/doc/launcher_ui_doc.tlv"
UI_ROOT="${ROOT_DIR}/tools/launcher/ui"

# Adjust UI_EDITOR to your local tool path if needed.
UI_EDITOR="${BUILD_DIR}/Debug/tool_ui_editor"
if [ ! -x "${UI_EDITOR}" ]; then
  UI_EDITOR="${ROOT_DIR}/build/macos-xcode/Debug/tool_ui_editor"
fi

"${UI_EDITOR}" --headless-build-ui --in "${UI_DOC}" --docname launcher_ui --out-root "${UI_ROOT}"
```

This mirrors the `ui_preview_launcher_macos` target and keeps the UI doc/codegen
in sync before running the preview host.
