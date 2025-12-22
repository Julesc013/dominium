/*
FILE: source/domino/ui_ir/tests/ui_ir_tests.cpp
MODULE: Tests
RESPONSIBILITY: Unit tests for UI IR canonicalization and ID stability.
*/
#include <stdio.h>
#include <string.h>
#include <vector>
#include <string>

#if defined(_WIN32)
#include <direct.h>
#else
#include <unistd.h>
#endif

#include "ui_ir_doc.h"
#include "ui_ir_diag.h"
#include "ui_ir_fileio.h"
#include "ui_ir_json.h"
#include "ui_ir_legacy_import.h"
#include "ui_ir_tlv.h"
#include "ui_layout.h"
#include "ui_validate.h"

static int g_failures = 0;

#define TEST_CHECK(cond) \
    do { \
        if (!(cond)) { \
            printf("FAIL: %s:%d: %s\n", __FILE__, __LINE__, #cond); \
            g_failures += 1; \
        } \
    } while (0)

static bool domui_find_layout_rect(const domui_layout_result* results,
                                   int count,
                                   domui_widget_id widget_id,
                                   domui_layout_rect* out_rect)
{
    int i;
    if (!results || count <= 0) {
        return false;
    }
    for (i = 0; i < count; ++i) {
        if (results[i].widget_id == widget_id) {
            if (out_rect) {
                *out_rect = results[i].rect;
            }
            return true;
        }
    }
    return false;
}

static void domui_check_layout_rect(const domui_layout_rect& rect,
                                    int x,
                                    int y,
                                    int w,
                                    int h)
{
    TEST_CHECK(rect.x == x);
    TEST_CHECK(rect.y == y);
    TEST_CHECK(rect.w == w);
    TEST_CHECK(rect.h == h);
}

static bool domui_layout_results_equal(const domui_layout_result* a,
                                       int count_a,
                                       const domui_layout_result* b,
                                       int count_b)
{
    int i;
    if (count_a != count_b) {
        return false;
    }
    for (i = 0; i < count_a; ++i) {
        if (a[i].widget_id != b[i].widget_id) {
            return false;
        }
        if (a[i].rect.x != b[i].rect.x ||
            a[i].rect.y != b[i].rect.y ||
            a[i].rect.w != b[i].rect.w ||
            a[i].rect.h != b[i].rect.h) {
            return false;
        }
    }
    return true;
}

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

static void test_layout_absolute(void)
{
    domui_doc doc;
    domui_widget_id root = doc.create_widget(DOMUI_WIDGET_CONTAINER, 0u);
    domui_widget_id child = doc.create_widget(DOMUI_WIDGET_BUTTON, root);
    domui_widget_id label = doc.create_widget(DOMUI_WIDGET_STATIC_TEXT, root);
    domui_widget* w;

    w = doc.find_by_id(root);
    w->padding.left = 5;
    w->padding.top = 6;
    w->padding.right = 7;
    w->padding.bottom = 8;

    w = doc.find_by_id(child);
    w->x = 10;
    w->y = 20;
    w->w = 30;
    w->h = 40;
    w->margin.left = 2;
    w->margin.top = 1;

    w = doc.find_by_id(label);
    w->x = 0;
    w->y = 0;
    w->w = 15;
    w->h = 10;

    {
        domui_layout_result results[8];
        int count = 8;
        domui_diag diag;
        domui_layout_rect rect;

        TEST_CHECK(domui_compute_layout(&doc, root, 0, 0, 200, 100, results, &count, &diag));
        TEST_CHECK(count == 3);

        TEST_CHECK(domui_find_layout_rect(results, count, root, &rect));
        domui_check_layout_rect(rect, 0, 0, 200, 100);

        TEST_CHECK(domui_find_layout_rect(results, count, child, &rect));
        domui_check_layout_rect(rect, 17, 27, 30, 40);

        TEST_CHECK(domui_find_layout_rect(results, count, label, &rect));
        domui_check_layout_rect(rect, 5, 6, 15, 10);
    }
}

static void test_layout_anchor(void)
{
    domui_doc doc;
    domui_widget_id root = doc.create_widget(DOMUI_WIDGET_CONTAINER, 0u);
    domui_widget_id stretch = doc.create_widget(DOMUI_WIDGET_BUTTON, root);
    domui_widget_id right = doc.create_widget(DOMUI_WIDGET_STATIC_TEXT, root);
    domui_widget* w;

    w = doc.find_by_id(stretch);
    w->anchors = DOMUI_ANCHOR_L | DOMUI_ANCHOR_R | DOMUI_ANCHOR_T;
    w->x = 10;
    w->w = 20;
    w->y = 5;
    w->h = 15;

    w = doc.find_by_id(right);
    w->anchors = DOMUI_ANCHOR_R | DOMUI_ANCHOR_T;
    w->x = 8;
    w->w = 30;
    w->y = 4;
    w->h = 10;

    {
        domui_layout_result results[8];
        int count = 8;
        domui_diag diag;
        domui_layout_rect rect;

        TEST_CHECK(domui_compute_layout(&doc, root, 0, 0, 100, 50, results, &count, &diag));
        TEST_CHECK(domui_find_layout_rect(results, count, stretch, &rect));
        domui_check_layout_rect(rect, 10, 5, 70, 15);
        TEST_CHECK(domui_find_layout_rect(results, count, right, &rect));
        domui_check_layout_rect(rect, 62, 4, 30, 10);

        count = 8;
        TEST_CHECK(domui_compute_layout(&doc, root, 0, 0, 140, 50, results, &count, &diag));
        TEST_CHECK(domui_find_layout_rect(results, count, stretch, &rect));
        domui_check_layout_rect(rect, 10, 5, 110, 15);
        TEST_CHECK(domui_find_layout_rect(results, count, right, &rect));
        domui_check_layout_rect(rect, 102, 4, 30, 10);
    }
}

static void test_layout_dock(void)
{
    domui_doc doc;
    domui_widget_id root = doc.create_widget(DOMUI_WIDGET_CONTAINER, 0u);
    domui_widget_id left = doc.create_widget(DOMUI_WIDGET_BUTTON, root);
    domui_widget_id top = doc.create_widget(DOMUI_WIDGET_STATIC_TEXT, root);
    domui_widget_id fill = doc.create_widget(DOMUI_WIDGET_EDIT, root);
    domui_widget* w;

    w = doc.find_by_id(left);
    w->dock = DOMUI_DOCK_LEFT;
    w->w = 10;

    w = doc.find_by_id(top);
    w->dock = DOMUI_DOCK_TOP;
    w->h = 5;

    w = doc.find_by_id(fill);
    w->dock = DOMUI_DOCK_FILL;

    {
        domui_layout_result results[8];
        int count = 8;
        domui_diag diag;
        domui_layout_rect rect;

        TEST_CHECK(domui_compute_layout(&doc, root, 0, 0, 100, 100, results, &count, &diag));
        TEST_CHECK(domui_find_layout_rect(results, count, left, &rect));
        domui_check_layout_rect(rect, 0, 0, 10, 100);
        TEST_CHECK(domui_find_layout_rect(results, count, top, &rect));
        domui_check_layout_rect(rect, 10, 0, 90, 5);
        TEST_CHECK(domui_find_layout_rect(results, count, fill, &rect));
        domui_check_layout_rect(rect, 10, 5, 90, 95);
    }
}

static void test_layout_stack(void)
{
    domui_doc doc;
    domui_widget_id root = doc.create_widget(DOMUI_WIDGET_CONTAINER, 0u);
    domui_widget_id a = doc.create_widget(DOMUI_WIDGET_BUTTON, root);
    domui_widget_id b = doc.create_widget(DOMUI_WIDGET_BUTTON, root);
    domui_widget* w;

    w = doc.find_by_id(root);
    w->layout_mode = DOMUI_LAYOUT_STACK_ROW;

    w = doc.find_by_id(a);
    w->w = 30;
    w->h = 10;
    w->min_w = 40;
    w->margin.left = 2;
    w->margin.right = 2;

    w = doc.find_by_id(b);
    w->w = 20;
    w->h = 12;
    w->max_w = 15;
    w->margin.left = 1;
    w->margin.right = 1;

    {
        domui_layout_result results[8];
        int count = 8;
        domui_diag diag;
        domui_layout_rect rect;

        TEST_CHECK(domui_compute_layout(&doc, root, 0, 0, 100, 30, results, &count, &diag));
        TEST_CHECK(domui_find_layout_rect(results, count, a, &rect));
        domui_check_layout_rect(rect, 2, 0, 40, 10);
        TEST_CHECK(domui_find_layout_rect(results, count, b, &rect));
        domui_check_layout_rect(rect, 45, 0, 15, 12);
    }
}

static void test_layout_splitter(void)
{
    domui_doc doc;
    domui_widget_id root = doc.create_widget(DOMUI_WIDGET_CONTAINER, 0u);
    domui_widget_id splitter = doc.create_widget(DOMUI_WIDGET_SPLITTER, root);
    domui_widget_id a = doc.create_widget(DOMUI_WIDGET_BUTTON, splitter);
    domui_widget_id b = doc.create_widget(DOMUI_WIDGET_BUTTON, splitter);
    domui_widget* w;

    w = doc.find_by_id(splitter);
    w->x = 0;
    w->y = 0;
    w->w = 100;
    w->h = 50;
    w->props.set("splitter.orientation", domui_value_string(domui_string("v")));
    w->props.set("splitter.pos", domui_value_int(30));
    w->props.set("splitter.thickness", domui_value_int(4));

    {
        domui_layout_result results[8];
        int count = 8;
        domui_diag diag;
        domui_layout_rect rect;

        TEST_CHECK(domui_compute_layout(&doc, root, 0, 0, 100, 50, results, &count, &diag));
        TEST_CHECK(domui_find_layout_rect(results, count, a, &rect));
        domui_check_layout_rect(rect, 0, 0, 30, 50);
        TEST_CHECK(domui_find_layout_rect(results, count, b, &rect));
        domui_check_layout_rect(rect, 34, 0, 66, 50);
    }
}

static void test_layout_tabs(void)
{
    domui_doc doc;
    domui_widget_id root = doc.create_widget(DOMUI_WIDGET_CONTAINER, 0u);
    domui_widget_id tabs = doc.create_widget(DOMUI_WIDGET_TABS, root);
    domui_widget_id page_a = doc.create_widget(DOMUI_WIDGET_TAB_PAGE, tabs);
    domui_widget_id page_b = doc.create_widget(DOMUI_WIDGET_TAB_PAGE, tabs);
    domui_widget* w;

    w = doc.find_by_id(tabs);
    w->x = 0;
    w->y = 0;
    w->w = 200;
    w->h = 100;
    w->props.set("tabs.selected_index", domui_value_int(1));
    w->props.set("tabs.placement", domui_value_string(domui_string("top")));

    {
        domui_layout_result results[8];
        int count = 8;
        domui_diag diag;
        domui_layout_rect rect;

        TEST_CHECK(domui_compute_layout(&doc, root, 0, 0, 200, 100, results, &count, &diag));
        TEST_CHECK(domui_find_layout_rect(results, count, page_a, &rect));
        domui_check_layout_rect(rect, 0, 0, 0, 0);
        TEST_CHECK(domui_find_layout_rect(results, count, page_b, &rect));
        domui_check_layout_rect(rect, 0, 24, 200, 76);
    }
}

static void test_layout_scrollpanel(void)
{
    domui_doc doc;
    domui_widget_id root = doc.create_widget(DOMUI_WIDGET_CONTAINER, 0u);
    domui_widget_id scroll = doc.create_widget(DOMUI_WIDGET_SCROLLPANEL, root);
    domui_widget_id content = doc.create_widget(DOMUI_WIDGET_CONTAINER, scroll);
    domui_widget* w;

    w = doc.find_by_id(scroll);
    w->x = 0;
    w->y = 0;
    w->w = 100;
    w->h = 100;

    w = doc.find_by_id(content);
    w->w = 200;
    w->h = 150;

    {
        domui_layout_result results[8];
        int count = 8;
        domui_diag diag;
        domui_layout_rect rect;

        TEST_CHECK(domui_compute_layout(&doc, root, 0, 0, 100, 100, results, &count, &diag));
        TEST_CHECK(domui_find_layout_rect(results, count, content, &rect));
        domui_check_layout_rect(rect, 0, 0, 200, 150);
    }
}

static void test_layout_determinism(void)
{
    domui_doc doc_a;
    domui_doc doc_b;
    domui_widget_id root_a = doc_a.create_widget(DOMUI_WIDGET_CONTAINER, 0u);
    domui_widget_id child_a = doc_a.create_widget(DOMUI_WIDGET_BUTTON, root_a);
    domui_widget_id child_b = doc_a.create_widget(DOMUI_WIDGET_BUTTON, root_a);
    domui_widget* w;

    w = doc_a.find_by_id(child_a);
    w->x = 10;
    w->y = 10;
    w->w = 20;
    w->h = 10;
    w->z_order = 1u;

    w = doc_a.find_by_id(child_b);
    w->x = 40;
    w->y = 10;
    w->w = 20;
    w->h = 10;
    w->z_order = 0u;

    {
        domui_widget wroot;
        domui_widget wa;
        domui_widget wb;

        wroot.id = 1u;
        wroot.type = DOMUI_WIDGET_CONTAINER;
        wroot.parent_id = 0u;

        wa.id = 2u;
        wa.type = DOMUI_WIDGET_BUTTON;
        wa.parent_id = 1u;
        wa.x = 10;
        wa.y = 10;
        wa.w = 20;
        wa.h = 10;
        wa.z_order = 1u;

        wb.id = 3u;
        wb.type = DOMUI_WIDGET_BUTTON;
        wb.parent_id = 1u;
        wb.x = 40;
        wb.y = 10;
        wb.w = 20;
        wb.h = 10;
        wb.z_order = 0u;

        TEST_CHECK(doc_b.insert_widget_with_id(wb));
        TEST_CHECK(doc_b.insert_widget_with_id(wroot));
        TEST_CHECK(doc_b.insert_widget_with_id(wa));
    }

    {
        domui_layout_result results_a[8];
        domui_layout_result results_b[8];
        int count_a = 8;
        int count_b = 8;
        domui_diag diag;

        TEST_CHECK(domui_compute_layout(&doc_a, root_a, 0, 0, 100, 50, results_a, &count_a, &diag));
        TEST_CHECK(domui_compute_layout(&doc_b, 1u, 0, 0, 100, 50, results_b, &count_b, &diag));
        TEST_CHECK(domui_layout_results_equal(results_a, count_a, results_b, count_b));
    }
}

static void domui_cleanup_file_family(const char* path)
{
    char buf[512];
    int i;
    if (!path || !path[0]) {
        return;
    }
    (void)remove(path);
    snprintf(buf, sizeof(buf), "%s.tmp", path);
    (void)remove(buf);
    for (i = 1; i <= 10; ++i) {
        snprintf(buf, sizeof(buf), "%s.bak%d", path, i);
        (void)remove(buf);
    }
}

static std::string domui_json_path_from_tlv(const char* path)
{
    std::string p = path ? path : "";
    size_t pos = p.rfind('.');
    if (pos != std::string::npos) {
        p = p.substr(0u, pos);
    }
    p += ".json";
    return p;
}

static void domui_cleanup_tlv_with_json(const char* tlv_path)
{
    std::string json = domui_json_path_from_tlv(tlv_path);
    domui_cleanup_file_family(tlv_path);
    domui_cleanup_file_family(json.c_str());
}

static bool domui_file_exists(const char* path)
{
    FILE* f;
    if (!path || !path[0]) {
        return false;
    }
    f = fopen(path, "rb");
    if (f) {
        fclose(f);
        return true;
    }
    return false;
}

static bool domui_bytes_equal(const std::vector<unsigned char>& a, const std::vector<unsigned char>& b)
{
    if (a.size() != b.size()) {
        return false;
    }
    if (a.empty()) {
        return true;
    }
    return memcmp(&a[0], &b[0], a.size()) == 0;
}

static void domui_fill_sample_doc(domui_doc& doc, const char* name)
{
    domui_widget_id root;
    domui_widget_id button;
    domui_widget_id label;
    domui_widget* w;

    doc.clear();
    doc.meta.doc_version = 2u;
    doc.meta.doc_name.set(name ? name : "");
    doc.meta.target_backends.push_back(domui_string("win32"));
    doc.meta.target_tiers.push_back(domui_string("win32_t1"));

    root = doc.create_widget(DOMUI_WIDGET_CONTAINER, 0u);
    button = doc.create_widget(DOMUI_WIDGET_BUTTON, root);
    label = doc.create_widget(DOMUI_WIDGET_STATIC_TEXT, root);

    w = doc.find_by_id(root);
    if (w) {
        w->layout_mode = DOMUI_LAYOUT_STACK_ROW;
        w->x = 0;
        w->y = 0;
        w->w = 640;
        w->h = 480;
        w->margin.left = 4;
        w->margin.right = 4;
        w->margin.top = 8;
        w->margin.bottom = 8;
        w->padding.left = 2;
        w->padding.right = 2;
        w->padding.top = 2;
        w->padding.bottom = 2;
        w->props.set("root.title", domui_value_string(domui_string("root")));
    }

    w = doc.find_by_id(button);
    if (w) {
        w->z_order = 2u;
        w->x = 10;
        w->y = 10;
        w->w = 120;
        w->h = 24;
        w->props.set("label", domui_value_string(domui_string("OK")));
        w->events.set("on_click", "action.ok");
    }

    w = doc.find_by_id(label);
    if (w) {
        w->z_order = 1u;
        w->x = 10;
        w->y = 40;
        w->w = 240;
        w->h = 20;
        w->props.set("text", domui_value_string(domui_string("Status")));
    }
}

static void domui_fill_widget_doc(domui_doc& doc, const char* name)
{
    domui_widget_id root;
    domui_widget_id splitter;
    domui_widget_id pane_a;
    domui_widget_id pane_b;
    domui_widget_id tabs;
    domui_widget_id page_a;
    domui_widget_id page_b;
    domui_widget_id scroll;
    domui_widget_id scroll_content;
    domui_widget* w;

    doc.clear();
    doc.meta.doc_version = 2u;
    doc.meta.doc_name.set(name ? name : "");
    doc.meta.target_backends.push_back(domui_string("win32"));
    doc.meta.target_tiers.push_back(domui_string("win32_t1"));

    root = doc.create_widget(DOMUI_WIDGET_CONTAINER, 0u);
    splitter = doc.create_widget(DOMUI_WIDGET_SPLITTER, root);
    pane_a = doc.create_widget(DOMUI_WIDGET_CONTAINER, splitter);
    pane_b = doc.create_widget(DOMUI_WIDGET_CONTAINER, splitter);

    w = doc.find_by_id(splitter);
    if (w) {
        w->x = 0;
        w->y = 0;
        w->w = 400;
        w->h = 200;
        w->props.set("splitter.orientation", domui_value_string(domui_string("v")));
        w->props.set("splitter.pos", domui_value_int(140));
        w->props.set("splitter.thickness", domui_value_int(4));
        w->props.set("splitter.min_a", domui_value_int(40));
        w->props.set("splitter.min_b", domui_value_int(40));
    }

    tabs = doc.create_widget(DOMUI_WIDGET_TABS, pane_a);
    page_a = doc.create_widget(DOMUI_WIDGET_TAB_PAGE, tabs);
    page_b = doc.create_widget(DOMUI_WIDGET_TAB_PAGE, tabs);

    w = doc.find_by_id(tabs);
    if (w) {
        w->x = 0;
        w->y = 0;
        w->w = 200;
        w->h = 180;
        w->props.set("tabs.selected_index", domui_value_int(1));
        w->props.set("tabs.placement", domui_value_string(domui_string("top")));
    }
    w = doc.find_by_id(page_a);
    if (w) {
        w->props.set("tab.title", domui_value_string(domui_string("First")));
        w->props.set("tab.enabled", domui_value_bool(1));
    }
    w = doc.find_by_id(page_b);
    if (w) {
        w->props.set("tab.title", domui_value_string(domui_string("Second")));
        w->props.set("tab.enabled", domui_value_bool(1));
    }

    scroll = doc.create_widget(DOMUI_WIDGET_SCROLLPANEL, pane_b);
    scroll_content = doc.create_widget(DOMUI_WIDGET_CONTAINER, scroll);
    w = doc.find_by_id(scroll);
    if (w) {
        w->x = 0;
        w->y = 0;
        w->w = 200;
        w->h = 180;
        w->props.set("scroll.h_enabled", domui_value_bool(1));
        w->props.set("scroll.v_enabled", domui_value_bool(1));
        w->props.set("scroll.x", domui_value_int(0));
        w->props.set("scroll.y", domui_value_int(0));
    }
    w = doc.find_by_id(scroll_content);
    if (w) {
        w->w = 320;
        w->h = 240;
    }
}

static void test_tlv_roundtrip(void)
{
    const char* path_a = "ui_ir_test_roundtrip.tlv";
    const char* path_b = "ui_ir_test_roundtrip_b.tlv";
    domui_doc doc;
    domui_doc doc2;
    domui_diag diag;
    std::vector<unsigned char> a_bytes;
    std::vector<unsigned char> b_bytes;

    domui_cleanup_tlv_with_json(path_a);
    domui_cleanup_tlv_with_json(path_b);

    domui_fill_sample_doc(doc, "roundtrip");
    TEST_CHECK(domui_doc_save_tlv(&doc, path_a, &diag));
    TEST_CHECK(domui_doc_load_tlv(&doc2, path_a, &diag));
    TEST_CHECK(domui_doc_save_tlv(&doc2, path_b, &diag));

    TEST_CHECK(domui_read_file_bytes(path_a, a_bytes, &diag));
    TEST_CHECK(domui_read_file_bytes(path_b, b_bytes, &diag));
    TEST_CHECK(domui_bytes_equal(a_bytes, b_bytes));
}

static void test_tlv_roundtrip_v2_widgets(void)
{
    const char* path_a = "ui_ir_test_roundtrip_v2.tlv";
    const char* path_b = "ui_ir_test_roundtrip_v2_b.tlv";
    domui_doc doc;
    domui_doc doc2;
    domui_diag diag;
    std::vector<unsigned char> a_bytes;
    std::vector<unsigned char> b_bytes;

    domui_cleanup_tlv_with_json(path_a);
    domui_cleanup_tlv_with_json(path_b);

    domui_fill_widget_doc(doc, "roundtrip_v2");
    TEST_CHECK(domui_doc_save_tlv(&doc, path_a, &diag));
    TEST_CHECK(domui_doc_load_tlv(&doc2, path_a, &diag));
    TEST_CHECK(domui_doc_save_tlv(&doc2, path_b, &diag));

    TEST_CHECK(domui_read_file_bytes(path_a, a_bytes, &diag));
    TEST_CHECK(domui_read_file_bytes(path_b, b_bytes, &diag));
    TEST_CHECK(domui_bytes_equal(a_bytes, b_bytes));
}

static void test_json_stability(void)
{
    const char* json_path = "ui_ir_test_json.json";
    domui_doc doc;
    domui_diag diag;
    std::vector<unsigned char> a_bytes;
    std::vector<unsigned char> b_bytes;

    domui_cleanup_file_family(json_path);

    domui_fill_sample_doc(doc, "json_stability");
    TEST_CHECK(domui_doc_save_json_mirror(&doc, json_path, &diag));
    TEST_CHECK(domui_read_file_bytes(json_path, a_bytes, &diag));
    TEST_CHECK(domui_doc_save_json_mirror(&doc, json_path, &diag));
    TEST_CHECK(domui_read_file_bytes(json_path, b_bytes, &diag));
    TEST_CHECK(domui_bytes_equal(a_bytes, b_bytes));
}

static void test_backup_rotation(void)
{
    const char* path = "ui_ir_test_backup.tlv";
    char bak1[512];
    domui_doc doc;
    domui_diag diag;
    std::vector<unsigned char> cur_bytes;
    std::vector<unsigned char> bak_bytes;

    domui_cleanup_tlv_with_json(path);

    domui_fill_sample_doc(doc, "backup_first");
    TEST_CHECK(domui_doc_save_tlv(&doc, path, &diag));

    domui_fill_sample_doc(doc, "backup_second");
    TEST_CHECK(domui_doc_save_tlv(&doc, path, &diag));

    snprintf(bak1, sizeof(bak1), "%s.bak1", path);
    TEST_CHECK(domui_file_exists(bak1));

    TEST_CHECK(domui_read_file_bytes(path, cur_bytes, &diag));
    TEST_CHECK(domui_read_file_bytes(bak1, bak_bytes, &diag));
    TEST_CHECK(!domui_bytes_equal(cur_bytes, bak_bytes));
}

static bool domui_get_cwd(std::string& out)
{
    char buf[512];
#if defined(_WIN32)
    if (!_getcwd(buf, sizeof(buf))) {
        return false;
    }
#else
    if (!getcwd(buf, sizeof(buf))) {
        return false;
    }
#endif
    out = buf;
    return true;
}

static bool domui_find_legacy_path(std::string& out_path)
{
    std::string cur;
    if (!domui_get_cwd(cur)) {
        return false;
    }
    while (!cur.empty()) {
        std::string candidate = cur + "/source/dominium/launcher/ui_schema/launcher_ui_v1.tlv";
        if (domui_file_exists(candidate.c_str())) {
            out_path = candidate;
            return true;
        }
        {
            size_t pos = cur.find_last_of("\\/");
            if (pos == std::string::npos) {
                break;
            }
            cur = cur.substr(0u, pos);
        }
    }
    return false;
}

static void test_legacy_import_smoke(void)
{
    std::string legacy_path;
    domui_doc doc;
    domui_diag diag;
    if (!domui_find_legacy_path(legacy_path)) {
        printf("SKIP: legacy import (launcher_ui_v1.tlv not found)\n");
        return;
    }
    TEST_CHECK(domui_doc_import_legacy_launcher_tlv(&doc, legacy_path.c_str(), &diag));
    TEST_CHECK(doc.widget_count() > 0u);
}

static std::string domui_diag_to_string(const domui_diag& diag)
{
    std::string out;
    size_t i;
    char buf[64];
    out += "errors\n";
    for (i = 0u; i < diag.errors().size(); ++i) {
        const domui_diag_item& item = diag.errors()[i];
        snprintf(buf, sizeof(buf), "%u", (unsigned int)item.widget_id);
        out += item.message.str();
        out += "|";
        out += buf;
        out += "|";
        out += item.context.str();
        out += "\n";
    }
    out += "warnings\n";
    for (i = 0u; i < diag.warnings().size(); ++i) {
        const domui_diag_item& item = diag.warnings()[i];
        snprintf(buf, sizeof(buf), "%u", (unsigned int)item.widget_id);
        out += item.message.str();
        out += "|";
        out += buf;
        out += "|";
        out += item.context.str();
        out += "\n";
    }
    return out;
}

static void domui_fill_listview_doc(domui_doc& doc)
{
    domui_widget_id root;
    domui_widget_id listview;
    domui_widget* w;
    doc.clear();
    root = doc.create_widget(DOMUI_WIDGET_CONTAINER, 0u);
    listview = doc.create_widget(DOMUI_WIDGET_LISTVIEW, root);
    w = doc.find_by_id(listview);
    if (w) {
        w->props.set("listview.columns", domui_value_uint(3u));
        w->props.set("items", domui_value_string(domui_string("a,b,c")));
    }
}

static void test_validation_win32_t1_pass(void)
{
    domui_doc doc;
    domui_diag diag;
    domui_target_set targets;
    domui_fill_listview_doc(doc);
    targets.backends.push_back(domui_string("win32"));
    targets.tiers.push_back(domui_string("win32_t1"));
    TEST_CHECK(domui_validate_doc(&doc, &targets, &diag));
    TEST_CHECK(!diag.has_errors());
}

static void test_validation_win32_t0_fail(void)
{
    domui_doc doc;
    domui_diag diag;
    domui_target_set targets;
    domui_fill_listview_doc(doc);
    targets.backends.push_back(domui_string("win32"));
    targets.tiers.push_back(domui_string("win32_t0"));
    TEST_CHECK(!domui_validate_doc(&doc, &targets, &diag));
    TEST_CHECK(diag.error_count() > 0u);
}

static void test_validation_determinism(void)
{
    domui_doc doc;
    domui_diag diag_a;
    domui_diag diag_b;
    domui_target_set targets;
    std::string a;
    std::string b;
    domui_fill_listview_doc(doc);
    targets.backends.push_back(domui_string("win32"));
    targets.tiers.push_back(domui_string("win32_t0"));
    (void)domui_validate_doc(&doc, &targets, &diag_a);
    (void)domui_validate_doc(&doc, &targets, &diag_b);
    a = domui_diag_to_string(diag_a);
    b = domui_diag_to_string(diag_b);
    TEST_CHECK(a == b);
}

int main(void)
{
    test_id_stability();
    test_child_order();
    test_prop_canonicalization();
    test_event_canonicalization();
    test_reparent_stability();
    test_layout_absolute();
    test_layout_anchor();
    test_layout_dock();
    test_layout_stack();
    test_layout_splitter();
    test_layout_tabs();
    test_layout_scrollpanel();
    test_layout_determinism();
    test_tlv_roundtrip();
    test_tlv_roundtrip_v2_widgets();
    test_json_stability();
    test_backup_rotation();
    test_legacy_import_smoke();
    test_validation_win32_t1_pass();
    test_validation_win32_t0_fail();
    test_validation_determinism();

    if (g_failures != 0) {
        printf("UI IR tests failed: %d\n", g_failures);
        return 1;
    }
    printf("UI IR tests passed\n");
    return 0;
}
