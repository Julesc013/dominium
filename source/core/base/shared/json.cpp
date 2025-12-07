#include "dom_shared/json.h"

#include <cctype>
#include <sstream>

namespace dom_shared {

JsonValue::JsonValue() : type_(Null), bool_value_(false), num_value_(0.0), str_value_(), object_value_(), array_value_()
{
}

JsonValue::JsonValue(Type t) : type_(t), bool_value_(false), num_value_(0.0), str_value_(), object_value_(), array_value_()
{
}

JsonValue JsonValue::object()
{
    return JsonValue(Object);
}

JsonValue JsonValue::array()
{
    return JsonValue(Array);
}

JsonValue::Type JsonValue::type() const
{
    return type_;
}

bool JsonValue::has(const std::string& key) const
{
    if (type_ != Object) return false;
    return object_value_.find(key) != object_value_.end();
}

const JsonValue& JsonValue::operator[](const std::string& key) const
{
    static JsonValue null_value;
    if (type_ != Object) return null_value;
    std::map<std::string, JsonValue>::const_iterator it = object_value_.find(key);
    if (it == object_value_.end()) return null_value;
    return it->second;
}

JsonValue& JsonValue::operator[](const std::string& key)
{
    if (type_ != Object) {
        type_ = Object;
        object_value_.clear();
    }
    return object_value_[key];
}

const std::map<std::string, JsonValue>& JsonValue::object_items() const
{
    static std::map<std::string, JsonValue> empty;
    if (type_ != Object) return empty;
    return object_value_;
}

void JsonValue::push_back(const JsonValue& v)
{
    if (type_ != Array) {
        type_ = Array;
        array_value_.clear();
    }
    array_value_.push_back(v);
}

const JsonValue& JsonValue::at(size_t idx) const
{
    static JsonValue null_value;
    if (type_ != Array) return null_value;
    if (idx >= array_value_.size()) return null_value;
    return array_value_[idx];
}

size_t JsonValue::size() const
{
    if (type_ == Array) return array_value_.size();
    if (type_ == Object) return object_value_.size();
    return 0;
}

const std::vector<JsonValue>& JsonValue::array_items() const
{
    static std::vector<JsonValue> empty;
    if (type_ != Array) return empty;
    return array_value_;
}

void JsonValue::set_string(const std::string& s)
{
    type_ = String;
    str_value_ = s;
}

std::string JsonValue::as_string(const std::string& def) const
{
    if (type_ == String) return str_value_;
    return def;
}

void JsonValue::set_number(double n)
{
    type_ = Number;
    num_value_ = n;
}

double JsonValue::as_number(double def) const
{
    if (type_ == Number) return num_value_;
    return def;
}

void JsonValue::set_bool(bool b)
{
    type_ = Bool;
    bool_value_ = b;
}

bool JsonValue::as_bool(bool def) const
{
    if (type_ == Bool) return bool_value_;
    return def;
}

static void skip_ws(const std::string& s, size_t& i)
{
    while (i < s.size() && (s[i] == ' ' || s[i] == '\t' || s[i] == '\r' || s[i] == '\n')) {
        ++i;
    }
}

static bool parse_value(const std::string& s, size_t& i, JsonValue& out);

static bool parse_string(const std::string& s, size_t& i, std::string& out)
{
    if (s[i] != '"') return false;
    ++i;
    while (i < s.size()) {
        char c = s[i++];
        if (c == '\\' && i < s.size()) {
            char esc = s[i++];
            if (esc == 'n') out.push_back('\n');
            else if (esc == 't') out.push_back('\t');
            else if (esc == 'r') out.push_back('\r');
            else if (esc == '"') out.push_back('"');
            else if (esc == '\\') out.push_back('\\');
            else out.push_back(esc);
        } else if (c == '"') {
            return true;
        } else {
            out.push_back(c);
        }
    }
    return false;
}

static bool parse_number(const std::string& s, size_t& i, double& out)
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

static bool parse_array(const std::string& s, size_t& i, JsonValue& out)
{
    if (s[i] != '[') return false;
    ++i;
    skip_ws(s, i);
    out = JsonValue::array();
    if (i < s.size() && s[i] == ']') { ++i; return true; }
    while (i < s.size()) {
        JsonValue elem;
        if (!parse_value(s, i, elem)) return false;
        out.push_back(elem);
        skip_ws(s, i);
        if (i >= s.size()) break;
        if (s[i] == ',') { ++i; skip_ws(s, i); continue; }
        if (s[i] == ']') { ++i; break; }
        return false;
    }
    return true;
}

static bool parse_object(const std::string& s, size_t& i, JsonValue& out)
{
    if (s[i] != '{') return false;
    ++i;
    skip_ws(s, i);
    out = JsonValue::object();
    if (i < s.size() && s[i] == '}') { ++i; return true; }
    while (i < s.size()) {
        std::string key;
        if (!parse_string(s, i, key)) return false;
        skip_ws(s, i);
        if (i >= s.size() || s[i] != ':') return false;
        ++i;
        skip_ws(s, i);
        JsonValue val;
        if (!parse_value(s, i, val)) return false;
        out[key] = val;
        skip_ws(s, i);
        if (i >= s.size()) break;
        if (s[i] == ',') { ++i; skip_ws(s, i); continue; }
        if (s[i] == '}') { ++i; break; }
        return false;
    }
    return true;
}

static bool parse_value(const std::string& s, size_t& i, JsonValue& out)
{
    skip_ws(s, i);
    if (i >= s.size()) return false;
    char c = s[i];
    if (c == '"') {
        std::string val;
        if (!parse_string(s, i, val)) return false;
        out = JsonValue(JsonValue::String);
        out.set_string(val);
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
        out = JsonValue(JsonValue::Number);
        out.set_number(num);
        return true;
    }
    if (s.compare(i, 4, "true") == 0) {
        i += 4;
        out = JsonValue(JsonValue::Bool);
        out.set_bool(true);
        return true;
    }
    if (s.compare(i, 5, "false") == 0) {
        i += 5;
        out = JsonValue(JsonValue::Bool);
        out.set_bool(false);
        return true;
    }
    if (s.compare(i, 4, "null") == 0) {
        i += 4;
        out = JsonValue(JsonValue::Null);
        return true;
    }
    return false;
}

bool json_parse(const std::string& text, JsonValue& out)
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

void JsonValue::stringify_internal(std::string& out, int indent, int indent_step, bool pretty) const
{
    switch (type_) {
    case Null: out += "null"; break;
    case Bool: out += (bool_value_ ? "true" : "false"); break;
    case Number: {
        std::stringstream ss;
        ss << num_value_;
        out += ss.str();
    } break;
    case String:
        out += "\"";
        {
            for (size_t i = 0; i < str_value_.size(); ++i) {
                char c = str_value_[i];
                if (c == '"' || c == '\\') out += "\\";
                out += c;
            }
        }
        out += "\"";
        break;
    case Object: {
        out += "{";
        if (pretty && !object_value_.empty()) out += "\n";
        size_t count = 0;
        for (std::map<std::string, JsonValue>::const_iterator it = object_value_.begin(); it != object_value_.end(); ++it, ++count) {
            if (pretty) out += indent_str(indent + indent_step);
            out += "\"";
            out += it->first;
            out += "\":";
            if (pretty) out += " ";
            it->second.stringify_internal(out, indent + indent_step, indent_step, pretty);
            if (count + 1 < object_value_.size()) out += ",";
            if (pretty) out += "\n";
        }
        if (pretty && !object_value_.empty()) out += indent_str(indent);
        out += "}";
    } break;
    case Array: {
        out += "[";
        if (pretty && !array_value_.empty()) out += "\n";
        for (size_t i = 0; i < array_value_.size(); ++i) {
            if (pretty) out += indent_str(indent + indent_step);
            array_value_[i].stringify_internal(out, indent + indent_step, indent_step, pretty);
            if (i + 1 < array_value_.size()) out += ",";
            if (pretty) out += "\n";
        }
        if (pretty && !array_value_.empty()) out += indent_str(indent);
        out += "]";
    } break;
    }
}

std::string json_stringify(const JsonValue& v, bool pretty)
{
    std::string out;
    v.stringify_internal(out, 0, pretty ? 2 : 0, pretty);
    return out;
}

} // namespace dom_shared
