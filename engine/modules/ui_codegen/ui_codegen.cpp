/*
FILE: source/domino/ui_codegen/ui_codegen.cpp
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / ui_codegen
RESPONSIBILITY: Deterministic action codegen + registry handling.
*/
#include "ui_codegen.h"

#include <algorithm>
#include <cctype>
#include <cstdio>
#include <cstring>
#include <vector>

#if defined(_WIN32)
#include <direct.h>
#else
#include <sys/stat.h>
#include <sys/types.h>
#endif

#include "ui_ir_doc.h"
#include "ui_ir_fileio.h"
#include "ui_ir_tlv.h"

domui_action_registry::domui_action_registry()
    : next_id(1u),
      key_to_id()
{
}

domui_codegen_params::domui_codegen_params()
    : input_tlv_path(0),
      registry_path(0),
      out_gen_dir(0),
      out_user_dir(0),
      doc_name_override(0)
{
}

static int domui_file_exists(const char* path)
{
    FILE* f;
    if (!path) {
        return 0;
    }
    f = fopen(path, "rb");
    if (!f) {
        return 0;
    }
    fclose(f);
    return 1;
}

static void domui_mkdir_one(const char* path)
{
    if (!path || !path[0]) {
        return;
    }
#if defined(_WIN32)
    _mkdir(path);
#else
    mkdir(path, 0755);
#endif
}

static void domui_ensure_dir(const std::string& path)
{
    size_t i;
    if (path.empty()) {
        return;
    }
    for (i = 0u; i < path.size(); ++i) {
        if (path[i] == '/' || path[i] == '\\') {
            std::string part = path.substr(0u, i);
            if (!part.empty()) {
                domui_mkdir_one(part.c_str());
            }
        }
    }
    domui_mkdir_one(path.c_str());
}

static std::string domui_join_path(const std::string& a, const std::string& b)
{
    if (a.empty()) {
        return b;
    }
    if (b.empty()) {
        return a;
    }
    if (a[a.size() - 1u] == '/' || a[a.size() - 1u] == '\\') {
        return a + b;
    }
    return a + "/" + b;
}

static void domui_skip_ws(const char** p, const char* end)
{
    while (*p < end) {
        char c = **p;
        if (c != ' ' && c != '\t' && c != '\r' && c != '\n') {
            break;
        }
        (*p)++;
    }
}

static int domui_parse_char(const char** p, const char* end, char want)
{
    domui_skip_ws(p, end);
    if (*p >= end || **p != want) {
        return 0;
    }
    (*p)++;
    return 1;
}

static int domui_parse_string(const char** p, const char* end, std::string& out)
{
    const char* cur;
    out.clear();
    domui_skip_ws(p, end);
    if (*p >= end || **p != '"') {
        return 0;
    }
    (*p)++;
    cur = *p;
    while (cur < end) {
        char c = *cur;
        if (c == '"') {
            *p = cur + 1;
            return 1;
        }
        if (c == '\\') {
            cur++;
            if (cur >= end) {
                return 0;
            }
            c = *cur;
            if (c == '"' || c == '\\' || c == '/') {
                out.push_back(c);
            } else if (c == 'n') {
                out.push_back('\n');
            } else if (c == 'r') {
                out.push_back('\r');
            } else if (c == 't') {
                out.push_back('\t');
            } else {
                out.push_back(c);
            }
        } else {
            out.push_back(c);
        }
        cur++;
    }
    return 0;
}

static int domui_parse_u32(const char** p, const char* end, domui_u32* out_v)
{
    domui_u32 v = 0u;
    int have = 0;
    domui_skip_ws(p, end);
    while (*p < end) {
        char c = **p;
        if (c < '0' || c > '9') {
            break;
        }
        have = 1;
        v = (v * 10u) + (domui_u32)(c - '0');
        (*p)++;
    }
    if (!have) {
        return 0;
    }
    if (out_v) {
        *out_v = v;
    }
    return 1;
}

static int domui_skip_value(const char** p, const char* end)
{
    domui_skip_ws(p, end);
    if (*p >= end) {
        return 0;
    }
    if (**p == '"') {
        std::string tmp;
        return domui_parse_string(p, end, tmp);
    }
    if (**p == '{') {
        int depth = 0;
        do {
            if (**p == '{') {
                depth++;
            } else if (**p == '}') {
                depth--;
            }
            (*p)++;
        } while (*p < end && depth > 0);
        return depth == 0;
    }
    if (**p == '[') {
        int depth = 0;
        do {
            if (**p == '[') {
                depth++;
            } else if (**p == ']') {
                depth--;
            }
            (*p)++;
        } while (*p < end && depth > 0);
        return depth == 0;
    }
    if (**p == '-' || (**p >= '0' && **p <= '9')) {
        domui_u32 tmp = 0u;
        return domui_parse_u32(p, end, &tmp);
    }
    if (!std::strncmp(*p, "true", 4)) {
        *p += 4;
        return 1;
    }
    if (!std::strncmp(*p, "false", 5)) {
        *p += 5;
        return 1;
    }
    if (!std::strncmp(*p, "null", 4)) {
        *p += 4;
        return 1;
    }
    return 0;
}

static int domui_parse_actions_object(const char** p, const char* end, domui_action_registry& reg)
{
    std::string key;
    domui_u32 id = 0u;
    if (!domui_parse_char(p, end, '{')) {
        return 0;
    }
    domui_skip_ws(p, end);
    if (*p < end && **p == '}') {
        (*p)++;
        return 1;
    }
    for (;;) {
        if (!domui_parse_string(p, end, key)) {
            return 0;
        }
        if (!domui_parse_char(p, end, ':')) {
            return 0;
        }
        if (!domui_parse_u32(p, end, &id)) {
            return 0;
        }
        if (!key.empty()) {
            reg.key_to_id[key] = id;
        }
        domui_skip_ws(p, end);
        if (*p < end && **p == ',') {
            (*p)++;
            continue;
        }
        break;
    }
    if (!domui_parse_char(p, end, '}')) {
        return 0;
    }
    return 1;
}

static int domui_parse_registry_json(const std::string& json, domui_action_registry& out)
{
    const char* p = json.c_str();
    const char* end = p + json.size();
    std::string key;
    domui_u32 next_id = 1u;

    if (!domui_parse_char(&p, end, '{')) {
        return 0;
    }
    domui_skip_ws(&p, end);
    if (p < end && *p == '}') {
        out.next_id = next_id;
        return 1;
    }
    for (;;) {
        if (!domui_parse_string(&p, end, key)) {
            return 0;
        }
        if (!domui_parse_char(&p, end, ':')) {
            return 0;
        }
        if (key == "next_id") {
            domui_u32 v = 0u;
            if (!domui_parse_u32(&p, end, &v)) {
                return 0;
            }
            next_id = v;
        } else if (key == "actions") {
            if (!domui_parse_actions_object(&p, end, out)) {
                return 0;
            }
        } else {
            if (!domui_skip_value(&p, end)) {
                return 0;
            }
        }
        domui_skip_ws(&p, end);
        if (p < end && *p == ',') {
            p++;
            continue;
        }
        break;
    }
    if (!domui_parse_char(&p, end, '}')) {
        return 0;
    }
    out.next_id = (next_id == 0u) ? 1u : next_id;
    return 1;
}

static std::string domui_escape_json_string(const std::string& s)
{
    std::string out;
    size_t i;
    out.reserve(s.size() + 8u);
    for (i = 0u; i < s.size(); ++i) {
        char c = s[i];
        if (c == '"' || c == '\\') {
            out.push_back('\\');
            out.push_back(c);
        } else if (c == '\n') {
            out.append("\\n");
        } else if (c == '\r') {
            out.append("\\r");
        } else if (c == '\t') {
            out.append("\\t");
        } else {
            out.push_back(c);
        }
    }
    return out;
}

static bool domui_write_text_if_changed(const char* path, const std::string& text, domui_diag* diag)
{
    std::vector<unsigned char> existing;
    if (path && domui_read_file_bytes(path, existing, 0)) {
        if (existing.size() == text.size() &&
            (text.empty() || memcmp(&existing[0], text.data(), text.size()) == 0)) {
            return true;
        }
    }
    return domui_atomic_write_file(path, text.data(), text.size(), diag);
}

bool domui_action_registry_load(const char* path, domui_action_registry* out, domui_diag* diag)
{
    std::vector<unsigned char> bytes;
    std::string json;
    domui_u32 max_id = 0u;
    if (!out) {
        if (diag) {
            diag->add_error("ui_codegen: registry output missing", 0u, "");
        }
        return false;
    }
    *out = domui_action_registry();
    if (!path || !path[0]) {
        return true;
    }
    if (!domui_file_exists(path)) {
        return true;
    }
    if (!domui_read_file_bytes(path, bytes, diag)) {
        return false;
    }
    if (!bytes.empty()) {
        json.assign((const char*)&bytes[0], bytes.size());
    }
    if (!domui_parse_registry_json(json, *out)) {
        if (diag) {
            diag->add_error("ui_codegen: registry parse failed", 0u, path);
        }
        return false;
    }
    for (std::map<std::string, domui_u32>::const_iterator it = out->key_to_id.begin();
         it != out->key_to_id.end();
         ++it) {
        if (it->second > max_id) {
            max_id = it->second;
        }
    }
    if (out->next_id <= max_id) {
        out->next_id = max_id + 1u;
    }
    return true;
}

bool domui_action_registry_save(const char* path, const domui_action_registry& reg, domui_diag* diag)
{
    std::string out;
    size_t i = 0u;
    if (!path || !path[0]) {
        if (diag) {
            diag->add_error("ui_codegen: registry path missing", 0u, "");
        }
        return false;
    }

    out.append("{\n");
    out.append("  \"next_id\": ");
    {
        char tmp[32];
        std::sprintf(tmp, "%u", (unsigned int)reg.next_id);
        out.append(tmp);
    }
    out.append(",\n");
    out.append("  \"actions\": {\n");
    for (std::map<std::string, domui_u32>::const_iterator it = reg.key_to_id.begin();
         it != reg.key_to_id.end();
         ++it) {
        out.append("    \"");
        out.append(domui_escape_json_string(it->first));
        out.append("\": ");
        {
            char tmp[32];
            std::sprintf(tmp, "%u", (unsigned int)it->second);
            out.append(tmp);
        }
        ++i;
        if (i < reg.key_to_id.size()) {
            out.append(",");
        }
        out.append("\n");
    }
    out.append("  }\n");
    out.append("}\n");

    return domui_write_text_if_changed(path, out, diag);
}

static std::string domui_sanitize_identifier(const std::string& in)
{
    std::string out;
    size_t i;
    out.reserve(in.size() + 8u);
    for (i = 0u; i < in.size(); ++i) {
        unsigned char c = (unsigned char)in[i];
        if (std::isalnum(c)) {
            out.push_back((char)std::toupper(c));
        } else {
            out.push_back('_');
        }
    }
    if (out.empty()) {
        out = "ACTION";
    }
    if (out[0] >= '0' && out[0] <= '9') {
        out.insert(out.begin(), '_');
    }
    return out;
}

static std::string domui_sanitize_doc_name(const std::string& in)
{
    std::string out;
    size_t i;
    out.reserve(in.size() + 8u);
    for (i = 0u; i < in.size(); ++i) {
        unsigned char c = (unsigned char)in[i];
        if (std::isalnum(c)) {
            out.push_back((char)std::tolower(c));
        } else {
            out.push_back('_');
        }
    }
    if (out.empty()) {
        out = "doc";
    }
    if (out[0] >= '0' && out[0] <= '9') {
        out.insert(0u, "ui_");
    }
    return out;
}

struct domui_action_def {
    std::string key;
    domui_u32 id;
    std::string symbol;
};

struct domui_action_id_less {
    bool operator()(const domui_action_def& a, const domui_action_def& b) const
    {
        return a.id < b.id;
    }
};

struct domui_action_key_less {
    bool operator()(const domui_action_def& a, const domui_action_def& b) const
    {
        return a.key < b.key;
    }
};

static void domui_collect_action_keys(const domui_doc& doc, std::vector<std::string>& out_keys)
{
    std::vector<domui_widget_id> order;
    out_keys.clear();
    doc.canonical_widget_order(order);
    for (size_t i = 0u; i < order.size(); ++i) {
        const domui_widget* w = doc.find_by_id(order[i]);
        if (!w) {
            continue;
        }
        const domui_events::list_type& entries = w->events.entries();
        for (size_t e = 0u; e < entries.size(); ++e) {
            const std::string& key = entries[e].action_key.str();
            if (!key.empty()) {
                out_keys.push_back(key);
            }
        }
    }
    std::sort(out_keys.begin(), out_keys.end());
    out_keys.erase(std::unique(out_keys.begin(), out_keys.end()), out_keys.end());
}

static void domui_build_action_defs(const std::vector<std::string>& keys,
                                    domui_action_registry& reg,
                                    std::vector<domui_action_def>& out_defs)
{
    std::map<std::string, int> used_symbols;
    size_t i;

    out_defs.clear();
    for (i = 0u; i < keys.size(); ++i) {
        const std::string& key = keys[i];
        domui_action_def def;
        std::string base = domui_sanitize_identifier(key);
        domui_u32 id = 0u;

        std::map<std::string, domui_u32>::iterator it = reg.key_to_id.find(key);
        if (it != reg.key_to_id.end()) {
            id = it->second;
        } else {
            id = reg.next_id;
            reg.key_to_id[key] = id;
            reg.next_id += 1u;
        }

        def.key = key;
        def.id = id;
        def.symbol = base;
        if (used_symbols.find(base) != used_symbols.end()) {
            char tmp[32];
            std::sprintf(tmp, "_ID%u", (unsigned int)id);
            def.symbol += tmp;
        }
        used_symbols[def.symbol] = 1;
        out_defs.push_back(def);
    }
}

static std::string domui_make_guard(const std::string& name)
{
    std::string guard = name;
    for (size_t i = 0u; i < guard.size(); ++i) {
        guard[i] = (char)std::toupper((unsigned char)guard[i]);
    }
    guard.append("_H_INCLUDED");
    return guard;
}

static void domui_append_line(std::string& out, const std::string& line)
{
    out.append(line);
    out.append("\n");
}

static std::string domui_build_gen_header(const std::string& doc_sym,
                                          const std::vector<domui_action_def>& defs)
{
    std::string out;
    std::string guard = domui_make_guard(doc_sym + "_ACTIONS_GEN");

    domui_append_line(out, "/* Auto-generated; do not edit. */");
    domui_append_line(out, "#ifndef " + guard);
    domui_append_line(out, "#define " + guard);
    domui_append_line(out, "");
    domui_append_line(out, "#include \"dui/domui_event.h\"");
    domui_append_line(out, "");
    domui_append_line(out, "#ifdef __cplusplus");
    domui_append_line(out, "extern \"C\" {");
    domui_append_line(out, "#endif");
    domui_append_line(out, "");
    domui_append_line(out, "typedef struct domui_action_entry {");
    domui_append_line(out, "    domui_action_id action_id;");
    domui_append_line(out, "    domui_action_fn fn;");
    domui_append_line(out, "    const char* key;");
    domui_append_line(out, "} domui_action_entry;");
    domui_append_line(out, "");
    for (size_t i = 0u; i < defs.size(); ++i) {
        char tmp[64];
        std::sprintf(tmp, "#define DOMUI_ACT_%s %uu", defs[i].symbol.c_str(), (unsigned int)defs[i].id);
        domui_append_line(out, tmp);
    }
    if (!defs.empty()) {
        domui_append_line(out, "");
    }
    domui_append_line(out, "const domui_action_entry* " + doc_sym + "_get_action_table(domui_u32* out_count);");
    domui_append_line(out, "domui_action_id " + doc_sym + "_action_id_from_key(const char* key, domui_u32 len);");
    domui_append_line(out, "void " + doc_sym + "_dispatch(void* user_ctx, const domui_event* e);");
    domui_append_line(out, "");
    domui_append_line(out, "#ifdef __cplusplus");
    domui_append_line(out, "} /* extern \"C\" */");
    domui_append_line(out, "#endif");
    domui_append_line(out, "");
    domui_append_line(out, "#endif /* " + guard + " */");
    return out;
}

static std::string domui_build_gen_cpp(const std::string& doc_sym,
                                       const std::string& user_header,
                                       const std::vector<domui_action_def>& defs)
{
    std::string out;
    std::vector<domui_action_def> by_id = defs;
    std::vector<domui_action_def> by_key = defs;

    std::sort(by_id.begin(), by_id.end(), domui_action_id_less());
    std::sort(by_key.begin(), by_key.end(), domui_action_key_less());

    domui_append_line(out, "/* Auto-generated; do not edit. */");
    domui_append_line(out, "#include \"" + doc_sym + "_actions_gen.h\"");
    domui_append_line(out, "#include \"" + user_header + "\"");
    domui_append_line(out, "#include <cstring>");
    domui_append_line(out, "");
    domui_append_line(out, "typedef struct domui_action_key_entry {");
    domui_append_line(out, "    const char* key;");
    domui_append_line(out, "    domui_action_id id;");
    domui_append_line(out, "} domui_action_key_entry;");
    domui_append_line(out, "");
    domui_append_line(out, "static const domui_action_entry g_actions[] = {");
    if (by_id.empty()) {
        domui_append_line(out, "    { 0u, (domui_action_fn)0, \"\" }");
    } else {
        for (size_t i = 0u; i < by_id.size(); ++i) {
            const domui_action_def& d = by_id[i];
            std::string line = "    { " + std::string("DOMUI_ACT_") + d.symbol + ", " +
                               doc_sym + "_act_" + d.symbol + ", \"" + d.key + "\" }";
            if (i + 1u < by_id.size()) {
                line += ",";
            }
            domui_append_line(out, line);
        }
    }
    domui_append_line(out, "};");
    {
        char tmp[64];
        std::sprintf(tmp, "static const domui_u32 g_action_count = %uu;", (unsigned int)by_id.size());
        domui_append_line(out, tmp);
    }
    domui_append_line(out, "");
    domui_append_line(out, "static const domui_action_key_entry g_action_keys[] = {");
    if (by_key.empty()) {
        domui_append_line(out, "    { \"\", 0u }");
    } else {
        for (size_t i = 0u; i < by_key.size(); ++i) {
            const domui_action_def& d = by_key[i];
            std::string line = "    { \"" + d.key + "\", " + std::string("DOMUI_ACT_") + d.symbol + " }";
            if (i + 1u < by_key.size()) {
                line += ",";
            }
            domui_append_line(out, line);
        }
    }
    domui_append_line(out, "};");
    {
        char tmp[64];
        std::sprintf(tmp, "static const domui_u32 g_action_key_count = %uu;", (unsigned int)by_key.size());
        domui_append_line(out, tmp);
    }
    domui_append_line(out, "");
    domui_append_line(out, "const domui_action_entry* " + doc_sym + "_get_action_table(domui_u32* out_count)");
    domui_append_line(out, "{");
    domui_append_line(out, "    if (out_count) {");
    domui_append_line(out, "        *out_count = g_action_count;");
    domui_append_line(out, "    }");
    domui_append_line(out, "    return g_actions;");
    domui_append_line(out, "}");
    domui_append_line(out, "");
    domui_append_line(out, "static domui_action_fn " + doc_sym + "_action_fn_from_id(domui_action_id id)");
    domui_append_line(out, "{");
    domui_append_line(out, "    size_t lo = 0u;");
    domui_append_line(out, "    size_t hi = (size_t)g_action_count;");
    domui_append_line(out, "    while (lo < hi) {");
    domui_append_line(out, "        size_t mid = (lo + hi) / 2u;");
    domui_append_line(out, "        domui_action_id cur = g_actions[mid].action_id;");
    domui_append_line(out, "        if (cur < id) {");
    domui_append_line(out, "            lo = mid + 1u;");
    domui_append_line(out, "        } else {");
    domui_append_line(out, "            hi = mid;");
    domui_append_line(out, "        }");
    domui_append_line(out, "    }");
    domui_append_line(out, "    if (lo < (size_t)g_action_count && g_actions[lo].action_id == id) {");
    domui_append_line(out, "        return g_actions[lo].fn;");
    domui_append_line(out, "    }");
    domui_append_line(out, "    return (domui_action_fn)0;");
    domui_append_line(out, "}");
    domui_append_line(out, "");
    domui_append_line(out, "domui_action_id " + doc_sym + "_action_id_from_key(const char* key, domui_u32 len)");
    domui_append_line(out, "{");
    domui_append_line(out, "    size_t lo = 0u;");
    domui_append_line(out, "    size_t hi = (size_t)g_action_key_count;");
    domui_append_line(out, "    if (!key) {");
    domui_append_line(out, "        return 0u;");
    domui_append_line(out, "    }");
    domui_append_line(out, "    while (lo < hi) {");
    domui_append_line(out, "        size_t mid = (lo + hi) / 2u;");
    domui_append_line(out, "        const char* cur = g_action_keys[mid].key;");
    domui_append_line(out, "        size_t cur_len = std::strlen(cur);");
    domui_append_line(out, "        size_t min_len = (len < (domui_u32)cur_len) ? (size_t)len : cur_len;");
    domui_append_line(out, "        int cmp = std::strncmp(key, cur, min_len);");
    domui_append_line(out, "        if (cmp == 0) {");
    domui_append_line(out, "            if (len < (domui_u32)cur_len) {");
    domui_append_line(out, "                cmp = -1;");
    domui_append_line(out, "            } else if (len > (domui_u32)cur_len) {");
    domui_append_line(out, "                cmp = 1;");
    domui_append_line(out, "            }");
    domui_append_line(out, "        }");
    domui_append_line(out, "        if (cmp < 0) {");
    domui_append_line(out, "            hi = mid;");
    domui_append_line(out, "        } else if (cmp > 0) {");
    domui_append_line(out, "            lo = mid + 1u;");
    domui_append_line(out, "        } else {");
    domui_append_line(out, "            return g_action_keys[mid].id;");
    domui_append_line(out, "        }");
    domui_append_line(out, "    }");
    domui_append_line(out, "    return 0u;");
    domui_append_line(out, "}");
    domui_append_line(out, "");
    domui_append_line(out, "void " + doc_sym + "_dispatch(void* user_ctx, const domui_event* e)");
    domui_append_line(out, "{");
    domui_append_line(out, "    domui_action_fn fn;");
    domui_append_line(out, "    if (!e) {");
    domui_append_line(out, "        return;");
    domui_append_line(out, "    }");
    domui_append_line(out, "    fn = " + doc_sym + "_action_fn_from_id(e->action_id);");
    domui_append_line(out, "    if (fn) {");
    domui_append_line(out, "        fn(user_ctx, e);");
    domui_append_line(out, "    }");
    domui_append_line(out, "}");
    return out;
}

static std::string domui_stub_region_begin(void)
{
    return "// BEGIN AUTO-GENERATED ACTION STUBS";
}

static std::string domui_stub_region_end(void)
{
    return "// END AUTO-GENERATED ACTION STUBS";
}

static void domui_collect_existing_stubs(const std::string& region,
                                         const std::string& doc_sym,
                                         std::vector<std::string>& out_names)
{
    size_t pos = 0u;
    out_names.clear();
    for (;;) {
        size_t at = region.find(doc_sym + "_act_", pos);
        if (at == std::string::npos) {
            break;
        }
        {
            size_t end = at;
            while (end < region.size() &&
                   (std::isalnum((unsigned char)region[end]) || region[end] == '_')) {
                end++;
            }
            out_names.push_back(region.substr(at, end - at));
            pos = end;
        }
    }
}

static bool domui_update_user_file(const std::string& path,
                                   const std::string& doc_sym,
                                   const std::vector<domui_action_def>& defs,
                                   bool is_header,
                                   domui_diag* diag)
{
    std::vector<unsigned char> bytes;
    std::string content;
    std::string begin = domui_stub_region_begin();
    std::string end = domui_stub_region_end();
    size_t begin_pos;
    size_t end_pos;

    if (domui_read_file_bytes(path.c_str(), bytes, 0) && !bytes.empty()) {
        content.assign((const char*)&bytes[0], bytes.size());
    }

    if (content.empty()) {
        std::string out;
        std::string guard = domui_make_guard(doc_sym + (is_header ? "_ACTIONS_USER" : "_ACTIONS_USER_CPP"));
        if (is_header) {
            domui_append_line(out, "/* User action stubs. */");
            domui_append_line(out, "#ifndef " + guard);
            domui_append_line(out, "#define " + guard);
            domui_append_line(out, "");
            domui_append_line(out, "#include \"dui/domui_event.h\"");
            domui_append_line(out, "");
            domui_append_line(out, "#ifdef __cplusplus");
            domui_append_line(out, "extern \"C\" {");
            domui_append_line(out, "#endif");
            domui_append_line(out, "");
            domui_append_line(out, begin);
            for (size_t i = 0u; i < defs.size(); ++i) {
                domui_append_line(out, "void " + doc_sym + "_act_" + defs[i].symbol +
                                        "(void* user_ctx, const domui_event* e);");
            }
            domui_append_line(out, end);
            domui_append_line(out, "");
            domui_append_line(out, "#ifdef __cplusplus");
            domui_append_line(out, "} /* extern \"C\" */");
            domui_append_line(out, "#endif");
            domui_append_line(out, "");
            domui_append_line(out, "#endif /* " + guard + " */");
        } else {
            domui_append_line(out, "/* User action stubs. */");
            domui_append_line(out, "#include \"" + doc_sym + "_actions_user.h\"");
            domui_append_line(out, "");
            domui_append_line(out, begin);
            for (size_t i = 0u; i < defs.size(); ++i) {
                domui_append_line(out, "void " + doc_sym + "_act_" + defs[i].symbol +
                                        "(void* user_ctx, const domui_event* e)");
                domui_append_line(out, "{");
                domui_append_line(out, "    (void)user_ctx;");
                domui_append_line(out, "    (void)e;");
                domui_append_line(out, "}");
                domui_append_line(out, "");
            }
            domui_append_line(out, end);
        }
        return domui_write_text_if_changed(path.c_str(), out, diag);
    }

    begin_pos = content.find(begin);
    end_pos = content.find(end);
    if (begin_pos == std::string::npos || end_pos == std::string::npos || end_pos < begin_pos) {
        std::string append;
        domui_append_line(append, "");
        domui_append_line(append, begin);
        for (size_t i = 0u; i < defs.size(); ++i) {
            if (is_header) {
                domui_append_line(append, "void " + doc_sym + "_act_" + defs[i].symbol +
                                         "(void* user_ctx, const domui_event* e);");
            } else {
                domui_append_line(append, "void " + doc_sym + "_act_" + defs[i].symbol +
                                         "(void* user_ctx, const domui_event* e)");
                domui_append_line(append, "{");
                domui_append_line(append, "    (void)user_ctx;");
                domui_append_line(append, "    (void)e;");
                domui_append_line(append, "}");
                domui_append_line(append, "");
            }
        }
        domui_append_line(append, end);
        content.append(append);
        return domui_write_text_if_changed(path.c_str(), content, diag);
    }

    {
        std::string region = content.substr(begin_pos, end_pos - begin_pos);
        std::vector<std::string> existing;
        std::string insert;
        domui_collect_existing_stubs(region, doc_sym, existing);
        for (size_t i = 0u; i < defs.size(); ++i) {
            std::string name = doc_sym + "_act_" + defs[i].symbol;
            if (std::find(existing.begin(), existing.end(), name) != existing.end()) {
                continue;
            }
            if (is_header) {
                domui_append_line(insert, "void " + name + "(void* user_ctx, const domui_event* e);");
            } else {
                domui_append_line(insert, "void " + name + "(void* user_ctx, const domui_event* e)");
                domui_append_line(insert, "{");
                domui_append_line(insert, "    (void)user_ctx;");
                domui_append_line(insert, "    (void)e;");
                domui_append_line(insert, "}");
                domui_append_line(insert, "");
            }
        }
        if (!insert.empty()) {
            content.insert(end_pos, insert);
        }
        return domui_write_text_if_changed(path.c_str(), content, diag);
    }
}

bool domui_codegen_run(const domui_codegen_params* params, domui_diag* diag)
{
    domui_doc doc;
    domui_action_registry reg;
    std::vector<std::string> keys;
    std::vector<domui_action_def> defs;
    std::string doc_name;
    std::string doc_sym;
    std::string gen_dir;
    std::string user_dir;
    std::string gen_header_path;
    std::string gen_cpp_path;
    std::string user_header_path;
    std::string user_cpp_path;
    std::string gen_header;
    std::string gen_cpp;

    if (!params || !params->input_tlv_path || !params->registry_path ||
        !params->out_gen_dir || !params->out_user_dir) {
        if (diag) {
            diag->add_error("ui_codegen: missing parameters", 0u, "");
        }
        return false;
    }

    if (!domui_doc_load_tlv(&doc, params->input_tlv_path, diag)) {
        return false;
    }

    if (params->doc_name_override && params->doc_name_override[0]) {
        doc_name = params->doc_name_override;
    } else {
        doc_name = doc.meta.doc_name.str();
    }
    doc_sym = "ui_" + domui_sanitize_doc_name(doc_name);

    if (!domui_action_registry_load(params->registry_path, &reg, diag)) {
        return false;
    }

    domui_collect_action_keys(doc, keys);
    domui_build_action_defs(keys, reg, defs);

    if (!domui_action_registry_save(params->registry_path, reg, diag)) {
        return false;
    }

    gen_dir = params->out_gen_dir;
    user_dir = params->out_user_dir;
    domui_ensure_dir(gen_dir);
    domui_ensure_dir(user_dir);

    gen_header_path = domui_join_path(gen_dir, doc_sym + "_actions_gen.h");
    gen_cpp_path = domui_join_path(gen_dir, doc_sym + "_actions_gen.cpp");
    user_header_path = domui_join_path(user_dir, doc_sym + "_actions_user.h");
    user_cpp_path = domui_join_path(user_dir, doc_sym + "_actions_user.cpp");

    gen_header = domui_build_gen_header(doc_sym, defs);
    gen_cpp = domui_build_gen_cpp(doc_sym, doc_sym + "_actions_user.h", defs);

    if (!domui_write_text_if_changed(gen_header_path.c_str(), gen_header, diag)) {
        return false;
    }
    if (!domui_write_text_if_changed(gen_cpp_path.c_str(), gen_cpp, diag)) {
        return false;
    }
    if (!domui_update_user_file(user_header_path, doc_sym, defs, true, diag)) {
        return false;
    }
    if (!domui_update_user_file(user_cpp_path, doc_sym, defs, false, diag)) {
        return false;
    }

    return true;
}
