/*
FILE: source/domino/ui_ir/ui_ir_diag.cpp
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / ui_ir diag
RESPONSIBILITY: Diagnostic collector for UI IR I/O and imports.
*/
#include "ui_ir_diag.h"

domui_diag_item::domui_diag_item()
    : message(),
      widget_id(0u),
      context()
{
}

domui_diag::domui_diag()
    : m_warnings(),
      m_errors()
{
}

void domui_diag::clear()
{
    m_warnings.clear();
    m_errors.clear();
}

void domui_diag::add_warning(const char* message, domui_widget_id widget_id, const char* context)
{
    domui_diag_item item;
    item.message.set(message ? message : "");
    item.widget_id = widget_id;
    item.context.set(context ? context : "");
    m_warnings.push_back(item);
}

void domui_diag::add_error(const char* message, domui_widget_id widget_id, const char* context)
{
    domui_diag_item item;
    item.message.set(message ? message : "");
    item.widget_id = widget_id;
    item.context.set(context ? context : "");
    m_errors.push_back(item);
}

void domui_diag::add_warning(const domui_string& message, domui_widget_id widget_id, const domui_string& context)
{
    domui_diag_item item;
    item.message = message;
    item.widget_id = widget_id;
    item.context = context;
    m_warnings.push_back(item);
}

void domui_diag::add_error(const domui_string& message, domui_widget_id widget_id, const domui_string& context)
{
    domui_diag_item item;
    item.message = message;
    item.widget_id = widget_id;
    item.context = context;
    m_errors.push_back(item);
}

size_t domui_diag::warning_count() const
{
    return m_warnings.size();
}

size_t domui_diag::error_count() const
{
    return m_errors.size();
}

bool domui_diag::has_errors() const
{
    return !m_errors.empty();
}

const std::vector<domui_diag_item>& domui_diag::warnings() const
{
    return m_warnings;
}

const std::vector<domui_diag_item>& domui_diag::errors() const
{
    return m_errors;
}
