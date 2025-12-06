#include "dom_input_mapping.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#include "core/dom_core_types.h"
#include "platform/dom_keys.h"
#include "platform/win32/dom_platform_win32.h"

#ifndef DOM_INPUT_LOG_BINDINGS
#define DOM_INPUT_LOG_BINDINGS 1
#endif

#define DOM_INPUT_MAX_BINDINGS_PER_CONTEXT 128
#define DOM_INPUT_MAX_TOKEN 64
#define DOM_INPUT_MOD_CTRL  (1u << 0)
#define DOM_INPUT_MOD_SHIFT (1u << 1)
#define DOM_INPUT_MOD_ALT   (1u << 2)

typedef enum dom_input_binding_type_e {
    DOM_INPUT_BINDING_KEY = 0,
    DOM_INPUT_BINDING_MOUSE_BUTTON,
    DOM_INPUT_BINDING_MOUSE_WHEEL
} dom_input_binding_type;

typedef struct DomInputBinding {
    dom_input_action action;
    dom_input_binding_type type;
    int keycode;
    int mouse_button;
    int wheel_direction;
    unsigned modifiers;
} DomInputBinding;

typedef struct DomInputContextBindings {
    DomInputBinding bindings[DOM_INPUT_MAX_BINDINGS_PER_CONTEXT];
    int binding_count;
} DomInputContextBindings;

static DomInputContextBindings g_contexts[DOM_INPUT_CONTEXT_COUNT];
static unsigned g_active_context_mask = 0;
static dom_bool8 g_action_triggered[ACTION_COUNT];
static int g_action_down_refcount[ACTION_COUNT];
static dom_bool8 g_prev_key_down[DOM_KEYCODE_MAX];
static dom_bool8 g_key_is_down[DOM_KEYCODE_MAX];
static dom_bool8 g_prev_mouse_down[3];

typedef struct dom_input_action_map_s {
    const char *name;
    dom_input_action action;
} dom_input_action_map;

static const dom_input_action_map g_action_names[] = {
    { "ACTION_HELP_OVERLAY", ACTION_HELP_OVERLAY },
    { "ACTION_SCREENSHOT_CAPTURE", ACTION_SCREENSHOT_CAPTURE },
    { "ACTION_DEBUG_OVERLAY_CYCLE", ACTION_DEBUG_OVERLAY_CYCLE },
    { "ACTION_VIEW_DIMENSION_TOGGLE", ACTION_VIEW_DIMENSION_TOGGLE },
    { "ACTION_VIEW_RENDER_MODE_CYCLE", ACTION_VIEW_RENDER_MODE_CYCLE },
    { "ACTION_QUICK_SAVE", ACTION_QUICK_SAVE },
    { "ACTION_QUICK_LOAD", ACTION_QUICK_LOAD },
    { "ACTION_REPLAY_PANEL", ACTION_REPLAY_PANEL },
    { "ACTION_TOOLS_PANEL", ACTION_TOOLS_PANEL },
    { "ACTION_WORLD_MAP", ACTION_WORLD_MAP },
    { "ACTION_SETTINGS_MENU", ACTION_SETTINGS_MENU },
    { "ACTION_FULLSCREEN_TOGGLE", ACTION_FULLSCREEN_TOGGLE },
    { "ACTION_DEV_CONSOLE", ACTION_DEV_CONSOLE },
    { "ACTION_MOVE_FORWARD", ACTION_MOVE_FORWARD },
    { "ACTION_MOVE_BACKWARD", ACTION_MOVE_BACKWARD },
    { "ACTION_MOVE_LEFT", ACTION_MOVE_LEFT },
    { "ACTION_MOVE_RIGHT", ACTION_MOVE_RIGHT },
    { "ACTION_CAMERA_ROTATE_CCW", ACTION_CAMERA_ROTATE_CCW },
    { "ACTION_CAMERA_ROTATE_CW", ACTION_CAMERA_ROTATE_CW },
    { "ACTION_CAMERA_ALT_UP", ACTION_CAMERA_ALT_UP },
    { "ACTION_CAMERA_ALT_DOWN", ACTION_CAMERA_ALT_DOWN },
    { "ACTION_PRIMARY_SELECT", ACTION_PRIMARY_SELECT },
    { "ACTION_SECONDARY_SELECT", ACTION_SECONDARY_SELECT },
    { "ACTION_UI_BACK", ACTION_UI_BACK },
    { "ACTION_LAYER_CYCLE", ACTION_LAYER_CYCLE },
    { "ACTION_QUICKBAR_SLOT_1", ACTION_QUICKBAR_SLOT_1 },
    { "ACTION_QUICKBAR_SLOT_2", ACTION_QUICKBAR_SLOT_2 },
    { "ACTION_QUICKBAR_SLOT_3", ACTION_QUICKBAR_SLOT_3 },
    { "ACTION_QUICKBAR_SLOT_4", ACTION_QUICKBAR_SLOT_4 },
    { "ACTION_QUICKBAR_SLOT_5", ACTION_QUICKBAR_SLOT_5 },
    { "ACTION_QUICKBAR_SLOT_6", ACTION_QUICKBAR_SLOT_6 },
    { "ACTION_QUICKBAR_SLOT_7", ACTION_QUICKBAR_SLOT_7 },
    { "ACTION_QUICKBAR_SLOT_8", ACTION_QUICKBAR_SLOT_8 },
    { "ACTION_QUICKBAR_SLOT_9", ACTION_QUICKBAR_SLOT_9 },
    { "ACTION_PROFILER_OVERLAY", ACTION_PROFILER_OVERLAY },
    { "ACTION_HIGHLIGHT_INTERACTIVES", ACTION_HIGHLIGHT_INTERACTIVES }
};

static const char *g_context_names[DOM_INPUT_CONTEXT_COUNT] = {
    "global",
    "gameplay",
    "ui",
    "map",
    "editor",
    "launcher"
};

static int dom_input_toupper(int c)
{
    if (c >= 'a' && c <= 'z') {
        return c - ('a' - 'A');
    }
    return c;
}

static int dom_input_stricmp(const char *a, const char *b)
{
    int da;
    int db;
    while (a && b) {
        da = dom_input_toupper((unsigned char)*a);
        db = dom_input_toupper((unsigned char)*b);
        if (da != db || da == 0) {
            return da - db;
        }
        ++a;
        ++b;
    }
    return 0;
}

static void dom_input_reset_state(void)
{
    memset(g_contexts, 0, sizeof(g_contexts));
    memset(g_action_triggered, 0, sizeof(g_action_triggered));
    memset(g_action_down_refcount, 0, sizeof(g_action_down_refcount));
    memset(g_prev_key_down, 0, sizeof(g_prev_key_down));
    memset(g_key_is_down, 0, sizeof(g_key_is_down));
    memset(g_prev_mouse_down, 0, sizeof(g_prev_mouse_down));
    g_active_context_mask = (1u << DOM_INPUT_CONTEXT_GLOBAL)
                          | (1u << DOM_INPUT_CONTEXT_GAMEPLAY)
                          | (1u << DOM_INPUT_CONTEXT_UI);
}

static dom_input_action dom_input_action_from_name(const char *name)
{
    size_t i;
    if (!name) {
        return ACTION_NONE;
    }
    for (i = 0; i < sizeof(g_action_names) / sizeof(g_action_names[0]); ++i) {
        if (dom_input_stricmp(g_action_names[i].name, name) == 0) {
            return g_action_names[i].action;
        }
    }
    return ACTION_NONE;
}

static const char *dom_input_action_name(dom_input_action action)
{
    size_t i;
    for (i = 0; i < sizeof(g_action_names) / sizeof(g_action_names[0]); ++i) {
        if (g_action_names[i].action == action) {
            return g_action_names[i].name;
        }
    }
    return "ACTION_UNKNOWN";
}

static void dom_input_add_binding(int ctx, const DomInputBinding *binding)
{
    DomInputContextBindings *c;
    if (!binding) return;
    if (ctx < 0 || ctx >= (int)DOM_INPUT_CONTEXT_COUNT) {
        return;
    }
    c = &g_contexts[ctx];
    if (c->binding_count >= DOM_INPUT_MAX_BINDINGS_PER_CONTEXT) {
        return;
    }
    c->bindings[c->binding_count++] = *binding;
}

static int dom_input_keycode_from_token(const char *token)
{
    if (!token) return DOM_KEY_UNKNOWN;
    if (strlen(token) == 1) {
        char c = (char)dom_input_toupper((unsigned char)token[0]);
        if (c >= 'A' && c <= 'Z') return DOM_KEY_A + (c - 'A');
        if (c >= '0' && c <= '9') return DOM_KEY_0 + (c - '0');
    }
    if (dom_input_stricmp(token, "ESC") == 0 || dom_input_stricmp(token, "ESCAPE") == 0) return DOM_KEY_ESCAPE;
    if (dom_input_stricmp(token, "TAB") == 0) return DOM_KEY_TAB;
    if (dom_input_stricmp(token, "SPACE") == 0) return DOM_KEY_SPACE;
    if (token[0] == 'F' || token[0] == 'f') {
        int num = atoi(token + 1);
        if (num >= 1 && num <= 12) {
            return DOM_KEY_F1 + (num - 1);
        }
    }
    if (dom_input_stricmp(token, "UP") == 0) return DOM_KEY_UP;
    if (dom_input_stricmp(token, "DOWN") == 0) return DOM_KEY_DOWN;
    if (dom_input_stricmp(token, "LEFT") == 0) return DOM_KEY_LEFT;
    if (dom_input_stricmp(token, "RIGHT") == 0) return DOM_KEY_RIGHT;
    return DOM_KEY_UNKNOWN;
}

static int dom_input_parse_mouse_button(const char *token)
{
    if (!token) return -1;
    if (dom_input_stricmp(token, "MOUSE_LEFT") == 0 || dom_input_stricmp(token, "MOUSEBUTTON_LEFT") == 0) return DOM_INPUT_MOUSE_LEFT;
    if (dom_input_stricmp(token, "MOUSE_RIGHT") == 0 || dom_input_stricmp(token, "MOUSEBUTTON_RIGHT") == 0) return DOM_INPUT_MOUSE_RIGHT;
    if (dom_input_stricmp(token, "MOUSE_MIDDLE") == 0 || dom_input_stricmp(token, "MOUSEBUTTON_MIDDLE") == 0) return DOM_INPUT_MOUSE_MIDDLE;
    return -1;
}

static int dom_input_parse_key_string(const char *str, int *out_keycode, unsigned *out_mods)
{
    char buf[DOM_INPUT_MAX_TOKEN];
    char token[DOM_INPUT_MAX_TOKEN];
    int len;
    int pos;
    int tok_start;
    int tok_len;
    int have_main = 0;
    unsigned mods = 0;
    int keycode = DOM_KEY_UNKNOWN;

    if (!str || !out_keycode || !out_mods) {
        return 0;
    }
    len = (int)strlen(str);
    if (len >= (int)sizeof(buf)) {
        len = (int)sizeof(buf) - 1;
    }
    memcpy(buf, str, (size_t)len);
    buf[len] = '\0';

    pos = 0;
    while (pos <= len) {
        tok_start = pos;
        while (pos <= len && buf[pos] != '+' && buf[pos] != '\0') {
            pos++;
        }
        tok_len = pos - tok_start;
        if (tok_len > 0 && tok_len < (int)sizeof(token)) {
            memcpy(token, buf + tok_start, (size_t)tok_len);
            token[tok_len] = '\0';
            if (dom_input_stricmp(token, "CTRL") == 0 || dom_input_stricmp(token, "CONTROL") == 0) {
                mods |= DOM_INPUT_MOD_CTRL;
            } else if (dom_input_stricmp(token, "SHIFT") == 0) {
                mods |= DOM_INPUT_MOD_SHIFT;
            } else if (dom_input_stricmp(token, "ALT") == 0) {
                mods |= DOM_INPUT_MOD_ALT;
                if (!have_main && (pos >= len || buf[pos] == '\0')) {
                    keycode = DOM_KEY_ALT;
                    have_main = 1;
                }
            } else {
                keycode = dom_input_keycode_from_token(token);
                have_main = 1;
            }
        }
        if (pos >= len) break;
        pos++; /* skip '+' */
    }

    if (!have_main && (mods & DOM_INPUT_MOD_CTRL)) {
        keycode = DOM_KEY_CONTROL;
        have_main = 1;
        mods &= ~DOM_INPUT_MOD_CTRL;
    } else if (!have_main && (mods & DOM_INPUT_MOD_SHIFT)) {
        keycode = DOM_KEY_SHIFT;
        have_main = 1;
        mods &= ~DOM_INPUT_MOD_SHIFT;
    }

    if (!have_main || keycode == DOM_KEY_UNKNOWN) {
        return 0;
    }

    *out_keycode = keycode;
    *out_mods = mods;
    return 1;
}

static const char *dom_input_find_in_range(const char *start, const char *end, const char *needle)
{
    const char *p;
    size_t len;
    size_t remaining;
    if (!start || !end || !needle) return NULL;
    len = strlen(needle);
    remaining = (size_t)(end - start);
    if (len == 0 || remaining < len) return NULL;
    for (p = start; p + len <= end; ++p) {
        if (memcmp(p, needle, len) == 0) {
            return p;
        }
    }
    return NULL;
}

static int dom_input_extract_string(const char *label,
                                    const char *start,
                                    const char *end,
                                    char *out,
                                    int out_len)
{
    const char *p;
    const char *colon;
    const char *quote_start;
    const char *quote_end;
    if (!label || !start || !end || !out || out_len <= 1) return 0;
    p = dom_input_find_in_range(start, end, label);
    if (!p) return 0;
    colon = dom_input_find_in_range(p, end, ":");
    if (!colon) return 0;
    quote_start = dom_input_find_in_range(colon, end, "\"");
    if (!quote_start) return 0;
    quote_start += 1;
    quote_end = dom_input_find_in_range(quote_start, end, "\"");
    if (!quote_end || quote_end <= quote_start) return 0;
    if (quote_end - quote_start >= out_len) {
        quote_end = quote_start + out_len - 1;
    }
    memcpy(out, quote_start, (size_t)(quote_end - quote_start));
    out[quote_end - quote_start] = '\0';
    return 1;
}

static void dom_input_parse_string_array(const char *label,
                                         const char *start,
                                         const char *end,
                                         dom_input_action action,
                                         int ctx_idx,
                                         dom_input_binding_type type)
{
    const char *p;
    const char *arr_start;
    const char *arr_end;
    const char *cursor;
    if (!label || !start || !end) return;

    p = dom_input_find_in_range(start, end, label);
    if (!p) return;
    arr_start = dom_input_find_in_range(p, end, "[");
    if (!arr_start || arr_start >= end) return;
    arr_end = dom_input_find_in_range(arr_start, end, "]");
    if (!arr_end || arr_end <= arr_start) return;

    cursor = arr_start;
    while (cursor && cursor < arr_end) {
        const char *quote = dom_input_find_in_range(cursor, arr_end, "\"");
        const char *quote2;
        char token[DOM_INPUT_MAX_TOKEN];
        DomInputBinding binding;
        int keycode = DOM_KEY_UNKNOWN;
        unsigned mods = 0;
        int mouse_button = -1;

        if (!quote || quote >= arr_end) break;
        quote2 = dom_input_find_in_range(quote + 1, arr_end, "\"");
        if (!quote2 || quote2 <= quote) break;
        if (quote2 - quote - 1 >= (int)sizeof(token)) {
            cursor = quote2 + 1;
            continue;
        }

        memset(&binding, 0, sizeof(binding));
        binding.action = action;
        binding.type = type;

        memcpy(token, quote + 1, (size_t)(quote2 - quote - 1));
        token[quote2 - quote - 1] = '\0';

        if (type == DOM_INPUT_BINDING_KEY) {
            if (dom_input_parse_key_string(token, &keycode, &mods)) {
                binding.keycode = keycode;
                binding.modifiers = mods;
                dom_input_add_binding(ctx_idx, &binding);
            }
        } else if (type == DOM_INPUT_BINDING_MOUSE_BUTTON) {
            mouse_button = dom_input_parse_mouse_button(token);
            if (mouse_button >= 0) {
                binding.mouse_button = mouse_button;
                dom_input_add_binding(ctx_idx, &binding);
            }
        }

        cursor = quote2 + 1;
    }
}

static void dom_input_parse_context(const char *buffer, const char *context_name, int ctx_idx)
{
    const char *ctx_start;
    const char *array_start;
    const char *array_end;
    const char *cursor;

    ctx_start = strstr(buffer, context_name);
    if (!ctx_start) return;
    array_start = strchr(ctx_start, '[');
    if (!array_start) return;
    array_end = strchr(array_start, ']');
    if (!array_end) return;

    cursor = array_start;
    while (cursor && cursor < array_end) {
        const char *obj_start = strchr(cursor, '{');
        const char *obj_end = strchr(cursor, '}');
        char action_buf[DOM_INPUT_MAX_TOKEN];
        dom_input_action action;

        if (!obj_start || !obj_end || obj_end > array_end) break;

        if (!dom_input_extract_string("action", obj_start, obj_end, action_buf, sizeof(action_buf))) {
            cursor = obj_end + 1;
            continue;
        }

        action = dom_input_action_from_name(action_buf);
        if (action != ACTION_NONE) {
            dom_input_parse_string_array("keys", obj_start, obj_end, action, ctx_idx, DOM_INPUT_BINDING_KEY);
            dom_input_parse_string_array("mouse", obj_start, obj_end, action, ctx_idx, DOM_INPUT_BINDING_MOUSE_BUTTON);
        }

        cursor = obj_end + 1;
    }
}

static int dom_input_read_file(const char *path, char **out_buf, long *out_size)
{
    FILE *f;
    long size;
    char *buf;
    if (!path || !out_buf) return 0;
    f = fopen(path, "rb");
    if (!f) return 0;
    if (fseek(f, 0, SEEK_END) != 0) {
        fclose(f);
        return 0;
    }
    size = ftell(f);
    if (size < 0) {
        fclose(f);
        return 0;
    }
    if (fseek(f, 0, SEEK_SET) != 0) {
        fclose(f);
        return 0;
    }
    buf = (char *)malloc((size_t)size + 1);
    if (!buf) {
        fclose(f);
        return 0;
    }
    if (fread(buf, 1, (size_t)size, f) != (size_t)size) {
        free(buf);
        fclose(f);
        return 0;
    }
    buf[size] = '\0';
    fclose(f);
    *out_buf = buf;
    if (out_size) *out_size = size;
    return 1;
}

static void dom_input_load_builtin_defaults(void)
{
    DomInputBinding b;
    dom_input_reset_state();
    memset(&b, 0, sizeof(b));

    /* Global (F1–F12, overlays) */
    b.type = DOM_INPUT_BINDING_KEY;
    b.modifiers = 0;
    b.keycode = DOM_KEY_F1;  b.action = ACTION_HELP_OVERLAY; dom_input_add_binding(DOM_INPUT_CONTEXT_GLOBAL, &b);
    b.keycode = DOM_KEY_F2;  b.action = ACTION_SCREENSHOT_CAPTURE; dom_input_add_binding(DOM_INPUT_CONTEXT_GLOBAL, &b);
    b.keycode = DOM_KEY_F3;  b.action = ACTION_DEBUG_OVERLAY_CYCLE; dom_input_add_binding(DOM_INPUT_CONTEXT_GLOBAL, &b);
    b.keycode = DOM_KEY_F4;  b.action = ACTION_VIEW_DIMENSION_TOGGLE; b.modifiers = 0; dom_input_add_binding(DOM_INPUT_CONTEXT_GLOBAL, &b);
    b.keycode = DOM_KEY_F4;  b.action = ACTION_VIEW_RENDER_MODE_CYCLE; b.modifiers = DOM_INPUT_MOD_SHIFT; dom_input_add_binding(DOM_INPUT_CONTEXT_GLOBAL, &b);
    b.keycode = DOM_KEY_F5;  b.action = ACTION_QUICK_SAVE; b.modifiers = 0; dom_input_add_binding(DOM_INPUT_CONTEXT_GLOBAL, &b);
    b.keycode = DOM_KEY_F6;  b.action = ACTION_QUICK_LOAD; dom_input_add_binding(DOM_INPUT_CONTEXT_GLOBAL, &b);
    b.keycode = DOM_KEY_F7;  b.action = ACTION_REPLAY_PANEL; dom_input_add_binding(DOM_INPUT_CONTEXT_GLOBAL, &b);
    b.keycode = DOM_KEY_F8;  b.action = ACTION_TOOLS_PANEL; dom_input_add_binding(DOM_INPUT_CONTEXT_GLOBAL, &b);
    b.keycode = DOM_KEY_F9;  b.action = ACTION_WORLD_MAP; dom_input_add_binding(DOM_INPUT_CONTEXT_GLOBAL, &b);
    b.keycode = DOM_KEY_F10; b.action = ACTION_SETTINGS_MENU; dom_input_add_binding(DOM_INPUT_CONTEXT_GLOBAL, &b);
    b.keycode = DOM_KEY_F11; b.action = ACTION_FULLSCREEN_TOGGLE; dom_input_add_binding(DOM_INPUT_CONTEXT_GLOBAL, &b);
    b.keycode = DOM_KEY_F12; b.action = ACTION_DEV_CONSOLE; dom_input_add_binding(DOM_INPUT_CONTEXT_GLOBAL, &b);
    b.keycode = DOM_KEY_P;   b.action = ACTION_PROFILER_OVERLAY; b.modifiers = DOM_INPUT_MOD_CTRL; dom_input_add_binding(DOM_INPUT_CONTEXT_GLOBAL, &b);
    b.keycode = DOM_KEY_ALT; b.action = ACTION_HIGHLIGHT_INTERACTIVES; b.modifiers = 0; dom_input_add_binding(DOM_INPUT_CONTEXT_GLOBAL, &b);

    /* Gameplay */
    b.modifiers = 0;
    b.type = DOM_INPUT_BINDING_KEY;
    b.keycode = DOM_KEY_W; b.action = ACTION_MOVE_FORWARD; dom_input_add_binding(DOM_INPUT_CONTEXT_GAMEPLAY, &b);
    b.keycode = DOM_KEY_S; b.action = ACTION_MOVE_BACKWARD; dom_input_add_binding(DOM_INPUT_CONTEXT_GAMEPLAY, &b);
    b.keycode = DOM_KEY_A; b.action = ACTION_MOVE_LEFT; dom_input_add_binding(DOM_INPUT_CONTEXT_GAMEPLAY, &b);
    b.keycode = DOM_KEY_D; b.action = ACTION_MOVE_RIGHT; dom_input_add_binding(DOM_INPUT_CONTEXT_GAMEPLAY, &b);
    b.keycode = DOM_KEY_Q; b.action = ACTION_CAMERA_ROTATE_CCW; dom_input_add_binding(DOM_INPUT_CONTEXT_GAMEPLAY, &b);
    b.keycode = DOM_KEY_E; b.action = ACTION_CAMERA_ROTATE_CW; dom_input_add_binding(DOM_INPUT_CONTEXT_GAMEPLAY, &b);
    b.keycode = DOM_KEY_R; b.action = ACTION_CAMERA_ALT_UP; dom_input_add_binding(DOM_INPUT_CONTEXT_GAMEPLAY, &b);
    b.keycode = DOM_KEY_F; b.action = ACTION_CAMERA_ALT_DOWN; dom_input_add_binding(DOM_INPUT_CONTEXT_GAMEPLAY, &b);
    b.keycode = DOM_KEY_TAB; b.action = ACTION_LAYER_CYCLE; dom_input_add_binding(DOM_INPUT_CONTEXT_GAMEPLAY, &b);

    b.type = DOM_INPUT_BINDING_MOUSE_BUTTON;
    b.modifiers = 0;
    b.mouse_button = DOM_INPUT_MOUSE_LEFT; b.action = ACTION_PRIMARY_SELECT; dom_input_add_binding(DOM_INPUT_CONTEXT_GAMEPLAY, &b);
    b.mouse_button = DOM_INPUT_MOUSE_RIGHT; b.action = ACTION_SECONDARY_SELECT; dom_input_add_binding(DOM_INPUT_CONTEXT_GAMEPLAY, &b);

    b.type = DOM_INPUT_BINDING_KEY;
    b.keycode = DOM_KEY_1; b.action = ACTION_QUICKBAR_SLOT_1; dom_input_add_binding(DOM_INPUT_CONTEXT_GAMEPLAY, &b);
    b.keycode = DOM_KEY_2; b.action = ACTION_QUICKBAR_SLOT_2; dom_input_add_binding(DOM_INPUT_CONTEXT_GAMEPLAY, &b);
    b.keycode = DOM_KEY_3; b.action = ACTION_QUICKBAR_SLOT_3; dom_input_add_binding(DOM_INPUT_CONTEXT_GAMEPLAY, &b);
    b.keycode = DOM_KEY_4; b.action = ACTION_QUICKBAR_SLOT_4; dom_input_add_binding(DOM_INPUT_CONTEXT_GAMEPLAY, &b);
    b.keycode = DOM_KEY_5; b.action = ACTION_QUICKBAR_SLOT_5; dom_input_add_binding(DOM_INPUT_CONTEXT_GAMEPLAY, &b);
    b.keycode = DOM_KEY_6; b.action = ACTION_QUICKBAR_SLOT_6; dom_input_add_binding(DOM_INPUT_CONTEXT_GAMEPLAY, &b);
    b.keycode = DOM_KEY_7; b.action = ACTION_QUICKBAR_SLOT_7; dom_input_add_binding(DOM_INPUT_CONTEXT_GAMEPLAY, &b);
    b.keycode = DOM_KEY_8; b.action = ACTION_QUICKBAR_SLOT_8; dom_input_add_binding(DOM_INPUT_CONTEXT_GAMEPLAY, &b);
    b.keycode = DOM_KEY_9; b.action = ACTION_QUICKBAR_SLOT_9; dom_input_add_binding(DOM_INPUT_CONTEXT_GAMEPLAY, &b);

    /* UI */
    b.type = DOM_INPUT_BINDING_KEY;
    b.modifiers = 0;
    b.keycode = DOM_KEY_ESCAPE; b.action = ACTION_UI_BACK; dom_input_add_binding(DOM_INPUT_CONTEXT_UI, &b);

    /* Launcher subset mirrors global + UI selection */
    b.keycode = DOM_KEY_F1;  b.action = ACTION_HELP_OVERLAY; dom_input_add_binding(DOM_INPUT_CONTEXT_LAUNCHER, &b);
    b.keycode = DOM_KEY_F3;  b.action = ACTION_DEBUG_OVERLAY_CYCLE; dom_input_add_binding(DOM_INPUT_CONTEXT_LAUNCHER, &b);
    b.keycode = DOM_KEY_F11; b.action = ACTION_FULLSCREEN_TOGGLE; dom_input_add_binding(DOM_INPUT_CONTEXT_LAUNCHER, &b);
    b.keycode = DOM_KEY_F10; b.action = ACTION_SETTINGS_MENU; dom_input_add_binding(DOM_INPUT_CONTEXT_LAUNCHER, &b);
    b.keycode = DOM_KEY_ESCAPE; b.action = ACTION_UI_BACK; dom_input_add_binding(DOM_INPUT_CONTEXT_LAUNCHER, &b);
}

void dom_input_mapping_init(void)
{
    dom_input_reset_state();
}

void dom_input_mapping_shutdown(void)
{
    dom_input_reset_state();
}

int dom_input_mapping_load_defaults(const char *path)
{
    char *buf = NULL;
    int parsed = 0;
    int ctx_idx;

    dom_input_reset_state();

    if (path && dom_input_read_file(path, &buf, NULL)) {
        parsed = 1;
        for (ctx_idx = 0; ctx_idx < (int)DOM_INPUT_CONTEXT_COUNT; ++ctx_idx) {
            dom_input_parse_context(buf, g_context_names[ctx_idx], ctx_idx);
        }
        free(buf);
    }

    if (!parsed) {
        dom_input_load_builtin_defaults();
        return -1;
    }

    return 0;
}

void dom_input_mapping_set_context_enabled(dom_input_context ctx, int enabled)
{
    unsigned bit;
    if (ctx < 0 || ctx >= DOM_INPUT_CONTEXT_COUNT) {
        return;
    }
    bit = (1u << ctx);
    if (enabled) {
        g_active_context_mask |= bit;
    } else {
        g_active_context_mask &= ~bit;
    }
    g_active_context_mask |= (1u << DOM_INPUT_CONTEXT_GLOBAL);
}

void dom_input_mapping_set_active_context_mask(unsigned mask)
{
    g_active_context_mask = mask | (1u << DOM_INPUT_CONTEXT_GLOBAL);
}

unsigned dom_input_mapping_active_context_mask(void)
{
    return g_active_context_mask;
}

static int dom_input_context_active(int ctx)
{
    unsigned bit;
    if (ctx < 0 || ctx >= (int)DOM_INPUT_CONTEXT_COUNT) return 0;
    bit = (1u << ctx);
    return (g_active_context_mask & bit) != 0;
}

static int dom_input_modifiers_match(unsigned required, const DomPlatformInputFrame *frame)
{
    if (!required) return 1;
    if (!frame) return 0;
    if ((required & DOM_INPUT_MOD_CTRL) && !frame->key_down[DOM_KEY_CONTROL]) return 0;
    if ((required & DOM_INPUT_MOD_SHIFT) && !frame->key_down[DOM_KEY_SHIFT]) return 0;
    if ((required & DOM_INPUT_MOD_ALT) && !frame->key_down[DOM_KEY_ALT]) return 0;
    return 1;
}

static void dom_input_apply_action_press(dom_input_action action)
{
    if (action <= ACTION_NONE || action >= ACTION_COUNT) {
        return;
    }
    g_action_down_refcount[action] += 1;
    g_action_triggered[action] = 1;
}

static void dom_input_apply_action_release(dom_input_action action)
{
    if (action <= ACTION_NONE || action >= ACTION_COUNT) {
        return;
    }
    if (g_action_down_refcount[action] > 0) {
        g_action_down_refcount[action] -= 1;
    }
}

static void dom_input_process_key_event_internal(int keycode, int pressed, const DomPlatformInputFrame *frame)
{
    int ctx;
    if (keycode < 0 || keycode >= DOM_KEYCODE_MAX) {
        return;
    }
    g_key_is_down[keycode] = pressed ? 1 : 0;

    for (ctx = 0; ctx < (int)DOM_INPUT_CONTEXT_COUNT; ++ctx) {
        DomInputContextBindings *c = &g_contexts[ctx];
        int i;
        if (!dom_input_context_active(ctx)) continue;
        for (i = 0; i < c->binding_count; ++i) {
            DomInputBinding *b = &c->bindings[i];
            if (b->type != DOM_INPUT_BINDING_KEY) continue;
            if (b->keycode != keycode) continue;
            if (!dom_input_modifiers_match(b->modifiers, frame)) continue;
            if (pressed) {
                dom_input_apply_action_press(b->action);
            } else {
                dom_input_apply_action_release(b->action);
            }
        }
    }
}

static void dom_input_process_mouse_button_event(int button, int pressed)
{
    int ctx;
    for (ctx = 0; ctx < (int)DOM_INPUT_CONTEXT_COUNT; ++ctx) {
        DomInputContextBindings *c = &g_contexts[ctx];
        int i;
        if (!dom_input_context_active(ctx)) continue;
        for (i = 0; i < c->binding_count; ++i) {
            DomInputBinding *b = &c->bindings[i];
            if (b->type != DOM_INPUT_BINDING_MOUSE_BUTTON) continue;
            if (b->mouse_button != button) continue;
            if (pressed) {
                dom_input_apply_action_press(b->action);
            } else {
                dom_input_apply_action_release(b->action);
            }
        }
    }
}

void dom_input_mapping_begin_frame(void)
{
    memset(g_action_triggered, 0, sizeof(g_action_triggered));
}

void dom_input_mapping_apply_frame(const DomPlatformInputFrame *frame)
{
    int i;
    if (!frame) return;

    for (i = 0; i < DOM_KEYCODE_MAX; ++i) {
        dom_bool8 now = frame->key_down[i] ? 1 : 0;
        dom_bool8 prev = g_prev_key_down[i];
        if (now != prev) {
            g_prev_key_down[i] = now;
            dom_input_process_key_event_internal(i, now ? 1 : 0, frame);
        } else {
            g_key_is_down[i] = now;
        }
    }

    for (i = 0; i < 3; ++i) {
        dom_bool8 now = frame->mouse_down[i] ? 1 : 0;
        dom_bool8 prev = g_prev_mouse_down[i];
        if (now != prev) {
            g_prev_mouse_down[i] = now;
            dom_input_on_mouse_button(i, now ? 1 : 0);
        }
    }

    if (frame->wheel_delta != 0) {
        dom_input_on_mouse_wheel(frame->wheel_delta);
    }
}

void dom_input_on_key_event(int keycode, int pressed)
{
    dom_input_process_key_event_internal(keycode, pressed, NULL);
}

void dom_input_on_mouse_button(int button, int pressed)
{
    dom_input_process_mouse_button_event(button, pressed);
}

void dom_input_on_mouse_wheel(int delta)
{
    int ctx;
    for (ctx = 0; ctx < (int)DOM_INPUT_CONTEXT_COUNT; ++ctx) {
        DomInputContextBindings *c = &g_contexts[ctx];
        int i;
        if (!dom_input_context_active(ctx)) continue;
        for (i = 0; i < c->binding_count; ++i) {
            DomInputBinding *b = &c->bindings[i];
            if (b->type != DOM_INPUT_BINDING_MOUSE_WHEEL) continue;
            if (b->wheel_direction != 0 && ((delta > 0 && b->wheel_direction < 0) || (delta < 0 && b->wheel_direction > 0))) {
                continue;
            }
            dom_input_apply_action_press(b->action);
        }
    }
}

int dom_input_action_was_triggered(dom_input_action action)
{
    if (action <= ACTION_NONE || action >= ACTION_COUNT) return 0;
    return g_action_triggered[action] ? 1 : 0;
}

int dom_input_action_is_down(dom_input_action action)
{
    if (action <= ACTION_NONE || action >= ACTION_COUNT) return 0;
    return g_action_down_refcount[action] > 0 ? 1 : 0;
}

static const char *dom_input_keycode_name(int keycode)
{
    switch (keycode) {
    case DOM_KEY_ESCAPE: return "ESCAPE";
    case DOM_KEY_TAB: return "TAB";
    case DOM_KEY_SPACE: return "SPACE";
    case DOM_KEY_SHIFT: return "SHIFT";
    case DOM_KEY_CONTROL: return "CTRL";
    case DOM_KEY_ALT: return "ALT";
    case DOM_KEY_LEFT: return "LEFT";
    case DOM_KEY_RIGHT: return "RIGHT";
    case DOM_KEY_UP: return "UP";
    case DOM_KEY_DOWN: return "DOWN";
    case DOM_KEY_F1: return "F1";
    case DOM_KEY_F2: return "F2";
    case DOM_KEY_F3: return "F3";
    case DOM_KEY_F4: return "F4";
    case DOM_KEY_F5: return "F5";
    case DOM_KEY_F6: return "F6";
    case DOM_KEY_F7: return "F7";
    case DOM_KEY_F8: return "F8";
    case DOM_KEY_F9: return "F9";
    case DOM_KEY_F10: return "F10";
    case DOM_KEY_F11: return "F11";
    case DOM_KEY_F12: return "F12";
    default:
        if (keycode >= DOM_KEY_A && keycode <= DOM_KEY_Z) {
            static char letter[2];
            letter[0] = (char)('A' + (keycode - DOM_KEY_A));
            letter[1] = '\0';
            return letter;
        }
        if (keycode >= DOM_KEY_0 && keycode <= DOM_KEY_9) {
            static char digit[2];
            digit[0] = (char)('0' + (keycode - DOM_KEY_0));
            digit[1] = '\0';
            return digit;
        }
        break;
    }
    return "UNKNOWN";
}

void dom_input_mapping_debug_dump_binding(dom_input_action action)
{
#if DOM_INPUT_LOG_BINDINGS
    int ctx;
    for (ctx = 0; ctx < (int)DOM_INPUT_CONTEXT_COUNT; ++ctx) {
        DomInputContextBindings *c = &g_contexts[ctx];
        int i;
        for (i = 0; i < c->binding_count; ++i) {
            DomInputBinding *b = &c->bindings[i];
            if (b->action != action) continue;
            if (b->type == DOM_INPUT_BINDING_KEY) {
                printf("[input] %s -> %s%s%s%s\n",
                       dom_input_action_name(action),
                       (b->modifiers & DOM_INPUT_MOD_CTRL) ? "CTRL+" : "",
                       (b->modifiers & DOM_INPUT_MOD_SHIFT) ? "SHIFT+" : "",
                       (b->modifiers & DOM_INPUT_MOD_ALT) ? "ALT+" : "",
                       dom_input_keycode_name(b->keycode));
                return;
            } else if (b->type == DOM_INPUT_BINDING_MOUSE_BUTTON) {
                const char *btn = "MOUSE_LEFT";
                if (b->mouse_button == DOM_INPUT_MOUSE_RIGHT) btn = "MOUSE_RIGHT";
                else if (b->mouse_button == DOM_INPUT_MOUSE_MIDDLE) btn = "MOUSE_MIDDLE";
                printf("[input] %s -> %s\n", dom_input_action_name(action), btn);
                return;
            }
        }
    }
    printf("[input] %s -> (unbound)\n", dom_input_action_name(action));
#else
    (void)action;
#endif
}
