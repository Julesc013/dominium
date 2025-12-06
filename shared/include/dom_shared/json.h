#ifndef DOM_SHARED_JSON_H
#define DOM_SHARED_JSON_H

#include <string>
#include <map>
#include <vector>

namespace dom_shared {

class JsonValue {
public:
    enum Type { Null, Bool, Number, String, Object, Array };

    JsonValue();
    explicit JsonValue(Type t);

    static JsonValue object();
    static JsonValue array();

    Type type() const;

    // Object access
    bool has(const std::string& key) const;
    const JsonValue& operator[](const std::string& key) const;
    JsonValue&       operator[](const std::string& key);
    const std::map<std::string, JsonValue>& object_items() const;

    // Array access
    void             push_back(const JsonValue& v);
    const JsonValue& at(size_t idx) const;
    size_t           size() const;
    const std::vector<JsonValue>& array_items() const;

    // Primitive setters/getters
    void        set_string(const std::string& s);
    std::string as_string(const std::string& def = "") const;

    void        set_number(double n);
    double      as_number(double def = 0.0) const;

    void        set_bool(bool b);
    bool        as_bool(bool def = false) const;

    // Internal stringify helper (exposed for writer utility)
    void stringify_internal(std::string& out, int indent, int indent_step, bool pretty) const;

private:
    Type type_;
    bool bool_value_;
    double num_value_;
    std::string str_value_;
    std::map<std::string, JsonValue> object_value_;
    std::vector<JsonValue> array_value_;
};

bool json_parse(const std::string& text, JsonValue& out);
std::string json_stringify(const JsonValue& v, bool pretty = false);

} // namespace dom_shared

#endif
