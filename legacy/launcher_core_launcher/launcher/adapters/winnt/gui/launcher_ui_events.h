/*
FILE: source/dominium/launcher/ui/launcher_ui_events.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/ui
RESPONSIBILITY: Defines stable semantic UI event IDs and value payloads for launcher frontends.
ALLOWED DEPENDENCIES: `include/domino/**` and C89/C++98 standard headers.
FORBIDDEN DEPENDENCIES: OS/UI toolkit headers; launcher core headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: None; POD-only payloads.
DETERMINISM: Event IDs are stable and presentation-only.
VERSIONING / ABI / DATA FORMAT NOTES: Keep numeric IDs stable (schema uses same values).
EXTENSION POINTS: Add new EVT_* entries with unique IDs.
*/
#ifndef DOM_LAUNCHER_UI_EVENTS_H
#define DOM_LAUNCHER_UI_EVENTS_H

extern "C" {
#include "domino/core/types.h"
}

namespace dom {

/* UI schema action IDs (scripts/gen_launcher_ui_schema_v1.py). */
enum LauncherUiEventId {
    EVT_TAB_PLAY = 100,
    EVT_TAB_INSTANCES = 101,
    EVT_TAB_PACKS = 102,
    EVT_TAB_OPTIONS = 103,
    EVT_TAB_LOGS = 104,

    EVT_PLAY = 200,
    EVT_SAFE_MODE = 201,
    EVT_VERIFY = 202,

    EVT_INST_CREATE = 300,
    EVT_INST_CLONE = 301,
    EVT_INST_DELETE = 302,
    EVT_INST_IMPORT = 303,
    EVT_INST_EXPORT_DEF = 304,
    EVT_INST_EXPORT_BUNDLE = 305,
    EVT_INST_MARK_KG = 306,

    EVT_PACKS_APPLY = 400,

    EVT_OPT_RESET = 500,
    EVT_OPT_DETAILS = 501,

    EVT_LOGS_DIAG = 600,

    EVT_DIALOG_OK = 900,
    EVT_DIALOG_CANCEL = 901
};

/* Value types mirror DUI value types for compatibility. */
enum LauncherUiValueType {
    UI_VALUE_NONE = 0,
    UI_VALUE_BOOL = 1,
    UI_VALUE_U32  = 2,
    UI_VALUE_I32  = 3,
    UI_VALUE_U64  = 4,
    UI_VALUE_TEXT = 5,
    UI_VALUE_LIST = 6
};

struct LauncherUiValueEvent {
    u32 widget_id;
    u32 value_type;
    u32 v_u32;
    i32 v_i32;
    u64 v_u64;
    const char* text;
    u32 text_len;
    u32 item_id;

    LauncherUiValueEvent()
        : widget_id(0u),
          value_type(0u),
          v_u32(0u),
          v_i32(0),
          v_u64(0u),
          text(0),
          text_len(0u),
          item_id(0u) {}
};

} // namespace dom

#endif /* DOM_LAUNCHER_UI_EVENTS_H */
