/*
FILE: source/domino/ui_ir/ui_ir_diag.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / ui_ir diag
RESPONSIBILITY: Diagnostic collector for UI IR I/O and imports.
ALLOWED DEPENDENCIES: C++98 standard headers only.
FORBIDDEN DEPENDENCIES: UI backends, launcher, TLV I/O.
THREADING MODEL: Caller-managed; no internal synchronization.
ERROR MODEL: Stores warnings/errors; does not print.
DETERMINISM: Stable append order for diagnostics.
*/
#ifndef DOMINO_UI_IR_DIAG_H_INCLUDED
#define DOMINO_UI_IR_DIAG_H_INCLUDED

#include <vector>

#include "ui_ir_string.h"
#include "ui_ir_types.h"

typedef struct domui_diag_item {
    domui_string message;
    domui_widget_id widget_id;
    domui_string context;

    domui_diag_item();
} domui_diag_item;

class domui_diag {
public:
    domui_diag();

    void clear();

    void add_warning(const char* message, domui_widget_id widget_id, const char* context);
    void add_error(const char* message, domui_widget_id widget_id, const char* context);

    void add_warning(const domui_string& message, domui_widget_id widget_id, const domui_string& context);
    void add_error(const domui_string& message, domui_widget_id widget_id, const domui_string& context);

    size_t warning_count() const;
    size_t error_count() const;
    bool has_errors() const;

    const std::vector<domui_diag_item>& warnings() const;
    const std::vector<domui_diag_item>& errors() const;

private:
    std::vector<domui_diag_item> m_warnings;
    std::vector<domui_diag_item> m_errors;
};

#endif /* DOMINO_UI_IR_DIAG_H_INCLUDED */
