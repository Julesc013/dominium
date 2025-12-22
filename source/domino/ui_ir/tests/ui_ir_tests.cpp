/*
FILE: source/domino/ui_ir/tests/ui_ir_tests.cpp
MODULE: Tests
RESPONSIBILITY: Unit tests for UI IR canonicalization and ID stability.
*/
#include <stdio.h>
#include <vector>

#include "ui_ir_doc.h"

static int g_failures = 0;

#define TEST_CHECK(cond) \
    do { \
        if (!(cond)) { \
            printf("FAIL: %s:%d: %s\n", __FILE__, __LINE__, #cond); \
            g_failures += 1; \
        } \
    } while (0)

static void test_id_stability(void)
{
    domui_doc doc;
    domui_widget_id a = doc.create_widget(DOMUI_WIDGET_CONTAINER, 0u);
    domui_widget_id b = doc.create_widget(DOMUI_WIDGET_BUTTON, 0u);
    domui_widget_id c = doc.create_widget(DOMUI_WIDGET_EDIT, 0u);
    TEST_CHECK(a == 1u);
    TEST_CHECK(b == 2u);
    TEST_CHECK(c == 3u);
    TEST_CHECK(doc.delete_widget(b));
    {
        domui_widget_id d = doc.create_widget(DOMUI_WIDGET_LISTBOX, 0u);
        TEST_CHECK(d == 4u);
    }
    TEST_CHECK(doc.next_id() == 5u);
}

static void test_child_order(void)
{
    domui_doc doc;
    domui_widget_id parent = doc.create_widget(DOMUI_WIDGET_CONTAINER, 0u);
    domui_widget_id c1 = doc.create_widget(DOMUI_WIDGET_BUTTON, parent);
    domui_widget_id c2 = doc.create_widget(DOMUI_WIDGET_BUTTON, parent);
    domui_widget_id c3 = doc.create_widget(DOMUI_WIDGET_BUTTON, parent);

    doc.find_by_id(c1)->z_order = 5u;
    doc.find_by_id(c2)->z_order = 1u;
    doc.find_by_id(c3)->z_order = 5u;

    {
        std::vector<domui_widget_id> children;
        doc.enumerate_children(parent, children);
        TEST_CHECK(children.size() == 3u);
        TEST_CHECK(children[0] == c2);
        TEST_CHECK(children[1] == c1);
        TEST_CHECK(children[2] == c3);
    }
}

static void test_prop_canonicalization(void)
{
    domui_props props;
    props.set("b", domui_value_int(1));
    props.set("a", domui_value_int(2));
    props.set("c", domui_value_int(3));

    {
        std::vector<domui_string> keys;
        props.canonical_keys(keys);
        TEST_CHECK(keys.size() == 3u);
        TEST_CHECK(domui_string_equal(keys[0], domui_string("a")));
        TEST_CHECK(domui_string_equal(keys[1], domui_string("b")));
        TEST_CHECK(domui_string_equal(keys[2], domui_string("c")));
    }
}

static void test_event_canonicalization(void)
{
    domui_events events;
    events.set("on_submit", "act_submit");
    events.set("on_change", "act_change");
    events.set("on_click", "act_click");

    {
        std::vector<domui_string> names;
        events.canonical_event_names(names);
        TEST_CHECK(names.size() == 3u);
        TEST_CHECK(domui_string_equal(names[0], domui_string("on_change")));
        TEST_CHECK(domui_string_equal(names[1], domui_string("on_click")));
        TEST_CHECK(domui_string_equal(names[2], domui_string("on_submit")));
    }
}

static void test_reparent_stability(void)
{
    domui_doc doc;
    domui_widget_id a = doc.create_widget(DOMUI_WIDGET_CONTAINER, 0u);
    domui_widget_id b = doc.create_widget(DOMUI_WIDGET_CONTAINER, 0u);
    domui_widget_id c = doc.create_widget(DOMUI_WIDGET_BUTTON, a);

    {
        std::vector<domui_widget_id> order;
        doc.canonical_widget_order(order);
        TEST_CHECK(order.size() == 3u);
        TEST_CHECK(order[0] == a);
        TEST_CHECK(order[1] == c);
        TEST_CHECK(order[2] == b);
    }

    TEST_CHECK(doc.reparent_widget(c, b, 0u));

    {
        std::vector<domui_widget_id> order;
        doc.canonical_widget_order(order);
        TEST_CHECK(order.size() == 3u);
        TEST_CHECK(order[0] == a);
        TEST_CHECK(order[1] == b);
        TEST_CHECK(order[2] == c);
    }
}

int main(void)
{
    test_id_stability();
    test_child_order();
    test_prop_canonicalization();
    test_event_canonicalization();
    test_reparent_stability();

    if (g_failures != 0) {
        printf("UI IR tests failed: %d\n", g_failures);
        return 1;
    }
    printf("UI IR tests passed\n");
    return 0;
}
