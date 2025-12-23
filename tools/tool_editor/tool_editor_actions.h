/*
FILE: tools/tool_editor/tool_editor_actions.h
MODULE: Dominium tools
RESPONSIBILITY: Shared action IDs + dispatch hook for Tool Editor actions.
*/
#ifndef DOMINIUM_TOOL_EDITOR_ACTIONS_H_INCLUDED
#define DOMINIUM_TOOL_EDITOR_ACTIONS_H_INCLUDED

enum ToolEditorAction {
    TOOL_EDITOR_ACTION_QUIT = 0,
    TOOL_EDITOR_ACTION_NEW,
    TOOL_EDITOR_ACTION_OPEN,
    TOOL_EDITOR_ACTION_SAVE,
    TOOL_EDITOR_ACTION_SAVE_AS,
    TOOL_EDITOR_ACTION_VALIDATE,
    TOOL_EDITOR_ACTION_TAB_CHANGE,
    TOOL_EDITOR_ACTION_HIER_SELECT,
    TOOL_EDITOR_ACTION_PROP_NAME,
    TOOL_EDITOR_ACTION_PROP_X,
    TOOL_EDITOR_ACTION_PROP_Y,
    TOOL_EDITOR_ACTION_PROP_W,
    TOOL_EDITOR_ACTION_PROP_H,
    TOOL_EDITOR_ACTION_ADD_WIDGET,
    TOOL_EDITOR_ACTION_DELETE_WIDGET
};

struct ToolEditorEvent {
    unsigned int value_u32;
    unsigned int value_u32_b;
    const char* text;
    unsigned int text_len;
    int has_text;

    ToolEditorEvent()
        : value_u32(0u),
          value_u32_b(0u),
          text(0),
          text_len(0u),
          has_text(0)
    {
    }
};

void tool_editor_handle_action(void* user_ctx, ToolEditorAction action, const ToolEditorEvent* e);

#endif /* DOMINIUM_TOOL_EDITOR_ACTIONS_H_INCLUDED */
