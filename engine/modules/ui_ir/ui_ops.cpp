/*
FILE: source/domino/ui_ir/ui_ops.cpp
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / ui_ir ops
RESPONSIBILITY: Deterministic ops.json parsing and scripted edits for UI IR.
*/
#include "ui_ops.h"

#include "ui_caps.h"
#include "ui_validate.h"

#include <ctype.h>
#include <errno.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>

#include <utility>
#include <vector>

enum domui_json_type {
    DOMUI_JSON_NULL = 0,
    DOMUI_JSON_BOOL,
    DOMUI_JSON_NUMBER,
    DOMUI_JSON_STRING,
    DOMUI_JSON_ARRAY,
    DOMUI_JSON_OBJECT
};

struct domui_json_value {
    domui_json_type type;
    int bool_value;
    std::string string_value;
    std::vector<domui_json_value> array;
    std::vector<std::pair<std::string, domui_json_value> > object;

    domui_json_value()
        : type(DOMUI_JSON_NULL),
          bool_value(0),
          string_value(),
          array(),
          object()
    {
    }
};

struct domui_json_parser {
    const char* start;
    const char* cur;
    const char* end;
    domui_diag* diag;
};

static void domui_json_skip_ws(domui_json_parser* p)
{
    while (p->cur < p->end) {
        char c = *p->cur;
        if (c != ' ' && c != '\t' && c != '\n' && c != '\r') {
            break;
        }
        p->cur++;
    }
}

static void domui_json_add_error(domui_json_parser* p, const char* message)
{
    if (!p || !p->diag) {
        return;
    }
    size_t offset = (size_t)(p->cur - p->start);
    char ctx[64];
    sprintf(ctx, "offset %u", (unsigned int)offset);
    p->diag->add_error(message ? message : "ops: parse error", 0u, ctx);
}

static int domui_json_append_utf8(std::string& out, unsigned int codepoint)
{
    if (codepoint <= 0x7Fu) {
        out.push_back((char)codepoint);
        return 1;
    }
    if (codepoint <= 0x7FFu) {
        out.push_back((char)(0xC0u | (codepoint >> 6)));
        out.push_back((char)(0x80u | (codepoint & 0x3Fu)));
        return 1;
    }
    if (codepoint <= 0xFFFFu) {
        out.push_back((char)(0xE0u | (codepoint >> 12)));
        out.push_back((char)(0x80u | ((codepoint >> 6) & 0x3Fu)));
        out.push_back((char)(0x80u | (codepoint & 0x3Fu)));
        return 1;
    }
    return 0;
}

static int domui_json_hex_value(char c, unsigned int* out)
{
    if (c >= '0' && c <= '9') {
        *out = (unsigned int)(c - '0');
        return 1;
    }
    if (c >= 'a' && c <= 'f') {
        *out = (unsigned int)(10 + (c - 'a'));
        return 1;
    }
    if (c >= 'A' && c <= 'F') {
        *out = (unsigned int)(10 + (c - 'A'));
        return 1;
    }
    return 0;
}

static int domui_json_parse_string(domui_json_parser* p, std::string& out)
{
    const char* cur;
    out.clear();
    domui_json_skip_ws(p);
    if (p->cur >= p->end || *p->cur != '"') {
        domui_json_add_error(p, "ops: expected string");
        return 0;
    }
    p->cur++;
    cur = p->cur;
    while (cur < p->end) {
        unsigned char c = (unsigned char)*cur;
        if (c == '"') {
            p->cur = cur + 1;
            return 1;
        }
        if (c == '\\') {
            cur++;
            if (cur >= p->end) {
                domui_json_add_error(p, "ops: unterminated escape");
                return 0;
            }
            c = (unsigned char)*cur;
            if (c == '"' || c == '\\' || c == '/') {
                out.push_back((char)c);
            } else if (c == 'b') {
                out.push_back('\b');
            } else if (c == 'f') {
                out.push_back('\f');
            } else if (c == 'n') {
                out.push_back('\n');
            } else if (c == 'r') {
                out.push_back('\r');
            } else if (c == 't') {
                out.push_back('\t');
            } else if (c == 'u') {
                unsigned int codepoint = 0u;
                unsigned int h;
                int i;
                if (cur + 4 >= p->end) {
                    domui_json_add_error(p, "ops: invalid unicode escape");
                    return 0;
                }
                for (i = 0; i < 4; ++i) {
                    cur++;
                    if (!domui_json_hex_value(*cur, &h)) {
                        domui_json_add_error(p, "ops: invalid unicode escape");
                        return 0;
                    }
                    codepoint = (codepoint << 4) | h;
                }
                if (codepoint >= 0xD800u && codepoint <= 0xDFFFu) {
                    domui_json_add_error(p, "ops: unsupported unicode surrogate");
                    return 0;
                }
                if (!domui_json_append_utf8(out, codepoint)) {
                    domui_json_add_error(p, "ops: unicode out of range");
                    return 0;
                }
            } else {
                domui_json_add_error(p, "ops: invalid escape");
                return 0;
            }
        } else {
            if (c < 0x20u) {
                domui_json_add_error(p, "ops: invalid control character");
                return 0;
            }
            out.push_back((char)c);
        }
        cur++;
    }
    domui_json_add_error(p, "ops: unterminated string");
    return 0;
}

static int domui_json_parse_number(domui_json_parser* p, std::string& out)
{
    const char* start;
    const char* cur;
    domui_json_skip_ws(p);
    if (p->cur >= p->end) {
        domui_json_add_error(p, "ops: expected number");
        return 0;
    }
    start = p->cur;
    cur = p->cur;
    if (*cur == '-') {
        cur++;
    }
    if (cur >= p->end || *cur < '0' || *cur > '9') {
        domui_json_add_error(p, "ops: invalid number");
        return 0;
    }
    if (*cur == '0' && (cur + 1) < p->end && (cur[1] >= '0' && cur[1] <= '9')) {
        domui_json_add_error(p, "ops: leading zero");
        return 0;
    }
    while (cur < p->end && *cur >= '0' && *cur <= '9') {
        cur++;
    }
    if (cur < p->end && (*cur == '.' || *cur == 'e' || *cur == 'E')) {
        domui_json_add_error(p, "ops: non-integer number");
        return 0;
    }
    out.assign(start, cur - start);
    p->cur = cur;
    return 1;
}

static int domui_json_parse_literal(domui_json_parser* p, const char* text)
{
    size_t i;
    for (i = 0u; text[i]; ++i) {
        if (p->cur + i >= p->end || p->cur[i] != text[i]) {
            return 0;
        }
    }
    p->cur += i;
    return 1;
}

static int domui_json_parse_value(domui_json_parser* p, domui_json_value& out);

static int domui_json_parse_array(domui_json_parser* p, domui_json_value& out)
{
    domui_json_skip_ws(p);
    if (p->cur >= p->end || *p->cur != '[') {
        domui_json_add_error(p, "ops: expected '['");
        return 0;
    }
    p->cur++;
    out.type = DOMUI_JSON_ARRAY;
    out.array.clear();
    out.object.clear();
    domui_json_skip_ws(p);
    if (p->cur < p->end && *p->cur == ']') {
        p->cur++;
        return 1;
    }
    while (p->cur < p->end) {
        domui_json_value item;
        if (!domui_json_parse_value(p, item)) {
            return 0;
        }
        out.array.push_back(item);
        domui_json_skip_ws(p);
        if (p->cur >= p->end) {
            domui_json_add_error(p, "ops: unterminated array");
            return 0;
        }
        if (*p->cur == ',') {
            p->cur++;
            continue;
        }
        if (*p->cur == ']') {
            p->cur++;
            return 1;
        }
        domui_json_add_error(p, "ops: expected ',' or ']'");
        return 0;
    }
    domui_json_add_error(p, "ops: unterminated array");
    return 0;
}

static int domui_json_key_exists(const std::vector<std::pair<std::string, domui_json_value> >& members,
                                 const std::string& key)
{
    for (size_t i = 0u; i < members.size(); ++i) {
        if (members[i].first == key) {
            return 1;
        }
    }
    return 0;
}

static int domui_json_parse_object(domui_json_parser* p, domui_json_value& out)
{
    domui_json_skip_ws(p);
    if (p->cur >= p->end || *p->cur != '{') {
        domui_json_add_error(p, "ops: expected '{'");
        return 0;
    }
    p->cur++;
    out.type = DOMUI_JSON_OBJECT;
    out.object.clear();
    out.array.clear();
    domui_json_skip_ws(p);
    if (p->cur < p->end && *p->cur == '}') {
        p->cur++;
        return 1;
    }
    while (p->cur < p->end) {
        std::string key;
        std::pair<std::string, domui_json_value> member;
        if (!domui_json_parse_string(p, key)) {
            return 0;
        }
        domui_json_skip_ws(p);
        if (p->cur >= p->end || *p->cur != ':') {
            domui_json_add_error(p, "ops: expected ':'");
            return 0;
        }
        p->cur++;
        if (!domui_json_parse_value(p, member.second)) {
            return 0;
        }
        if (domui_json_key_exists(out.object, key)) {
            domui_json_add_error(p, "ops: duplicate key");
            return 0;
        }
        member.first = key;
        out.object.push_back(member);
        domui_json_skip_ws(p);
        if (p->cur >= p->end) {
            domui_json_add_error(p, "ops: unterminated object");
            return 0;
        }
        if (*p->cur == ',') {
            p->cur++;
            continue;
        }
        if (*p->cur == '}') {
            p->cur++;
            return 1;
        }
        domui_json_add_error(p, "ops: expected ',' or '}'");
        return 0;
    }
    domui_json_add_error(p, "ops: unterminated object");
    return 0;
}

static int domui_json_parse_value(domui_json_parser* p, domui_json_value& out)
{
    domui_json_skip_ws(p);
    if (p->cur >= p->end) {
        domui_json_add_error(p, "ops: unexpected end");
        return 0;
    }
    if (*p->cur == '{') {
        return domui_json_parse_object(p, out);
    }
    if (*p->cur == '[') {
        return domui_json_parse_array(p, out);
    }
    if (*p->cur == '"') {
        out.type = DOMUI_JSON_STRING;
        return domui_json_parse_string(p, out.string_value);
    }
    if (*p->cur == 't') {
        if (!domui_json_parse_literal(p, "true")) {
            domui_json_add_error(p, "ops: invalid literal");
            return 0;
        }
        out.type = DOMUI_JSON_BOOL;
        out.bool_value = 1;
        return 1;
    }
    if (*p->cur == 'f') {
        if (!domui_json_parse_literal(p, "false")) {
            domui_json_add_error(p, "ops: invalid literal");
            return 0;
        }
        out.type = DOMUI_JSON_BOOL;
        out.bool_value = 0;
        return 1;
    }
    if (*p->cur == 'n') {
        if (!domui_json_parse_literal(p, "null")) {
            domui_json_add_error(p, "ops: invalid literal");
            return 0;
        }
        out.type = DOMUI_JSON_NULL;
        return 1;
    }
    if (*p->cur == '-' || (*p->cur >= '0' && *p->cur <= '9')) {
        out.type = DOMUI_JSON_NUMBER;
        return domui_json_parse_number(p, out.string_value);
    }
    domui_json_add_error(p, "ops: unexpected token");
    return 0;
}

static int domui_json_parse(domui_json_parser* p, domui_json_value& out)
{
    if (!domui_json_parse_value(p, out)) {
        return 0;
    }
    domui_json_skip_ws(p);
    if (p->cur != p->end) {
        domui_json_add_error(p, "ops: trailing characters");
        return 0;
    }
    return 1;
}

static const domui_json_value* domui_json_find_member(const domui_json_value& obj, const char* key)
{
    if (obj.type != DOMUI_JSON_OBJECT || !key) {
        return 0;
    }
    for (size_t i = 0u; i < obj.object.size(); ++i) {
        if (obj.object[i].first == key) {
            return &obj.object[i].second;
        }
    }
    return 0;
}

static int domui_ops_parse_u32(const domui_json_value& v, domui_u32* out_value)
{
    unsigned long value;
    char* endptr = 0;
    if (v.type != DOMUI_JSON_NUMBER) {
        return 0;
    }
    if (!v.string_value.empty() && v.string_value[0] == '-') {
        return 0;
    }
    errno = 0;
    value = strtoul(v.string_value.c_str(), &endptr, 10);
    if (errno != 0 || !endptr || *endptr) {
        return 0;
    }
    if (value > 0xFFFFFFFFul) {
        return 0;
    }
    if (out_value) {
        *out_value = (domui_u32)value;
    }
    return 1;
}

static int domui_ops_parse_int(const domui_json_value& v, int* out_value)
{
    long value;
    char* endptr = 0;
    if (v.type != DOMUI_JSON_NUMBER) {
        return 0;
    }
    errno = 0;
    value = strtol(v.string_value.c_str(), &endptr, 10);
    if (errno != 0 || !endptr || *endptr) {
        return 0;
    }
    if (value < (long)INT_MIN || value > (long)INT_MAX) {
        return 0;
    }
    if (out_value) {
        *out_value = (int)value;
    }
    return 1;
}

static int domui_ops_parse_bool(const domui_json_value& v, int* out_value)
{
    if (v.type != DOMUI_JSON_BOOL) {
        return 0;
    }
    if (out_value) {
        *out_value = v.bool_value ? 1 : 0;
    }
    return 1;
}

static int domui_ops_parse_string(const domui_json_value& v, std::string& out_value)
{
    if (v.type != DOMUI_JSON_STRING) {
        return 0;
    }
    out_value = v.string_value;
    return 1;
}

static int domui_ops_check_unknown_fields(const domui_json_value& obj,
                                          const char* const* allowed,
                                          size_t allowed_count,
                                          domui_diag* diag,
                                          const char* context,
                                          int strict)
{
    const char* ctx = context ? context : "ops";
    if (!strict) {
        return 1;
    }
    if (obj.type != DOMUI_JSON_OBJECT) {
        if (diag) {
            diag->add_error("ops: expected object", 0u, ctx);
        }
        return 0;
    }
    for (size_t i = 0u; i < obj.object.size(); ++i) {
        size_t j;
        int found = 0;
        for (j = 0u; j < allowed_count; ++j) {
            if (obj.object[i].first == allowed[j]) {
                found = 1;
                break;
            }
        }
        if (!found) {
            std::string msg = "ops: unknown field '" + obj.object[i].first + "'";
            if (diag) {
                diag->add_error(msg.c_str(), 0u, ctx);
            }
            return 0;
        }
    }
    return 1;
}

struct domui_ops_context {
    domui_doc* doc;
    domui_diag* diag;
    domui_ops_result* result;
    const domui_ops_apply_params* params;
    int strict;
    size_t op_index;
    std::string op_name;
    std::string context_label;
    std::string default_root_name;
    int stop;

    domui_ops_context()
        : doc(0),
          diag(0),
          result(0),
          params(0),
          strict(1),
          op_index(0u),
          op_name(),
          context_label(),
          default_root_name(),
          stop(0)
    {
    }
};

static std::string domui_ops_upper(const std::string& text)
{
    std::string out;
    out.reserve(text.size());
    for (size_t i = 0u; i < text.size(); ++i) {
        char c = text[i];
        if (c >= 'a' && c <= 'z') {
            c = (char)(c - 'a' + 'A');
        }
        out.push_back(c);
    }
    return out;
}

static void domui_ops_update_context_label(domui_ops_context* ctx)
{
    char buf[64];
    if (!ctx) {
        return;
    }
    sprintf(buf, "op %u", (unsigned int)ctx->op_index);
    ctx->context_label = buf;
    if (!ctx->op_name.empty()) {
        ctx->context_label += " ";
        ctx->context_label += ctx->op_name;
    }
}

static void domui_ops_add_error(domui_ops_context* ctx, const char* message, domui_widget_id id)
{
    if (!ctx || !ctx->diag) {
        return;
    }
    const char* ctx_text = ctx->context_label.empty() ? "ops" : ctx->context_label.c_str();
    ctx->diag->add_error(message ? message : "ops: error", id, ctx_text);
}

static void domui_ops_add_warning(domui_ops_context* ctx, const char* message, domui_widget_id id)
{
    if (!ctx || !ctx->diag) {
        return;
    }
    const char* ctx_text = ctx->context_label.empty() ? "ops" : ctx->context_label.c_str();
    ctx->diag->add_warning(message ? message : "ops: warning", id, ctx_text);
}

static void domui_ops_append_diag(domui_diag* dst, const domui_diag& src)
{
    if (!dst) {
        return;
    }
    {
        const std::vector<domui_diag_item>& errs = src.errors();
        for (size_t i = 0u; i < errs.size(); ++i) {
            dst->add_error(errs[i].message, errs[i].widget_id, errs[i].context);
        }
    }
    {
        const std::vector<domui_diag_item>& warns = src.warnings();
        for (size_t i = 0u; i < warns.size(); ++i) {
            dst->add_warning(warns[i].message, warns[i].widget_id, warns[i].context);
        }
    }
}

static int domui_ops_parse_var_name(const std::string& text, std::string& out_name)
{
    if (text.size() < 2u || text[0] != '$') {
        return 0;
    }
    out_name = text.substr(1u);
    if (out_name.empty()) {
        return 0;
    }
    for (size_t i = 0u; i < out_name.size(); ++i) {
        unsigned char c = (unsigned char)out_name[i];
        if (!isalnum(c) && c != '_') {
            return 0;
        }
    }
    return 1;
}

static int domui_ops_store_out(domui_ops_context* ctx, const domui_json_value* out_val, domui_widget_id id)
{
    if (!out_val) {
        return 1;
    }
    if (out_val->type != DOMUI_JSON_STRING) {
        domui_ops_add_error(ctx, "ops: out must be string", id);
        return 0;
    }
    std::string name;
    if (!domui_ops_parse_var_name(out_val->string_value, name)) {
        domui_ops_add_error(ctx, "ops: invalid out variable", id);
        return 0;
    }
    if (ctx && ctx->result) {
        ctx->result->created_ids[name] = id;
    }
    return 1;
}

static const domui_json_value* domui_ops_require_member(domui_ops_context* ctx,
                                                        const domui_json_value& obj,
                                                        const char* key)
{
    const domui_json_value* v = domui_json_find_member(obj, key);
    if (!v) {
        std::string msg = "ops: missing field '" + std::string(key ? key : "") + "'";
        domui_ops_add_error(ctx, msg.c_str(), 0u);
        return 0;
    }
    return v;
}

static domui_widget* domui_ops_require_widget(domui_ops_context* ctx, domui_widget_id id)
{
    domui_widget* w = ctx && ctx->doc ? ctx->doc->find_by_id(id) : 0;
    if (!w) {
        domui_ops_add_error(ctx, "ops: widget not found", id);
    }
    return w;
}

static int domui_ops_widget_type_from_string(const std::string& text, domui_widget_type* out_type)
{
    std::string t = domui_ops_upper(text);
    if (t == "CONTAINER") { if (out_type) *out_type = DOMUI_WIDGET_CONTAINER; return 1; }
    if (t == "STATIC_TEXT") { if (out_type) *out_type = DOMUI_WIDGET_STATIC_TEXT; return 1; }
    if (t == "BUTTON") { if (out_type) *out_type = DOMUI_WIDGET_BUTTON; return 1; }
    if (t == "EDIT") { if (out_type) *out_type = DOMUI_WIDGET_EDIT; return 1; }
    if (t == "LISTBOX") { if (out_type) *out_type = DOMUI_WIDGET_LISTBOX; return 1; }
    if (t == "COMBOBOX") { if (out_type) *out_type = DOMUI_WIDGET_COMBOBOX; return 1; }
    if (t == "CHECKBOX") { if (out_type) *out_type = DOMUI_WIDGET_CHECKBOX; return 1; }
    if (t == "RADIO") { if (out_type) *out_type = DOMUI_WIDGET_RADIO; return 1; }
    if (t == "TAB") { if (out_type) *out_type = DOMUI_WIDGET_TAB; return 1; }
    if (t == "TREEVIEW") { if (out_type) *out_type = DOMUI_WIDGET_TREEVIEW; return 1; }
    if (t == "LISTVIEW") { if (out_type) *out_type = DOMUI_WIDGET_LISTVIEW; return 1; }
    if (t == "PROGRESS") { if (out_type) *out_type = DOMUI_WIDGET_PROGRESS; return 1; }
    if (t == "SLIDER") { if (out_type) *out_type = DOMUI_WIDGET_SLIDER; return 1; }
    if (t == "GROUPBOX") { if (out_type) *out_type = DOMUI_WIDGET_GROUPBOX; return 1; }
    if (t == "IMAGE") { if (out_type) *out_type = DOMUI_WIDGET_IMAGE; return 1; }
    if (t == "SPLITTER") { if (out_type) *out_type = DOMUI_WIDGET_SPLITTER; return 1; }
    if (t == "SCROLLPANEL") { if (out_type) *out_type = DOMUI_WIDGET_SCROLLPANEL; return 1; }
    if (t == "TABS") { if (out_type) *out_type = DOMUI_WIDGET_TABS; return 1; }
    if (t == "TAB_PAGE") { if (out_type) *out_type = DOMUI_WIDGET_TAB_PAGE; return 1; }
    return 0;
}

static int domui_ops_dock_from_string(const std::string& text, domui_dock_mode* out_mode)
{
    std::string t = domui_ops_upper(text);
    if (t == "NONE") { if (out_mode) *out_mode = DOMUI_DOCK_NONE; return 1; }
    if (t == "LEFT") { if (out_mode) *out_mode = DOMUI_DOCK_LEFT; return 1; }
    if (t == "RIGHT") { if (out_mode) *out_mode = DOMUI_DOCK_RIGHT; return 1; }
    if (t == "TOP") { if (out_mode) *out_mode = DOMUI_DOCK_TOP; return 1; }
    if (t == "BOTTOM") { if (out_mode) *out_mode = DOMUI_DOCK_BOTTOM; return 1; }
    if (t == "FILL") { if (out_mode) *out_mode = DOMUI_DOCK_FILL; return 1; }
    return 0;
}

static int domui_ops_layout_from_string(const std::string& text, domui_container_layout_mode* out_mode)
{
    std::string t = domui_ops_upper(text);
    if (t == "ABSOLUTE") { if (out_mode) *out_mode = DOMUI_LAYOUT_ABSOLUTE; return 1; }
    if (t == "STACK_ROW") { if (out_mode) *out_mode = DOMUI_LAYOUT_STACK_ROW; return 1; }
    if (t == "STACK_COL") { if (out_mode) *out_mode = DOMUI_LAYOUT_STACK_COL; return 1; }
    if (t == "GRID") { if (out_mode) *out_mode = DOMUI_LAYOUT_GRID; return 1; }
    return 0;
}

static int domui_ops_parse_anchor_list(domui_ops_context* ctx, const domui_json_value& v, domui_u32* out_mask)
{
    domui_u32 mask = 0u;
    if (v.type != DOMUI_JSON_ARRAY) {
        domui_ops_add_error(ctx, "ops: anchors must be array", 0u);
        return 0;
    }
    for (size_t i = 0u; i < v.array.size(); ++i) {
        if (v.array[i].type != DOMUI_JSON_STRING) {
            domui_ops_add_error(ctx, "ops: anchor must be string", 0u);
            return 0;
        }
        std::string a = domui_ops_upper(v.array[i].string_value);
        if (a == "L" || a == "LEFT") {
            mask |= DOMUI_ANCHOR_L;
        } else if (a == "R" || a == "RIGHT") {
            mask |= DOMUI_ANCHOR_R;
        } else if (a == "T" || a == "TOP") {
            mask |= DOMUI_ANCHOR_T;
        } else if (a == "B" || a == "BOTTOM") {
            mask |= DOMUI_ANCHOR_B;
        } else {
            domui_ops_add_error(ctx, "ops: unknown anchor", 0u);
            return 0;
        }
    }
    if (out_mask) {
        *out_mask = mask;
    }
    return 1;
}

static int domui_ops_parse_box(domui_ops_context* ctx,
                               const domui_json_value& v,
                               domui_box* out_box,
                               const char* label)
{
    const char* ctx_label = label ? label : "box";
    static const char* kFields[] = { "l", "r", "t", "b" };
    const domui_json_value* lv;
    const domui_json_value* rv;
    const domui_json_value* tv;
    const domui_json_value* bv;
    if (!out_box) {
        return 0;
    }
    if (!domui_ops_check_unknown_fields(v, kFields, sizeof(kFields) / sizeof(kFields[0]),
                                        ctx ? ctx->diag : 0,
                                        ctx ? ctx->context_label.c_str() : "ops",
                                        ctx ? ctx->strict : 1)) {
        return 0;
    }
    lv = domui_ops_require_member(ctx, v, "l");
    rv = domui_ops_require_member(ctx, v, "r");
    tv = domui_ops_require_member(ctx, v, "t");
    bv = domui_ops_require_member(ctx, v, "b");
    if (!lv || !rv || !tv || !bv) {
        return 0;
    }
    if (!domui_ops_parse_int(*lv, &out_box->left) ||
        !domui_ops_parse_int(*rv, &out_box->right) ||
        !domui_ops_parse_int(*tv, &out_box->top) ||
        !domui_ops_parse_int(*bv, &out_box->bottom)) {
        std::string msg = std::string("ops: invalid ") + ctx_label;
        domui_ops_add_error(ctx, msg.c_str(), 0u);
        return 0;
    }
    return 1;
}

static int domui_ops_parse_constraints(domui_ops_context* ctx, const domui_json_value& v, domui_widget* w)
{
    static const char* kFields[] = { "min_w", "min_h", "max_w", "max_h" };
    const domui_json_value* min_w;
    const domui_json_value* min_h;
    const domui_json_value* max_w;
    const domui_json_value* max_h;
    if (!w) {
        return 0;
    }
    if (!domui_ops_check_unknown_fields(v, kFields, sizeof(kFields) / sizeof(kFields[0]),
                                        ctx ? ctx->diag : 0,
                                        ctx ? ctx->context_label.c_str() : "ops",
                                        ctx ? ctx->strict : 1)) {
        return 0;
    }
    min_w = domui_ops_require_member(ctx, v, "min_w");
    min_h = domui_ops_require_member(ctx, v, "min_h");
    max_w = domui_ops_require_member(ctx, v, "max_w");
    max_h = domui_ops_require_member(ctx, v, "max_h");
    if (!min_w || !min_h || !max_w || !max_h) {
        return 0;
    }
    if (!domui_ops_parse_int(*min_w, &w->min_w) ||
        !domui_ops_parse_int(*min_h, &w->min_h) ||
        !domui_ops_parse_int(*max_w, &w->max_w) ||
        !domui_ops_parse_int(*max_h, &w->max_h)) {
        domui_ops_add_error(ctx, "ops: invalid constraints", 0u);
        return 0;
    }
    return 1;
}

static int domui_ops_parse_vec2i(domui_ops_context* ctx, const domui_json_value& v, domui_vec2i* out_value)
{
    static const char* kFields[] = { "x", "y" };
    const domui_json_value* xv;
    const domui_json_value* yv;
    if (!out_value) {
        return 0;
    }
    if (!domui_ops_check_unknown_fields(v, kFields, sizeof(kFields) / sizeof(kFields[0]),
                                        ctx ? ctx->diag : 0,
                                        ctx ? ctx->context_label.c_str() : "ops",
                                        ctx ? ctx->strict : 1)) {
        return 0;
    }
    xv = domui_ops_require_member(ctx, v, "x");
    yv = domui_ops_require_member(ctx, v, "y");
    if (!xv || !yv) {
        return 0;
    }
    if (!domui_ops_parse_int(*xv, &out_value->x) ||
        !domui_ops_parse_int(*yv, &out_value->y)) {
        domui_ops_add_error(ctx, "ops: invalid vec2i", 0u);
        return 0;
    }
    return 1;
}

static int domui_ops_parse_recti(domui_ops_context* ctx, const domui_json_value& v, domui_recti* out_value)
{
    static const char* kFields[] = { "x", "y", "w", "h" };
    const domui_json_value* xv;
    const domui_json_value* yv;
    const domui_json_value* wv;
    const domui_json_value* hv;
    if (!out_value) {
        return 0;
    }
    if (!domui_ops_check_unknown_fields(v, kFields, sizeof(kFields) / sizeof(kFields[0]),
                                        ctx ? ctx->diag : 0,
                                        ctx ? ctx->context_label.c_str() : "ops",
                                        ctx ? ctx->strict : 1)) {
        return 0;
    }
    xv = domui_ops_require_member(ctx, v, "x");
    yv = domui_ops_require_member(ctx, v, "y");
    wv = domui_ops_require_member(ctx, v, "w");
    hv = domui_ops_require_member(ctx, v, "h");
    if (!xv || !yv || !wv || !hv) {
        return 0;
    }
    if (!domui_ops_parse_int(*xv, &out_value->x) ||
        !domui_ops_parse_int(*yv, &out_value->y) ||
        !domui_ops_parse_int(*wv, &out_value->w) ||
        !domui_ops_parse_int(*hv, &out_value->h)) {
        domui_ops_add_error(ctx, "ops: invalid recti", 0u);
        return 0;
    }
    return 1;
}

static void domui_ops_split_path(const std::string& path, std::vector<std::string>& out_parts)
{
    size_t i = 0u;
    out_parts.clear();
    while (i < path.size()) {
        size_t start;
        while (i < path.size() && (path[i] == '/' || path[i] == '\\')) {
            i++;
        }
        start = i;
        while (i < path.size() && path[i] != '/' && path[i] != '\\') {
            i++;
        }
        if (start < i) {
            out_parts.push_back(path.substr(start, i - start));
        }
    }
}

static int domui_ops_find_child_by_name(domui_doc* doc,
                                        domui_widget_id parent_id,
                                        const std::string& name,
                                        domui_widget_id* out_id,
                                        int* out_count)
{
    std::vector<domui_widget_id> children;
    int count = 0;
    domui_widget_id match = 0u;
    domui_string key(name.c_str());
    if (doc) {
        doc->enumerate_children(parent_id, children);
        for (size_t i = 0u; i < children.size(); ++i) {
            const domui_widget* w = doc->find_by_id(children[i]);
            if (w && domui_string_equal(w->name, key)) {
                count += 1;
                match = w->id;
            }
        }
    }
    if (out_id) {
        *out_id = match;
    }
    if (out_count) {
        *out_count = count;
    }
    return count;
}

static int domui_ops_resolve_path(domui_ops_context* ctx, const std::string& path, domui_widget_id* out_id)
{
    std::vector<std::string> parts;
    domui_widget_id parent = 0u;
    domui_ops_split_path(path, parts);
    if (parts.empty()) {
        domui_ops_add_error(ctx, "ops: empty path", 0u);
        return 0;
    }
    for (size_t i = 0u; i < parts.size(); ++i) {
        domui_widget_id child = 0u;
        int count = 0;
        domui_ops_find_child_by_name(ctx->doc, parent, parts[i], &child, &count);
        if (count == 0) {
            domui_ops_add_error(ctx, "ops: path not found", 0u);
            return 0;
        }
        if (count > 1) {
            domui_ops_add_error(ctx, "ops: path is ambiguous", 0u);
            return 0;
        }
        parent = child;
    }
    if (out_id) {
        *out_id = parent;
    }
    return 1;
}

static int domui_ops_resolve_query(domui_ops_context* ctx,
                                   const domui_json_value& query,
                                   domui_widget_id* out_id)
{
    std::string name;
    std::string type_text;
    domui_widget_type type = DOMUI_WIDGET_CONTAINER;
    int has_name = 0;
    int has_type = 0;
    static const char* kQueryFields[] = { "name", "type" };
    if (!domui_ops_check_unknown_fields(query,
                                        kQueryFields,
                                        sizeof(kQueryFields) / sizeof(kQueryFields[0]),
                                        ctx ? ctx->diag : 0,
                                        ctx ? ctx->context_label.c_str() : "ops",
                                        ctx ? ctx->strict : 1)) {
        return 0;
    }
    {
        const domui_json_value* v = domui_json_find_member(query, "name");
        if (v) {
            if (!domui_ops_parse_string(*v, name)) {
                domui_ops_add_error(ctx, "ops: query name must be string", 0u);
                return 0;
            }
            has_name = 1;
        }
    }
    {
        const domui_json_value* v = domui_json_find_member(query, "type");
        if (v) {
            if (!domui_ops_parse_string(*v, type_text) ||
                !domui_ops_widget_type_from_string(type_text, &type)) {
                domui_ops_add_error(ctx, "ops: query type invalid", 0u);
                return 0;
            }
            has_type = 1;
        }
    }
    if (!has_name && !has_type) {
        domui_ops_add_error(ctx, "ops: query requires name or type", 0u);
        return 0;
    }
    {
        std::vector<domui_widget_id> order;
        domui_widget_id match = 0u;
        int count = 0;
        domui_string key(name.c_str());
        ctx->doc->canonical_widget_order(order);
        for (size_t i = 0u; i < order.size(); ++i) {
            const domui_widget* w = ctx->doc->find_by_id(order[i]);
            if (!w) {
                continue;
            }
            if (has_name && !domui_string_equal(w->name, key)) {
                continue;
            }
            if (has_type && w->type != type) {
                continue;
            }
            count += 1;
            match = w->id;
        }
        if (count == 0) {
            domui_ops_add_error(ctx, "ops: query not found", 0u);
            return 0;
        }
        if (count > 1) {
            domui_ops_add_error(ctx, "ops: query is ambiguous", 0u);
            return 0;
        }
        if (out_id) {
            *out_id = match;
        }
    }
    return 1;
}

static int domui_ops_resolve_selector(domui_ops_context* ctx,
                                      const domui_json_value& selector,
                                      domui_widget_id* out_id)
{
    const domui_json_value* v;
    static const char* kSelectorFields[] = { "id", "path", "query" };
    if (!domui_ops_check_unknown_fields(selector,
                                        kSelectorFields,
                                        sizeof(kSelectorFields) / sizeof(kSelectorFields[0]),
                                        ctx ? ctx->diag : 0,
                                        ctx ? ctx->context_label.c_str() : "ops",
                                        ctx ? ctx->strict : 1)) {
        return 0;
    }
    v = domui_json_find_member(selector, "id");
    if (v) {
        if (v->type == DOMUI_JSON_NUMBER) {
            domui_u32 id = 0u;
            if (!domui_ops_parse_u32(*v, &id) || id == 0u) {
                domui_ops_add_error(ctx, "ops: invalid id", 0u);
                return 0;
            }
            if (out_id) {
                *out_id = id;
            }
            return 1;
        }
        if (v->type == DOMUI_JSON_STRING) {
            std::string name;
            if (!domui_ops_parse_var_name(v->string_value, name)) {
                domui_ops_add_error(ctx, "ops: invalid id variable", 0u);
                return 0;
            }
            if (!ctx || !ctx->result) {
                domui_ops_add_error(ctx, "ops: variable map missing", 0u);
                return 0;
            }
            {
                std::map<std::string, domui_u32>::const_iterator it = ctx->result->created_ids.find(name);
                if (it == ctx->result->created_ids.end()) {
                    domui_ops_add_error(ctx, "ops: unknown id variable", 0u);
                    return 0;
                }
                if (out_id) {
                    *out_id = it->second;
                }
                return 1;
            }
        }
        domui_ops_add_error(ctx, "ops: id must be number or $var", 0u);
        return 0;
    }
    v = domui_json_find_member(selector, "path");
    if (v) {
        std::string path;
        if (!domui_ops_parse_string(*v, path)) {
            domui_ops_add_error(ctx, "ops: path must be string", 0u);
            return 0;
        }
        return domui_ops_resolve_path(ctx, path, out_id);
    }
    v = domui_json_find_member(selector, "query");
    if (v) {
        if (v->type != DOMUI_JSON_OBJECT) {
            domui_ops_add_error(ctx, "ops: query must be object", 0u);
            return 0;
        }
        return domui_ops_resolve_query(ctx, *v, out_id);
    }
    domui_ops_add_error(ctx, "ops: selector missing id/path/query", 0u);
    return 0;
}

static int domui_ops_parse_targets(domui_ops_context* ctx,
                                   const domui_json_value& v,
                                   domui_target_set& out_targets)
{
    if (v.type != DOMUI_JSON_ARRAY) {
        domui_ops_add_error(ctx, "ops: targets must be array", 0u);
        return 0;
    }
    domui_register_default_backend_caps();
    out_targets.backends.clear();
    out_targets.tiers.clear();
    for (size_t i = 0u; i < v.array.size(); ++i) {
        if (v.array[i].type != DOMUI_JSON_STRING) {
            domui_ops_add_error(ctx, "ops: target must be string", 0u);
            return 0;
        }
        const std::string& token = v.array[i].string_value;
        if (domui_get_backend_caps_cstr(token.c_str())) {
            out_targets.backends.push_back(domui_string(token.c_str()));
        } else {
            out_targets.tiers.push_back(domui_string(token.c_str()));
        }
    }
    return 1;
}

static int domui_ops_op_ensure_root(domui_ops_context* ctx, const domui_json_value& op)
{
    domui_widget_type type = DOMUI_WIDGET_CONTAINER;
    std::string name = ctx ? ctx->default_root_name : std::string("root");
    const domui_json_value* v;
    std::vector<domui_widget_id> roots;
    domui_widget_id root_id = 0u;
    static const char* kEnsureRootFields[] = { "op", "name", "type", "out" };
    if (!domui_ops_check_unknown_fields(op,
                                        kEnsureRootFields,
                                        sizeof(kEnsureRootFields) / sizeof(kEnsureRootFields[0]),
                                        ctx ? ctx->diag : 0,
                                        ctx ? ctx->context_label.c_str() : "ops",
                                        ctx ? ctx->strict : 1)) {
        return 0;
    }
    v = domui_json_find_member(op, "name");
    if (v) {
        if (!domui_ops_parse_string(*v, name)) {
            domui_ops_add_error(ctx, "ops: name must be string", 0u);
            return 0;
        }
    }
    v = domui_ops_require_member(ctx, op, "type");
    if (!v) {
        return 0;
    }
    {
        std::string type_text;
        if (!domui_ops_parse_string(*v, type_text) ||
            !domui_ops_widget_type_from_string(type_text, &type)) {
            domui_ops_add_error(ctx, "ops: invalid widget type", 0u);
            return 0;
        }
    }
    if (ctx && ctx->doc) {
        ctx->doc->enumerate_children(0u, roots);
    }
    if (roots.empty()) {
        root_id = ctx->doc->create_widget(type, 0u);
        if (root_id == 0u) {
            domui_ops_add_error(ctx, "ops: failed to create root", 0u);
            return 0;
        }
        {
            domui_widget* w = ctx->doc->find_by_id(root_id);
            if (w && !name.empty()) {
                w->name.set(name.c_str());
            }
        }
    } else if (name.empty()) {
        root_id = roots[0];
    } else {
        domui_widget_id match = 0u;
        int count = 0;
        domui_string key(name.c_str());
        for (size_t i = 0u; i < roots.size(); ++i) {
            const domui_widget* w = ctx->doc->find_by_id(roots[i]);
            if (w && domui_string_equal(w->name, key)) {
                count += 1;
                match = w->id;
            }
        }
        if (count == 1) {
            root_id = match;
        } else if (count == 0 && roots.size() == 1u) {
            domui_widget* w = ctx->doc->find_by_id(roots[0]);
            if (w && w->name.empty()) {
                w->name.set(name.c_str());
                root_id = w->id;
            } else {
                domui_ops_add_error(ctx, "ops: root name not found", 0u);
                return 0;
            }
        } else if (count > 1) {
            domui_ops_add_error(ctx, "ops: root name ambiguous", 0u);
            return 0;
        } else {
            domui_ops_add_error(ctx, "ops: root name not found", 0u);
            return 0;
        }
    }
    if (root_id == 0u) {
        domui_ops_add_error(ctx, "ops: root not resolved", 0u);
        return 0;
    }
    {
        domui_widget* w = ctx->doc->find_by_id(root_id);
        if (!w) {
            domui_ops_add_error(ctx, "ops: root not found", root_id);
            return 0;
        }
        if (w->type != type) {
            domui_ops_add_error(ctx, "ops: root type mismatch", root_id);
            return 0;
        }
    }
    v = domui_json_find_member(op, "out");
    if (!domui_ops_store_out(ctx, v, root_id)) {
        return 0;
    }
    return 1;
}

static int domui_ops_op_create_widget(domui_ops_context* ctx, const domui_json_value& op)
{
    domui_widget_type type = DOMUI_WIDGET_CONTAINER;
    std::string name;
    std::string if_exists = "ERROR";
    domui_widget_id parent_id = 0u;
    domui_widget_id existing_id = 0u;
    int existing_count = 0;
    const domui_json_value* v;
    static const char* kCreateFields[] = { "op", "parent", "type", "name", "out", "if_exists" };
    if (!domui_ops_check_unknown_fields(op,
                                        kCreateFields,
                                        sizeof(kCreateFields) / sizeof(kCreateFields[0]),
                                        ctx ? ctx->diag : 0,
                                        ctx ? ctx->context_label.c_str() : "ops",
                                        ctx ? ctx->strict : 1)) {
        return 0;
    }
    v = domui_ops_require_member(ctx, op, "parent");
    if (!v || v->type != DOMUI_JSON_OBJECT) {
        domui_ops_add_error(ctx, "ops: parent must be selector", 0u);
        return 0;
    }
    if (!domui_ops_resolve_selector(ctx, *v, &parent_id)) {
        return 0;
    }
    v = domui_ops_require_member(ctx, op, "type");
    if (!v) {
        return 0;
    }
    {
        std::string type_text;
        if (!domui_ops_parse_string(*v, type_text) ||
            !domui_ops_widget_type_from_string(type_text, &type)) {
            domui_ops_add_error(ctx, "ops: invalid widget type", 0u);
            return 0;
        }
    }
    v = domui_ops_require_member(ctx, op, "name");
    if (!v) {
        return 0;
    }
    if (!domui_ops_parse_string(*v, name) || name.empty()) {
        domui_ops_add_error(ctx, "ops: name must be string", 0u);
        return 0;
    }
    v = domui_json_find_member(op, "if_exists");
    if (v) {
        std::string mode;
        if (!domui_ops_parse_string(*v, mode)) {
            domui_ops_add_error(ctx, "ops: if_exists must be string", 0u);
            return 0;
        }
        if_exists = domui_ops_upper(mode);
        if (if_exists != "ERROR" && if_exists != "REUSE" && if_exists != "REPLACE") {
            domui_ops_add_error(ctx, "ops: invalid if_exists", 0u);
            return 0;
        }
    }
    domui_ops_find_child_by_name(ctx->doc, parent_id, name, &existing_id, &existing_count);
    if (existing_count > 1) {
        domui_ops_add_error(ctx, "ops: name is ambiguous", 0u);
        return 0;
    }
    if (existing_count == 1) {
        if (if_exists == "REUSE") {
            domui_widget* w = domui_ops_require_widget(ctx, existing_id);
            if (!w) {
                return 0;
            }
            if (w->type != type) {
                domui_ops_add_error(ctx, "ops: existing widget type mismatch", existing_id);
                return 0;
            }
            v = domui_json_find_member(op, "out");
            return domui_ops_store_out(ctx, v, existing_id);
        }
        if (if_exists == "REPLACE") {
            if (!ctx->doc->delete_widget(existing_id)) {
                domui_ops_add_error(ctx, "ops: failed to delete existing widget", existing_id);
                return 0;
            }
        } else {
            domui_ops_add_error(ctx, "ops: name already exists", existing_id);
            return 0;
        }
    }
    {
        domui_widget_id new_id = ctx->doc->create_widget(type, parent_id);
        domui_widget* w = ctx->doc->find_by_id(new_id);
        if (new_id == 0u || !w) {
            domui_ops_add_error(ctx, "ops: failed to create widget", 0u);
            return 0;
        }
        w->name.set(name.c_str());
        v = domui_json_find_member(op, "out");
        return domui_ops_store_out(ctx, v, new_id);
    }
}

static int domui_ops_op_delete_widget(domui_ops_context* ctx, const domui_json_value& op)
{
    domui_widget_id id = 0u;
    const domui_json_value* v;
    static const char* kDeleteFields[] = { "op", "target", "out" };
    if (!domui_ops_check_unknown_fields(op,
                                        kDeleteFields,
                                        sizeof(kDeleteFields) / sizeof(kDeleteFields[0]),
                                        ctx ? ctx->diag : 0,
                                        ctx ? ctx->context_label.c_str() : "ops",
                                        ctx ? ctx->strict : 1)) {
        return 0;
    }
    v = domui_ops_require_member(ctx, op, "target");
    if (!v || v->type != DOMUI_JSON_OBJECT) {
        domui_ops_add_error(ctx, "ops: target must be selector", 0u);
        return 0;
    }
    if (!domui_ops_resolve_selector(ctx, *v, &id)) {
        return 0;
    }
    if (!ctx->doc->delete_widget(id)) {
        domui_ops_add_error(ctx, "ops: delete failed", id);
        return 0;
    }
    v = domui_json_find_member(op, "out");
    return domui_ops_store_out(ctx, v, id);
}

static int domui_ops_op_rename_widget(domui_ops_context* ctx, const domui_json_value& op)
{
    domui_widget_id id = 0u;
    std::string name;
    const domui_json_value* v;
    static const char* kRenameFields[] = { "op", "target", "name", "out" };
    if (!domui_ops_check_unknown_fields(op,
                                        kRenameFields,
                                        sizeof(kRenameFields) / sizeof(kRenameFields[0]),
                                        ctx ? ctx->diag : 0,
                                        ctx ? ctx->context_label.c_str() : "ops",
                                        ctx ? ctx->strict : 1)) {
        return 0;
    }
    v = domui_ops_require_member(ctx, op, "target");
    if (!v || v->type != DOMUI_JSON_OBJECT) {
        domui_ops_add_error(ctx, "ops: target must be selector", 0u);
        return 0;
    }
    if (!domui_ops_resolve_selector(ctx, *v, &id)) {
        return 0;
    }
    v = domui_ops_require_member(ctx, op, "name");
    if (!v || !domui_ops_parse_string(*v, name) || name.empty()) {
        domui_ops_add_error(ctx, "ops: name must be string", id);
        return 0;
    }
    if (!ctx->doc->rename_widget(id, domui_string(name.c_str()))) {
        domui_ops_add_error(ctx, "ops: rename failed", id);
        return 0;
    }
    v = domui_json_find_member(op, "out");
    return domui_ops_store_out(ctx, v, id);
}

static int domui_ops_op_reparent_widget(domui_ops_context* ctx, const domui_json_value& op)
{
    domui_widget_id id = 0u;
    domui_widget_id new_parent = 0u;
    domui_u32 z_order = 0u;
    const domui_json_value* v;
    static const char* kReparentFields[] = { "op", "target", "new_parent", "z_order", "out" };
    if (!domui_ops_check_unknown_fields(op,
                                        kReparentFields,
                                        sizeof(kReparentFields) / sizeof(kReparentFields[0]),
                                        ctx ? ctx->diag : 0,
                                        ctx ? ctx->context_label.c_str() : "ops",
                                        ctx ? ctx->strict : 1)) {
        return 0;
    }
    v = domui_ops_require_member(ctx, op, "target");
    if (!v || v->type != DOMUI_JSON_OBJECT) {
        domui_ops_add_error(ctx, "ops: target must be selector", 0u);
        return 0;
    }
    if (!domui_ops_resolve_selector(ctx, *v, &id)) {
        return 0;
    }
    v = domui_ops_require_member(ctx, op, "new_parent");
    if (!v || v->type != DOMUI_JSON_OBJECT) {
        domui_ops_add_error(ctx, "ops: new_parent must be selector", id);
        return 0;
    }
    if (!domui_ops_resolve_selector(ctx, *v, &new_parent)) {
        return 0;
    }
    v = domui_ops_require_member(ctx, op, "z_order");
    if (!v || !domui_ops_parse_u32(*v, &z_order)) {
        domui_ops_add_error(ctx, "ops: z_order must be uint", id);
        return 0;
    }
    if (!ctx->doc->reparent_widget(id, new_parent, z_order)) {
        domui_ops_add_error(ctx, "ops: reparent failed", id);
        return 0;
    }
    v = domui_json_find_member(op, "out");
    return domui_ops_store_out(ctx, v, id);
}

static int domui_ops_op_set_rect(domui_ops_context* ctx, const domui_json_value& op)
{
    domui_widget_id id = 0u;
    int x = 0;
    int y = 0;
    int w = 0;
    int h = 0;
    const domui_json_value* v;
    static const char* kSetRectFields[] = { "op", "target", "x", "y", "w", "h", "out" };
    if (!domui_ops_check_unknown_fields(op,
                                        kSetRectFields,
                                        sizeof(kSetRectFields) / sizeof(kSetRectFields[0]),
                                        ctx ? ctx->diag : 0,
                                        ctx ? ctx->context_label.c_str() : "ops",
                                        ctx ? ctx->strict : 1)) {
        return 0;
    }
    v = domui_ops_require_member(ctx, op, "target");
    if (!v || v->type != DOMUI_JSON_OBJECT) {
        domui_ops_add_error(ctx, "ops: target must be selector", 0u);
        return 0;
    }
    if (!domui_ops_resolve_selector(ctx, *v, &id)) {
        return 0;
    }
    v = domui_ops_require_member(ctx, op, "x");
    if (!v || !domui_ops_parse_int(*v, &x)) {
        domui_ops_add_error(ctx, "ops: invalid x", id);
        return 0;
    }
    v = domui_ops_require_member(ctx, op, "y");
    if (!v || !domui_ops_parse_int(*v, &y)) {
        domui_ops_add_error(ctx, "ops: invalid y", id);
        return 0;
    }
    v = domui_ops_require_member(ctx, op, "w");
    if (!v || !domui_ops_parse_int(*v, &w)) {
        domui_ops_add_error(ctx, "ops: invalid w", id);
        return 0;
    }
    v = domui_ops_require_member(ctx, op, "h");
    if (!v || !domui_ops_parse_int(*v, &h)) {
        domui_ops_add_error(ctx, "ops: invalid h", id);
        return 0;
    }
    if (!ctx->doc->set_rect(id, x, y, w, h)) {
        domui_ops_add_error(ctx, "ops: set_rect failed", id);
        return 0;
    }
    v = domui_json_find_member(op, "out");
    return domui_ops_store_out(ctx, v, id);
}

static int domui_ops_op_set_layout(domui_ops_context* ctx, const domui_json_value& op)
{
    domui_widget_id id = 0u;
    domui_dock_mode dock = DOMUI_DOCK_NONE;
    domui_u32 anchors = 0u;
    domui_box margin;
    const domui_json_value* v;
    domui_widget* w;
    static const char* kSetLayoutFields[] = { "op", "target", "dock", "anchors", "margins", "constraints", "out" };
    if (!domui_ops_check_unknown_fields(op,
                                        kSetLayoutFields,
                                        sizeof(kSetLayoutFields) / sizeof(kSetLayoutFields[0]),
                                        ctx ? ctx->diag : 0,
                                        ctx ? ctx->context_label.c_str() : "ops",
                                        ctx ? ctx->strict : 1)) {
        return 0;
    }
    v = domui_ops_require_member(ctx, op, "target");
    if (!v || v->type != DOMUI_JSON_OBJECT) {
        domui_ops_add_error(ctx, "ops: target must be selector", 0u);
        return 0;
    }
    if (!domui_ops_resolve_selector(ctx, *v, &id)) {
        return 0;
    }
    w = domui_ops_require_widget(ctx, id);
    if (!w) {
        return 0;
    }
    v = domui_ops_require_member(ctx, op, "dock");
    if (!v) {
        return 0;
    }
    {
        std::string dock_text;
        if (!domui_ops_parse_string(*v, dock_text) ||
            !domui_ops_dock_from_string(dock_text, &dock)) {
            domui_ops_add_error(ctx, "ops: invalid dock", id);
            return 0;
        }
    }
    v = domui_ops_require_member(ctx, op, "anchors");
    if (!v || !domui_ops_parse_anchor_list(ctx, *v, &anchors)) {
        return 0;
    }
    v = domui_ops_require_member(ctx, op, "margins");
    if (!v || v->type != DOMUI_JSON_OBJECT) {
        domui_ops_add_error(ctx, "ops: margins must be object", id);
        return 0;
    }
    if (!domui_ops_parse_box(ctx, *v, &margin, "margins")) {
        return 0;
    }
    v = domui_ops_require_member(ctx, op, "constraints");
    if (!v || v->type != DOMUI_JSON_OBJECT) {
        domui_ops_add_error(ctx, "ops: constraints must be object", id);
        return 0;
    }
    if (!domui_ops_parse_constraints(ctx, *v, w)) {
        return 0;
    }
    if (!ctx->doc->set_layout(id, dock, anchors, margin)) {
        domui_ops_add_error(ctx, "ops: set_layout failed", id);
        return 0;
    }
    v = domui_json_find_member(op, "out");
    return domui_ops_store_out(ctx, v, id);
}

static int domui_ops_op_set_container_layout(domui_ops_context* ctx, const domui_json_value& op)
{
    domui_widget_id id = 0u;
    domui_container_layout_mode mode = DOMUI_LAYOUT_ABSOLUTE;
    const domui_json_value* v;
    const domui_json_value* params;
    domui_widget* w;
    static const char* kSetContainerFields[] = { "op", "target", "mode", "params", "out" };
    if (!domui_ops_check_unknown_fields(op,
                                        kSetContainerFields,
                                        sizeof(kSetContainerFields) / sizeof(kSetContainerFields[0]),
                                        ctx ? ctx->diag : 0,
                                        ctx ? ctx->context_label.c_str() : "ops",
                                        ctx ? ctx->strict : 1)) {
        return 0;
    }
    v = domui_ops_require_member(ctx, op, "target");
    if (!v || v->type != DOMUI_JSON_OBJECT) {
        domui_ops_add_error(ctx, "ops: target must be selector", 0u);
        return 0;
    }
    if (!domui_ops_resolve_selector(ctx, *v, &id)) {
        return 0;
    }
    w = domui_ops_require_widget(ctx, id);
    if (!w) {
        return 0;
    }
    v = domui_ops_require_member(ctx, op, "mode");
    if (!v) {
        return 0;
    }
    {
        std::string mode_text;
        if (!domui_ops_parse_string(*v, mode_text) ||
            !domui_ops_layout_from_string(mode_text, &mode)) {
            domui_ops_add_error(ctx, "ops: invalid layout mode", id);
            return 0;
        }
    }
    w->layout_mode = mode;
    params = domui_json_find_member(op, "params");
    if (params) {
        if (params->type != DOMUI_JSON_OBJECT) {
            domui_ops_add_error(ctx, "ops: params must be object", id);
            return 0;
        }
        if (!params->object.empty()) {
            domui_ops_add_warning(ctx, "ops: params ignored", id);
        }
    }
    v = domui_json_find_member(op, "out");
    return domui_ops_store_out(ctx, v, id);
}

static int domui_ops_op_set_prop(domui_ops_context* ctx, const domui_json_value& op)
{
    domui_widget_id id = 0u;
    std::string key;
    domui_value value;
    const domui_json_value* v;
    static const char* kSetPropFields[] = { "op", "target", "key", "value", "out" };
    static const char* kValueFields[] = { "type", "v" };
    if (!domui_ops_check_unknown_fields(op,
                                        kSetPropFields,
                                        sizeof(kSetPropFields) / sizeof(kSetPropFields[0]),
                                        ctx ? ctx->diag : 0,
                                        ctx ? ctx->context_label.c_str() : "ops",
                                        ctx ? ctx->strict : 1)) {
        return 0;
    }
    v = domui_ops_require_member(ctx, op, "target");
    if (!v || v->type != DOMUI_JSON_OBJECT) {
        domui_ops_add_error(ctx, "ops: target must be selector", 0u);
        return 0;
    }
    if (!domui_ops_resolve_selector(ctx, *v, &id)) {
        return 0;
    }
    v = domui_ops_require_member(ctx, op, "key");
    if (!v || !domui_ops_parse_string(*v, key) || key.empty()) {
        domui_ops_add_error(ctx, "ops: key must be string", id);
        return 0;
    }
    v = domui_ops_require_member(ctx, op, "value");
    if (!v || v->type != DOMUI_JSON_OBJECT) {
        domui_ops_add_error(ctx, "ops: value must be object", id);
        return 0;
    }
    if (!domui_ops_check_unknown_fields(*v,
                                        kValueFields,
                                        sizeof(kValueFields) / sizeof(kValueFields[0]),
                                        ctx ? ctx->diag : 0,
                                        ctx ? ctx->context_label.c_str() : "ops",
                                        ctx ? ctx->strict : 1)) {
        return 0;
    }
    {
        const domui_json_value* type_val = domui_ops_require_member(ctx, *v, "type");
        const domui_json_value* val_val = domui_ops_require_member(ctx, *v, "v");
        std::string type_text;
        if (!type_val || !val_val) {
            return 0;
        }
        if (!domui_ops_parse_string(*type_val, type_text)) {
            domui_ops_add_error(ctx, "ops: value.type must be string", id);
            return 0;
        }
        type_text = domui_ops_upper(type_text);
        if (type_text == "INT") {
            int iv = 0;
            if (!domui_ops_parse_int(*val_val, &iv)) {
                domui_ops_add_error(ctx, "ops: value.v must be int", id);
                return 0;
            }
            value = domui_value_int(iv);
        } else if (type_text == "UINT") {
            domui_u32 uv = 0u;
            if (!domui_ops_parse_u32(*val_val, &uv)) {
                domui_ops_add_error(ctx, "ops: value.v must be uint", id);
                return 0;
            }
            value = domui_value_uint(uv);
        } else if (type_text == "BOOL") {
            int bv = 0;
            if (val_val->type == DOMUI_JSON_BOOL) {
                bv = val_val->bool_value ? 1 : 0;
            } else if (!ctx->strict && val_val->type == DOMUI_JSON_NUMBER) {
                int iv = 0;
                if (!domui_ops_parse_int(*val_val, &iv) || (iv != 0 && iv != 1)) {
                    domui_ops_add_error(ctx, "ops: value.v must be bool", id);
                    return 0;
                }
                bv = iv;
                domui_ops_add_warning(ctx, "ops: coerced bool from number", id);
            } else {
                domui_ops_add_error(ctx, "ops: value.v must be bool", id);
                return 0;
            }
            value = domui_value_bool(bv);
        } else if (type_text == "STRING") {
            std::string sv;
            if (!domui_ops_parse_string(*val_val, sv)) {
                domui_ops_add_error(ctx, "ops: value.v must be string", id);
                return 0;
            }
            value = domui_value_string(domui_string(sv.c_str()));
        } else if (type_text == "VEC2I") {
            domui_vec2i vv;
            if (val_val->type != DOMUI_JSON_OBJECT || !domui_ops_parse_vec2i(ctx, *val_val, &vv)) {
                return 0;
            }
            value = domui_value_vec2i(vv);
        } else if (type_text == "RECTI") {
            domui_recti rv;
            if (val_val->type != DOMUI_JSON_OBJECT || !domui_ops_parse_recti(ctx, *val_val, &rv)) {
                return 0;
            }
            value = domui_value_recti(rv);
        } else {
            domui_ops_add_error(ctx, "ops: unknown value.type", id);
            return 0;
        }
    }
    {
        domui_widget* w = domui_ops_require_widget(ctx, id);
        if (!w) {
            return 0;
        }
        if (!w->props.set(key.c_str(), value)) {
            domui_ops_add_error(ctx, "ops: set_prop failed", id);
            return 0;
        }
    }
    v = domui_json_find_member(op, "out");
    return domui_ops_store_out(ctx, v, id);
}

static int domui_ops_op_bind_event(domui_ops_context* ctx, const domui_json_value& op)
{
    domui_widget_id id = 0u;
    std::string event_name;
    std::string action;
    const domui_json_value* v;
    static const char* kBindFields[] = { "op", "target", "event", "action", "out" };
    if (!domui_ops_check_unknown_fields(op,
                                        kBindFields,
                                        sizeof(kBindFields) / sizeof(kBindFields[0]),
                                        ctx ? ctx->diag : 0,
                                        ctx ? ctx->context_label.c_str() : "ops",
                                        ctx ? ctx->strict : 1)) {
        return 0;
    }
    v = domui_ops_require_member(ctx, op, "target");
    if (!v || v->type != DOMUI_JSON_OBJECT) {
        domui_ops_add_error(ctx, "ops: target must be selector", 0u);
        return 0;
    }
    if (!domui_ops_resolve_selector(ctx, *v, &id)) {
        return 0;
    }
    v = domui_ops_require_member(ctx, op, "event");
    if (!v || !domui_ops_parse_string(*v, event_name) || event_name.empty()) {
        domui_ops_add_error(ctx, "ops: event must be string", id);
        return 0;
    }
    v = domui_ops_require_member(ctx, op, "action");
    if (!v || !domui_ops_parse_string(*v, action) || action.empty()) {
        domui_ops_add_error(ctx, "ops: action must be string", id);
        return 0;
    }
    {
        domui_widget* w = domui_ops_require_widget(ctx, id);
        if (!w) {
            return 0;
        }
        w->events.set(event_name.c_str(), action.c_str());
    }
    v = domui_json_find_member(op, "out");
    return domui_ops_store_out(ctx, v, id);
}

static int domui_ops_op_validate(domui_ops_context* ctx, const domui_json_value& op)
{
    domui_target_set targets;
    domui_target_set* target_ptr = 0;
    domui_diag vdiag;
    int fail_on_warning = 0;
    const domui_json_value* v;
    static const char* kValidateFields[] = { "op", "targets", "fail_on_warning" };
    if (!domui_ops_check_unknown_fields(op,
                                        kValidateFields,
                                        sizeof(kValidateFields) / sizeof(kValidateFields[0]),
                                        ctx ? ctx->diag : 0,
                                        ctx ? ctx->context_label.c_str() : "ops",
                                        ctx ? ctx->strict : 1)) {
        return 0;
    }
    v = domui_json_find_member(op, "targets");
    if (v) {
        if (!domui_ops_parse_targets(ctx, *v, targets)) {
            return 0;
        }
        target_ptr = &targets;
    }
    v = domui_json_find_member(op, "fail_on_warning");
    if (v) {
        if (!domui_ops_parse_bool(*v, &fail_on_warning)) {
            domui_ops_add_error(ctx, "ops: fail_on_warning must be bool", 0u);
            return 0;
        }
    }
    if (!domui_validate_doc(ctx->doc, target_ptr, &vdiag)) {
        if (ctx && ctx->result) {
            ctx->result->validation_failed = true;
        }
    }
    if (fail_on_warning && vdiag.warning_count() > 0u) {
        if (ctx && ctx->result) {
            ctx->result->validation_failed = true;
        }
        domui_ops_add_error(ctx, "ops: warnings treated as errors", 0u);
    }
    domui_ops_append_diag(ctx ? ctx->diag : 0, vdiag);
    if (ctx && ctx->result && ctx->result->validation_failed) {
        ctx->stop = 1;
    }
    return 1;
}

static int domui_ops_op_save(domui_ops_context* ctx, const domui_json_value& op)
{
    static const char* kSaveFields[] = { "op" };
    if (!domui_ops_check_unknown_fields(op,
                                        kSaveFields,
                                        sizeof(kSaveFields) / sizeof(kSaveFields[0]),
                                        ctx ? ctx->diag : 0,
                                        ctx ? ctx->context_label.c_str() : "ops",
                                        ctx ? ctx->strict : 1)) {
        return 0;
    }
    if (!ctx || !ctx->params || !ctx->params->save_fn) {
        domui_ops_add_error(ctx, "ops: save not available", 0u);
        return 0;
    }
    if (!ctx->params->save_fn(ctx->params->save_user, ctx->doc, ctx->diag)) {
        if (ctx->result) {
            ctx->result->save_failed = true;
        }
        ctx->stop = 1;
    }
    return 1;
}

static int domui_ops_apply_op(domui_ops_context* ctx, const domui_json_value& op)
{
    const domui_json_value* v;
    std::string op_name;
    if (op.type != DOMUI_JSON_OBJECT) {
        domui_ops_add_error(ctx, "ops: op must be object", 0u);
        return 0;
    }
    v = domui_ops_require_member(ctx, op, "op");
    if (!v || !domui_ops_parse_string(*v, op_name) || op_name.empty()) {
        domui_ops_add_error(ctx, "ops: op name missing", 0u);
        return 0;
    }
    ctx->op_name = op_name;
    domui_ops_update_context_label(ctx);
    if (op_name == "ensure_root") {
        return domui_ops_op_ensure_root(ctx, op);
    }
    if (op_name == "create_widget") {
        return domui_ops_op_create_widget(ctx, op);
    }
    if (op_name == "delete_widget") {
        return domui_ops_op_delete_widget(ctx, op);
    }
    if (op_name == "rename_widget") {
        return domui_ops_op_rename_widget(ctx, op);
    }
    if (op_name == "reparent_widget") {
        return domui_ops_op_reparent_widget(ctx, op);
    }
    if (op_name == "set_rect") {
        return domui_ops_op_set_rect(ctx, op);
    }
    if (op_name == "set_layout") {
        return domui_ops_op_set_layout(ctx, op);
    }
    if (op_name == "set_container_layout") {
        return domui_ops_op_set_container_layout(ctx, op);
    }
    if (op_name == "set_prop") {
        return domui_ops_op_set_prop(ctx, op);
    }
    if (op_name == "bind_event") {
        return domui_ops_op_bind_event(ctx, op);
    }
    if (op_name == "validate") {
        return domui_ops_op_validate(ctx, op);
    }
    if (op_name == "save") {
        return domui_ops_op_save(ctx, op);
    }
    domui_ops_add_error(ctx, "ops: unknown op", 0u);
    return 0;
}

bool domui_ops_apply_json(domui_doc* doc,
                          const char* json_text,
                          size_t json_len,
                          const domui_ops_apply_params* params,
                          domui_ops_result* out_result,
                          domui_diag* out_diag)
{
    domui_json_parser parser;
    domui_json_value root;
    domui_ops_result result;
    domui_ops_context ctx;
    int strict = 1;
    domui_u32 version = 0u;
    std::string docname;
    std::string default_root = "root";
    const domui_json_value* v;
    if (!doc || !json_text) {
        if (out_diag) {
            out_diag->add_error("ops: invalid input", 0u, "ops");
        }
        return false;
    }
    parser.start = json_text;
    parser.cur = json_text;
    parser.end = json_text + json_len;
    parser.diag = out_diag;
    if (!domui_json_parse(&parser, root)) {
        return false;
    }
    if (root.type != DOMUI_JSON_OBJECT) {
        if (out_diag) {
            out_diag->add_error("ops: root must be object", 0u, "ops");
        }
        return false;
    }
    v = domui_json_find_member(root, "strict");
    if (v) {
        if (!domui_ops_parse_bool(*v, &strict)) {
            if (out_diag) {
                out_diag->add_error("ops: strict must be bool", 0u, "ops");
            }
            return false;
        }
    }
    {
        static const char* kRootFields[] = {
            "version",
            "docname",
            "defaults",
            "ops",
            "strict",
            "validate"
        };
        if (!domui_ops_check_unknown_fields(root,
                                            kRootFields,
                                            sizeof(kRootFields) / sizeof(kRootFields[0]),
                                            out_diag,
                                            "ops",
                                            strict)) {
            return false;
        }
    }
    v = domui_json_find_member(root, "version");
    if (!v || !domui_ops_parse_u32(*v, &version)) {
        if (out_diag) {
            out_diag->add_error("ops: missing or invalid version", 0u, "ops");
        }
        return false;
    }
    if (version != 1u) {
        if (out_diag) {
            out_diag->add_error("ops: unsupported version", 0u, "ops");
        }
        return false;
    }
    v = domui_json_find_member(root, "docname");
    if (v && domui_ops_parse_string(*v, docname) && !docname.empty()) {
        doc->meta.doc_name.set(docname.c_str());
    }
    v = domui_json_find_member(root, "validate");
    if (v) {
        int validate_flag = 1;
        if (!domui_ops_parse_bool(*v, &validate_flag)) {
            if (out_diag) {
                out_diag->add_error("ops: validate must be bool", 0u, "ops");
            }
            return false;
        }
        result.final_validate = validate_flag ? true : false;
    }
    v = domui_json_find_member(root, "defaults");
    if (v) {
        if (v->type != DOMUI_JSON_OBJECT) {
            if (out_diag) {
                out_diag->add_error("ops: defaults must be object", 0u, "ops");
            }
            return false;
        }
        {
            static const char* kDefaultsFields[] = {
                "root_name"
            };
            if (!domui_ops_check_unknown_fields(*v,
                                                kDefaultsFields,
                                                sizeof(kDefaultsFields) / sizeof(kDefaultsFields[0]),
                                                out_diag,
                                                "ops",
                                                strict)) {
                return false;
            }
        }
        {
            const domui_json_value* rv = domui_json_find_member(*v, "root_name");
            if (rv && !domui_ops_parse_string(*rv, default_root)) {
                if (out_diag) {
                    out_diag->add_error("ops: defaults.root_name must be string", 0u, "ops");
                }
                return false;
            }
        }
    }
    v = domui_json_find_member(root, "ops");
    if (!v || v->type != DOMUI_JSON_ARRAY) {
        if (out_diag) {
            out_diag->add_error("ops: missing or invalid ops array", 0u, "ops");
        }
        return false;
    }
    domui_register_default_backend_caps();
    ctx.doc = doc;
    ctx.diag = out_diag;
    ctx.result = &result;
    ctx.params = params;
    ctx.strict = strict;
    ctx.default_root_name = default_root;
    for (size_t i = 0u; i < v->array.size(); ++i) {
        ctx.op_index = i;
        ctx.op_name.clear();
        ctx.context_label.clear();
        if (!domui_ops_apply_op(&ctx, v->array[i])) {
            return false;
        }
        if (ctx.stop) {
            break;
        }
    }
    if (out_result) {
        *out_result = result;
    }
    return true;
}
