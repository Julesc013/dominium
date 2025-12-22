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
    doc.meta.doc_version = 1u;
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

int main(void)
{
    test_id_stability();
    test_child_order();
    test_prop_canonicalization();
    test_event_canonicalization();
    test_reparent_stability();
    test_tlv_roundtrip();
    test_json_stability();
    test_backup_rotation();
    test_legacy_import_smoke();

    if (g_failures != 0) {
        printf("UI IR tests failed: %d\n", g_failures);
        return 1;
    }
    printf("UI IR tests passed\n");
    return 0;
}
