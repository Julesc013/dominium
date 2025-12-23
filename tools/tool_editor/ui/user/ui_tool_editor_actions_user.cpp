/* User action stubs. */
#include "ui_tool_editor_actions_user.h"
#include "tool_editor_actions.h"

static void tool_editor_fill_value_u32(const domui_value* v, unsigned int* out_u32)
{
    if (!v || !out_u32) {
        return;
    }
    switch (v->type) {
    case DOMUI_VALUE_U32:
        *out_u32 = v->u.v_u32;
        break;
    case DOMUI_VALUE_I32:
        *out_u32 = (unsigned int)v->u.v_i32;
        break;
    case DOMUI_VALUE_BOOL:
        *out_u32 = v->u.v_bool ? 1u : 0u;
        break;
    default:
        break;
    }
}

static void tool_editor_fill_text(const domui_value* v, ToolEditorEvent* out)
{
    if (!v || !out) {
        return;
    }
    if (v->type == DOMUI_VALUE_STR) {
        out->text = v->u.v_str.ptr;
        out->text_len = v->u.v_str.len;
        out->has_text = 1;
    }
}

static const ToolEditorEvent* tool_editor_make_event(const domui_event* e, ToolEditorEvent* out)
{
    if (!e || !out) {
        return 0;
    }
    tool_editor_fill_value_u32(&e->a, &out->value_u32);
    tool_editor_fill_value_u32(&e->b, &out->value_u32_b);
    tool_editor_fill_text(&e->a, out);
    return out;
}

static void tool_editor_dispatch(void* user_ctx, ToolEditorAction action, const domui_event* e)
{
    ToolEditorEvent ev;
    const ToolEditorEvent* ev_ptr = tool_editor_make_event(e, &ev);
    tool_editor_handle_action(user_ctx, action, ev_ptr);
}

// BEGIN AUTO-GENERATED ACTION STUBS
void ui_tool_editor_act_TOOL_EDITOR_QUIT(void* user_ctx, const domui_event* e)
{
    tool_editor_dispatch(user_ctx, TOOL_EDITOR_ACTION_QUIT, e);
}

void ui_tool_editor_act_TOOL_EDITOR_ADD_WIDGET(void* user_ctx, const domui_event* e)
{
    tool_editor_dispatch(user_ctx, TOOL_EDITOR_ACTION_ADD_WIDGET, e);
}

void ui_tool_editor_act_TOOL_EDITOR_DELETE_WIDGET(void* user_ctx, const domui_event* e)
{
    tool_editor_dispatch(user_ctx, TOOL_EDITOR_ACTION_DELETE_WIDGET, e);
}

void ui_tool_editor_act_TOOL_EDITOR_HIERARCHY_SELECT(void* user_ctx, const domui_event* e)
{
    tool_editor_dispatch(user_ctx, TOOL_EDITOR_ACTION_HIER_SELECT, e);
}

void ui_tool_editor_act_TOOL_EDITOR_NEW(void* user_ctx, const domui_event* e)
{
    tool_editor_dispatch(user_ctx, TOOL_EDITOR_ACTION_NEW, e);
}

void ui_tool_editor_act_TOOL_EDITOR_OPEN(void* user_ctx, const domui_event* e)
{
    tool_editor_dispatch(user_ctx, TOOL_EDITOR_ACTION_OPEN, e);
}

void ui_tool_editor_act_TOOL_EDITOR_PROP_H(void* user_ctx, const domui_event* e)
{
    tool_editor_dispatch(user_ctx, TOOL_EDITOR_ACTION_PROP_H, e);
}

void ui_tool_editor_act_TOOL_EDITOR_PROP_NAME(void* user_ctx, const domui_event* e)
{
    tool_editor_dispatch(user_ctx, TOOL_EDITOR_ACTION_PROP_NAME, e);
}

void ui_tool_editor_act_TOOL_EDITOR_PROP_W(void* user_ctx, const domui_event* e)
{
    tool_editor_dispatch(user_ctx, TOOL_EDITOR_ACTION_PROP_W, e);
}

void ui_tool_editor_act_TOOL_EDITOR_PROP_X(void* user_ctx, const domui_event* e)
{
    tool_editor_dispatch(user_ctx, TOOL_EDITOR_ACTION_PROP_X, e);
}

void ui_tool_editor_act_TOOL_EDITOR_PROP_Y(void* user_ctx, const domui_event* e)
{
    tool_editor_dispatch(user_ctx, TOOL_EDITOR_ACTION_PROP_Y, e);
}

void ui_tool_editor_act_TOOL_EDITOR_SAVE(void* user_ctx, const domui_event* e)
{
    tool_editor_dispatch(user_ctx, TOOL_EDITOR_ACTION_SAVE, e);
}

void ui_tool_editor_act_TOOL_EDITOR_SAVE_AS(void* user_ctx, const domui_event* e)
{
    tool_editor_dispatch(user_ctx, TOOL_EDITOR_ACTION_SAVE_AS, e);
}

void ui_tool_editor_act_TOOL_EDITOR_TAB_CHANGE(void* user_ctx, const domui_event* e)
{
    tool_editor_dispatch(user_ctx, TOOL_EDITOR_ACTION_TAB_CHANGE, e);
}

void ui_tool_editor_act_TOOL_EDITOR_VALIDATE(void* user_ctx, const domui_event* e)
{
    tool_editor_dispatch(user_ctx, TOOL_EDITOR_ACTION_VALIDATE, e);
}

// END AUTO-GENERATED ACTION STUBS
