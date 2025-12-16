/*
FILE: include/dominium/_internal/dom_priv/dom_shared/json.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / _internal/dom_priv/dom_shared/json
RESPONSIBILITY: Defines the public contract for `json` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/dominium/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_SHARED_JSON_H
#define DOM_SHARED_JSON_H

#include <string>
#include <map>
#include <vector>

namespace dom_shared {

class JsonValue {
public:
    enum Type { Null, Bool, Number, String, Object, Array };

/* Purpose: API entry point for `json`.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
    JsonValue();
/* Purpose: API entry point for `json`.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
    explicit JsonValue(Type t);

/* Purpose: API entry point for `json`.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
    static JsonValue object();
/* Purpose: API entry point for `json`.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
    static JsonValue array();

/* Purpose: API entry point for `json`.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
    Type type() const;

    // Object access
    bool has(const std::string& key) const;
    const JsonValue& operator[](const std::string& key) const;
    JsonValue&       operator[](const std::string& key);
/* Purpose: Items object.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
    const std::map<std::string, JsonValue>& object_items() const;

    // Array access
    void             push_back(const JsonValue& v);
/* Purpose: API entry point for `json`.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
    const JsonValue& at(size_t idx) const;
/* Purpose: API entry point for `json`.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
    size_t           size() const;
/* Purpose: Items array.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
    const std::vector<JsonValue>& array_items() const;

    // Primitive setters/getters
    void        set_string(const std::string& s);
/* Purpose: String as.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
    std::string as_string(const std::string& def = "") const;

/* Purpose: Number set.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 */
    void        set_number(double n);
/* Purpose: Number as.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
    double      as_number(double def = 0.0) const;

/* Purpose: Bool set.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 */
    void        set_bool(bool b);
/* Purpose: Bool as.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: `true` on success; `false` on failure.
 */
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

/* Purpose: Parse json.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: `true` on success; `false` on failure.
 */
bool json_parse(const std::string& text, JsonValue& out);
/* Purpose: Stringify json.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
std::string json_stringify(const JsonValue& v, bool pretty = false);

} // namespace dom_shared

#endif
