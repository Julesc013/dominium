/*
FILE: source/dominium/launcher/ui/launcher_ui_session_state.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/ui
RESPONSIBILITY: Defines the dev-only launcher UI session state TLV contract.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers.
FORBIDDEN DEPENDENCIES: OS/UI toolkit headers; launcher core headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes/false; no exceptions.
DETERMINISM: Session state is local-only, not part of determinism.
VERSIONING / ABI / DATA FORMAT NOTES: TLV tags are stable; schema_version=1.
EXTENSION POINTS: Add new TLV tags with new schema version.
*/
#ifndef DOM_LAUNCHER_UI_SESSION_STATE_H
#define DOM_LAUNCHER_UI_SESSION_STATE_H

#include <string>

extern "C" {
#include "domino/core/types.h"
}

namespace dom {

enum LauncherUiSessionStateTag {
    UI_SESSION_TAG_SCHEMA_VERSION = 1u,
    UI_SESSION_TAG_TAB_ID = 10u,
    UI_SESSION_TAG_INSTANCE_ID = 11u,
    UI_SESSION_TAG_PLAY_TARGET_ITEM_ID = 12u,
    UI_SESSION_TAG_WINDOW_X = 20u,
    UI_SESSION_TAG_WINDOW_Y = 21u,
    UI_SESSION_TAG_WINDOW_W = 22u,
    UI_SESSION_TAG_WINDOW_H = 23u
};

struct LauncherUiSessionState {
    u32 schema_version;
    u32 tab_id;
    std::string instance_id;
    u32 play_target_item_id;
    i32 window_x;
    i32 window_y;
    i32 window_w;
    i32 window_h;

    LauncherUiSessionState();
};

std::string launcher_ui_session_state_path();
bool launcher_ui_session_state_load(LauncherUiSessionState& out_state, std::string& out_error);
bool launcher_ui_session_state_save(const LauncherUiSessionState& state, std::string& out_error);

} // namespace dom

#endif /* DOM_LAUNCHER_UI_SESSION_STATE_H */
