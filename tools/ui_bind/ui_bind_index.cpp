/*
FILE: tools/ui_bind/ui_bind_index.cpp
MODULE: Dominium
PURPOSE: Parse tools/ui_index/ui_index.json for canonical UI entries.
NOTES: Minimal JSON parser (strings only) for deterministic tooling.
*/
#include "ui_bind_index.h"

#include <cctype>
#include <cstdio>

static bool read_text_file(const char* path, std::string& out, std::string* out_error)
{
    FILE* f = 0;
    long size = 0;
    size_t read_bytes = 0;
    out.clear();
    if (!path || !path[0]) {
        if (out_error) {
            *out_error = "ui_index: missing path";
        }
        return false;
    }
    f = std::fopen(path, "rb");
    if (!f) {
        if (out_error) {
            *out_error = "ui_index: open failed";
        }
        return false;
    }
    if (std::fseek(f, 0L, SEEK_END) != 0) {
        std::fclose(f);
        if (out_error) {
            *out_error = "ui_index: fseek failed";
        }
        return false;
    }
    size = std::ftell(f);
    if (size < 0) {
        std::fclose(f);
        if (out_error) {
            *out_error = "ui_index: ftell failed";
        }
        return false;
    }
    if (std::fseek(f, 0L, SEEK_SET) != 0) {
        std::fclose(f);
        if (out_error) {
            *out_error = "ui_index: fseek reset failed";
        }
        return false;
    }
    if (size == 0) {
        std::fclose(f);
        return true;
    }
    out.resize((size_t)size);
    read_bytes = std::fread(&out[0], 1u, (size_t)size, f);
    std::fclose(f);
    if (read_bytes != (size_t)size) {
        if (out_error) {
            *out_error = "ui_index: read failed";
        }
        return false;
    }
    return true;
}

static void skip_ws(const std::string& text, size_t& idx)
{
    while (idx < text.size()) {
        unsigned char c = (unsigned char)text[idx];
        if (!std::isspace(c)) {
            break;
        }
        ++idx;
    }
}

static bool parse_string(const std::string& text, size_t& idx, std::string& out)
{
    out.clear();
    skip_ws(text, idx);
    if (idx >= text.size() || text[idx] != '"') {
        return false;
    }
    ++idx;
    while (idx < text.size()) {
        char c = text[idx++];
        if (c == '"') {
            return true;
        }
        if (c == '\\') {
            if (idx >= text.size()) {
                return false;
            }
            char esc = text[idx++];
            switch (esc) {
            case '"': out.push_back('"'); break;
            case '\\': out.push_back('\\'); break;
            case '/': out.push_back('/'); break;
            case 'b': out.push_back('\b'); break;
            case 'f': out.push_back('\f'); break;
            case 'n': out.push_back('\n'); break;
            case 'r': out.push_back('\r'); break;
            case 't': out.push_back('\t'); break;
            default:
                out.push_back(esc);
                break;
            }
            continue;
        }
        out.push_back(c);
    }
    return false;
}

static void skip_value(const std::string& text, size_t& idx)
{
    skip_ws(text, idx);
    if (idx >= text.size()) {
        return;
    }
    if (text[idx] == '"') {
        std::string tmp;
        (void)parse_string(text, idx, tmp);
        return;
    }
    if (text[idx] == '{') {
        int depth = 0;
        while (idx < text.size()) {
            char c = text[idx++];
            if (c == '"') {
                std::string tmp;
                --idx;
                (void)parse_string(text, idx, tmp);
                continue;
            }
            if (c == '{') {
                ++depth;
            } else if (c == '}') {
                --depth;
                if (depth <= 0) {
                    break;
                }
            }
        }
        return;
    }
    if (text[idx] == '[') {
        int depth = 0;
        while (idx < text.size()) {
            char c = text[idx++];
            if (c == '"') {
                std::string tmp;
                --idx;
                (void)parse_string(text, idx, tmp);
                continue;
            }
            if (c == '[') {
                ++depth;
            } else if (c == ']') {
                --depth;
                if (depth <= 0) {
                    break;
                }
            }
        }
        return;
    }
    while (idx < text.size()) {
        char c = text[idx];
        if (c == ',' || c == '}' || c == ']') {
            break;
        }
        ++idx;
    }
}

static bool parse_entries_array(const std::string& text,
                                size_t& idx,
                                std::vector<ui_bind_index_entry>& out_entries)
{
    skip_ws(text, idx);
    if (idx >= text.size() || text[idx] != '[') {
        return false;
    }
    ++idx;
    while (idx < text.size()) {
        skip_ws(text, idx);
        if (idx >= text.size()) {
            return false;
        }
        if (text[idx] == ']') {
            ++idx;
            return true;
        }
        if (text[idx] == ',') {
            ++idx;
            continue;
        }
        if (text[idx] != '{') {
            return false;
        }
        ++idx;
        ui_bind_index_entry entry;
        while (idx < text.size()) {
            std::string key;
            std::string value;
            skip_ws(text, idx);
            if (idx >= text.size()) {
                return false;
            }
            if (text[idx] == '}') {
                ++idx;
                break;
            }
            if (text[idx] == ',') {
                ++idx;
                continue;
            }
            if (!parse_string(text, idx, key)) {
                return false;
            }
            skip_ws(text, idx);
            if (idx >= text.size() || text[idx] != ':') {
                return false;
            }
            ++idx;
            skip_ws(text, idx);
            if (idx < text.size() && text[idx] == '"') {
                if (!parse_string(text, idx, value)) {
                    return false;
                }
                if (key == "ui_type") {
                    entry.ui_type = value;
                } else if (key == "path") {
                    entry.path = value;
                } else if (key == "tool") {
                    entry.tool = value;
                }
            } else {
                skip_value(text, idx);
            }
        }
        if (!entry.path.empty()) {
            out_entries.push_back(entry);
        }
    }
    return false;
}

bool ui_bind_load_index(const char* path,
                        std::vector<ui_bind_index_entry>& out_entries,
                        std::string* out_error)
{
    std::string text;
    size_t idx = 0;
    bool found_entries = false;

    out_entries.clear();
    if (!read_text_file(path, text, out_error)) {
        return false;
    }

    while (idx < text.size()) {
        std::string key;
        skip_ws(text, idx);
        if (idx >= text.size()) {
            break;
        }
        if (text[idx] == '"') {
            if (!parse_string(text, idx, key)) {
                if (out_error) {
                    *out_error = "ui_index: invalid JSON string";
                }
                return false;
            }
            skip_ws(text, idx);
            if (idx >= text.size() || text[idx] != ':') {
                if (out_error) {
                    *out_error = "ui_index: expected ':'";
                }
                return false;
            }
            ++idx;
            if (key == "entries") {
                if (!parse_entries_array(text, idx, out_entries)) {
                    if (out_error) {
                        *out_error = "ui_index: invalid entries array";
                    }
                    return false;
                }
                found_entries = true;
            } else {
                skip_value(text, idx);
            }
        } else {
            ++idx;
        }
    }

    if (!found_entries) {
        if (out_error) {
            *out_error = "ui_index: entries not found";
        }
        return false;
    }
    return true;
}
