/*
FILE: source/domino/ui_ir/ui_ir_string.cpp
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / ui_ir string
RESPONSIBILITY: Implements deterministic string wrapper and comparisons.
*/
#include "ui_ir_string.h"

static int domui_compare_bytes(const char* a, size_t a_len, const char* b, size_t b_len)
{
    size_t i;
    size_t n = (a_len < b_len) ? a_len : b_len;
    for (i = 0u; i < n; ++i) {
        unsigned char ca = (unsigned char)a[i];
        unsigned char cb = (unsigned char)b[i];
        if (ca < cb) {
            return -1;
        }
        if (ca > cb) {
            return 1;
        }
    }
    if (a_len < b_len) {
        return -1;
    }
    if (a_len > b_len) {
        return 1;
    }
    return 0;
}

domui_string::domui_string()
    : m_value()
{
}

domui_string::domui_string(const char* s)
    : m_value()
{
    if (s) {
        m_value = s;
    }
}

domui_string::domui_string(const std::string& s)
    : m_value(s)
{
}

const char* domui_string::c_str() const
{
    return m_value.c_str();
}

const std::string& domui_string::str() const
{
    return m_value;
}

size_t domui_string::size() const
{
    return m_value.size();
}

bool domui_string::empty() const
{
    return m_value.empty();
}

void domui_string::clear()
{
    m_value.clear();
}

void domui_string::set(const char* s)
{
    if (s) {
        m_value = s;
    } else {
        m_value.clear();
    }
}

void domui_string::set_bytes(const char* s, size_t len)
{
    if (!s || len == 0u) {
        m_value.clear();
        return;
    }
    m_value.assign(s, len);
}

int domui_string_compare(const domui_string& a, const domui_string& b)
{
    return domui_compare_bytes(a.str().c_str(), a.str().size(), b.str().c_str(), b.str().size());
}

bool domui_string_less(const domui_string& a, const domui_string& b)
{
    return domui_string_compare(a, b) < 0;
}

bool domui_string_equal(const domui_string& a, const domui_string& b)
{
    return domui_string_compare(a, b) == 0;
}
