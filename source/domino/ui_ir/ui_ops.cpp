/*
FILE: source/domino/ui_ir/ui_ops.cpp
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / ui_ir ops
RESPONSIBILITY: Deterministic ops.json parsing and scripted edits for UI IR.
*/
#include "ui_ops.h"

#include <ctype.h>
#include <errno.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>

#include <vector>

enum domui_json_type {
    DOMUI_JSON_NULL = 0,
    DOMUI_JSON_BOOL,
    DOMUI_JSON_NUMBER,
    DOMUI_JSON_STRING,
    DOMUI_JSON_ARRAY,
    DOMUI_JSON_OBJECT
};

struct domui_json_value;

struct domui_json_member {
    std::string key;
    domui_json_value value;

    domui_json_member()
        : key(),
          value()
    {
    }
};

struct domui_json_value {
    domui_json_type type;
    int bool_value;
    std::string string_value;
    std::vector<domui_json_value> array;
    std::vector<domui_json_member> object;

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

static int domui_json_key_exists(const std::vector<domui_json_member>& members, const std::string& key)
{
    for (size_t i = 0u; i < members.size(); ++i) {
        if (members[i].key == key) {
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
        domui_json_member member;
        if (!domui_json_parse_string(p, key)) {
            return 0;
        }
        domui_json_skip_ws(p);
        if (p->cur >= p->end || *p->cur != ':') {
            domui_json_add_error(p, "ops: expected ':'");
            return 0;
        }
        p->cur++;
        if (!domui_json_parse_value(p, member.value)) {
            return 0;
        }
        if (domui_json_key_exists(out.object, key)) {
            domui_json_add_error(p, "ops: duplicate key");
            return 0;
        }
        member.key = key;
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
        if (obj.object[i].key == key) {
            return &obj.object[i].value;
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
                                          domui_diag* diag)
{
    if (!diag) {
        return 0;
    }
    if (obj.type != DOMUI_JSON_OBJECT) {
        diag->add_error("ops: expected object", 0u, "ops");
        return 0;
    }
    for (size_t i = 0u; i < obj.object.size(); ++i) {
        size_t j;
        int found = 0;
        for (j = 0u; j < allowed_count; ++j) {
            if (obj.object[i].key == allowed[j]) {
                found = 1;
                break;
            }
        }
        if (!found) {
            std::string msg = "ops: unknown field '" + obj.object[i].key + "'";
            diag->add_error(msg.c_str(), 0u, "ops");
            return 0;
        }
    }
    return 1;
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
    int strict = 1;
    domui_u32 version = 0u;
    std::string docname;
    const domui_json_value* v;
    (void)params;
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
        if (strict && !domui_ops_check_unknown_fields(root, kRootFields, sizeof(kRootFields) / sizeof(kRootFields[0]), out_diag)) {
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
    v = domui_json_find_member(root, "ops");
    if (!v || v->type != DOMUI_JSON_ARRAY) {
        if (out_diag) {
            out_diag->add_error("ops: missing or invalid ops array", 0u, "ops");
        }
        return false;
    }
    if (out_result) {
        *out_result = result;
    }
    return true;
}
