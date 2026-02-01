/*
UI IR accessibility validation tests (DEV-OPS-0).
*/
#include "ui_validate.h"
#include "tests/test_version.h"

#include <stdio.h>

#define EXPECT(cond, msg) do { \
    if (!(cond)) { \
        fprintf(stderr, "FAIL: %s\n", msg); \
        return 1; \
    } \
} while (0)

static int expect_validate(domui_doc* doc, int expect_ok, const char* label)
{
    domui_diag diag;
    int ok = domui_validate_doc(doc, 0, &diag) ? 1 : 0;
    if (ok != expect_ok) {
        fprintf(stderr, "FAIL: %s validation=%d expected=%d\n", label, ok, expect_ok);
        return 0;
    }
    if (!expect_ok && diag.error_count() == 0u) {
        fprintf(stderr, "FAIL: %s expected errors\n", label);
        return 0;
    }
    return 1;
}

int main(void)
{
    domui_doc doc;
    domui_widget_id root_id;
    domui_widget_id button_id;
    domui_widget* button;

    print_version_banner();

    root_id = doc.create_widget(DOMUI_WIDGET_CONTAINER, 0u);
    EXPECT(root_id != 0u, "root widget create");
    button_id = doc.create_widget(DOMUI_WIDGET_BUTTON, root_id);
    EXPECT(button_id != 0u, "button widget create");

    button = doc.find_by_id(button_id);
    EXPECT(button != 0, "button lookup");
    button->events.set("activate", "cmd.test");

    EXPECT(expect_validate(&doc, 0, "missing accessibility"), "validate missing accessibility");

    button->props.set("accessibility.name", domui_value_string(domui_string("Start")));
    button->props.set("accessibility.role", domui_value_string(domui_string("button")));
    button->props.set("accessibility.description", domui_value_string(domui_string("Start action")));

    EXPECT(expect_validate(&doc, 1, "accessibility present"), "validate accessibility present");

    return 0;
}
