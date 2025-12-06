#ifndef DOM_SHARED_JSON_H
#define DOM_SHARED_JSON_H

#include <string>
#include <map>
#include <vector>

struct JsonValue {
    enum Kind { JSON_NULL, JSON_BOOL, JSON_NUMBER, JSON_STRING, JSON_OBJECT, JSON_ARRAY } kind;
    bool bool_value;
    double number_value;
    std::string string_value;
    std::map<std::string, JsonValue> object_values;
    std::vector<JsonValue> array_values;

    JsonValue() : kind(JSON_NULL), bool_value(false), number_value(0.0) {}
    static JsonValue make_null();
    static JsonValue make_bool(bool v);
    static JsonValue make_number(double v);
    static JsonValue make_string(const std::string &v);
    static JsonValue make_object();
    static JsonValue make_array();
};

bool json_parse(const std::string &text, JsonValue &out);
std::string json_stringify(const JsonValue &v, int indent = 0);

#endif /* DOM_SHARED_JSON_H */
