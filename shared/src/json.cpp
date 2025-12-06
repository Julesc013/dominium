#include "dom_shared/json.h"

#include <cctype>
#include <sstream>

static void skip_ws(const std::string &s, size_t &i)
{
    while (i < s.size() && (s[i] == ' ' || s[i] == '\t' || s[i] == '\r' || s[i] == '\n')) {
        ++i;
    }
}

static bool parse_value(const std::string &s, size_t &i, JsonValue &out);

static bool parse_string(const std::string &s, size_t &i, std::string &out)
{
    if (s[i] != '"') return false;
    ++i;
    while (i < s.size()) {
        char c = s[i++];
        if (c == '\\' && i < s.size()) {
            char esc = s[i++];
            if (esc == 'n') out.push_back('\n');
            else if (esc == 't') out.push_back('\t');
            else out.push_back(esc);
        } else if (c == '"') {
            return true;
        } else {
            out.push_back(c);
        }
    }
    return false;
}

static bool parse_number(const std::string &s, size_t &i, double &out)
{
    size_t start = i;
    if (s[i] == '-') ++i;
    while (i < s.size() && std::isdigit((unsigned char)s[i])) ++i;
    if (i < s.size() && s[i] == '.') {
        ++i;
        while (i < s.size() && std::isdigit((unsigned char)s[i])) ++i;
    }
    std::stringstream ss;
    ss << s.substr(start, i - start);
    ss >> out;
    return true;
}

static bool parse_array(const std::string &s, size_t &i, JsonValue &out)
{
    if (s[i] != '[') return false;
    ++i;
    skip_ws(s, i);
    out = JsonValue::make_array();
    if (i < s.size() && s[i] == ']') { ++i; return true; }
    while (i < s.size()) {
        JsonValue elem;
        if (!parse_value(s, i, elem)) return false;
        out.array_values.push_back(elem);
        skip_ws(s, i);
        if (s[i] == ',') { ++i; skip_ws(s, i); continue; }
        if (s[i] == ']') { ++i; break; }
        return false;
    }
    return true;
}

static bool parse_object(const std::string &s, size_t &i, JsonValue &out)
{
    if (s[i] != '{') return false;
    ++i;
    skip_ws(s, i);
    out = JsonValue::make_object();
    if (i < s.size() && s[i] == '}') { ++i; return true; }
    while (i < s.size()) {
        std::string key;
        if (!parse_string(s, i, key)) return false;
        skip_ws(s, i);
        if (s[i] != ':') return false;
        ++i;
        skip_ws(s, i);
        JsonValue val;
        if (!parse_value(s, i, val)) return false;
        out.object_values[key] = val;
        skip_ws(s, i);
        if (s[i] == ',') { ++i; skip_ws(s, i); continue; }
        if (s[i] == '}') { ++i; break; }
        return false;
    }
    return true;
}

static bool parse_value(const std::string &s, size_t &i, JsonValue &out)
{
    skip_ws(s, i);
    if (i >= s.size()) return false;
    char c = s[i];
    if (c == '"') {
        std::string val;
        if (!parse_string(s, i, val)) return false;
        out = JsonValue::make_string(val);
        return true;
    }
    if (c == '{') {
        return parse_object(s, i, out);
    }
    if (c == '[') {
        return parse_array(s, i, out);
    }
    if (std::isdigit((unsigned char)c) || c == '-') {
        double num = 0.0;
        if (!parse_number(s, i, num)) return false;
        out = JsonValue::make_number(num);
        return true;
    }
    if (s.compare(i, 4, "true") == 0) {
        i += 4;
        out = JsonValue::make_bool(true);
        return true;
    }
    if (s.compare(i, 5, "false") == 0) {
        i += 5;
        out = JsonValue::make_bool(false);
        return true;
    }
    if (s.compare(i, 4, "null") == 0) {
        i += 4;
        out = JsonValue::make_null();
        return true;
    }
    return false;
}

bool json_parse(const std::string &text, JsonValue &out)
{
    size_t i = 0;
    bool ok = parse_value(text, i, out);
    if (!ok) return false;
    skip_ws(text, i);
    return i == text.size();
}

static std::string indent_str(int indent)
{
    return std::string(indent, ' ');
}

static void stringify(const JsonValue &v, std::string &out, int indent)
{
    switch (v.kind) {
    case JsonValue::JSON_NULL: out += "null"; break;
    case JsonValue::JSON_BOOL: out += (v.bool_value ? "true" : "false"); break;
    case JsonValue::JSON_NUMBER: {
        std::stringstream ss;
        ss << v.number_value;
        out += ss.str();
    } break;
    case JsonValue::JSON_STRING:
        out += "\"";
        for (size_t i = 0; i < v.string_value.size(); ++i) {
            char c = v.string_value[i];
            if (c == '"' || c == '\\') out += "\\";
            out += c;
        }
        out += "\"";
        break;
    case JsonValue::JSON_OBJECT: {
        out += "{";
        if (!v.object_values.empty()) out += "\n";
        size_t count = 0;
        for (std::map<std::string, JsonValue>::const_iterator it = v.object_values.begin(); it != v.object_values.end(); ++it, ++count) {
            out += indent_str(indent + 2);
            out += "\"";
            out += it->first;
            out += "\": ";
            stringify(it->second, out, indent + 2);
            if (count + 1 < v.object_values.size()) out += ",";
            out += "\n";
        }
        if (!v.object_values.empty()) out += indent_str(indent);
        out += "}";
    } break;
    case JsonValue::JSON_ARRAY: {
        out += "[";
        if (!v.array_values.empty()) out += "\n";
        for (size_t i = 0; i < v.array_values.size(); ++i) {
            out += indent_str(indent + 2);
            stringify(v.array_values[i], out, indent + 2);
            if (i + 1 < v.array_values.size()) out += ",";
            out += "\n";
        }
        if (!v.array_values.empty()) out += indent_str(indent);
        out += "]";
    } break;
    }
}

std::string json_stringify(const JsonValue &v, int indent)
{
    std::string out;
    stringify(v, out, indent);
    return out;
}

JsonValue JsonValue::make_null() { JsonValue v; v.kind = JSON_NULL; return v; }
JsonValue JsonValue::make_bool(bool b) { JsonValue v; v.kind = JSON_BOOL; v.bool_value = b; return v; }
JsonValue JsonValue::make_number(double n) { JsonValue v; v.kind = JSON_NUMBER; v.number_value = n; return v; }
JsonValue JsonValue::make_string(const std::string &s) { JsonValue v; v.kind = JSON_STRING; v.string_value = s; return v; }
JsonValue JsonValue::make_object() { JsonValue v; v.kind = JSON_OBJECT; return v; }
JsonValue JsonValue::make_array() { JsonValue v; v.kind = JSON_ARRAY; return v; }
