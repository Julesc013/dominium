/*
FILE: source/domino/ui_ir/ui_ir_string.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / ui_ir string
RESPONSIBILITY: Deterministic string wrapper and comparisons (byte-order).
ALLOWED DEPENDENCIES: C++98 standard headers only.
FORBIDDEN DEPENDENCIES: UI backends, launcher, TLV I/O.
THREADING MODEL: Data-only; no internal synchronization.
ERROR MODEL: N/A (helpers only).
DETERMINISM: Byte-wise comparisons (no locale reliance).
*/
#ifndef DOMINO_UI_IR_STRING_H_INCLUDED
#define DOMINO_UI_IR_STRING_H_INCLUDED

#include <string>
#include <vector>

class domui_string {
public:
    domui_string();
    explicit domui_string(const char* s);
    domui_string(const std::string& s);

    const char* c_str() const;
    const std::string& str() const;
    size_t size() const;
    bool empty() const;
    void clear();
    void set(const char* s);

private:
    std::string m_value;
};

int domui_string_compare(const domui_string& a, const domui_string& b);
bool domui_string_less(const domui_string& a, const domui_string& b);
bool domui_string_equal(const domui_string& a, const domui_string& b);

typedef std::vector<domui_string> domui_string_list;

#endif /* DOMINO_UI_IR_STRING_H_INCLUDED */
