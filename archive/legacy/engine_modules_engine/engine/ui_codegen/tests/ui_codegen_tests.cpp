/*
FILE: source/domino/ui_codegen/tests/ui_codegen_tests.cpp
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / ui_codegen tests
RESPONSIBILITY: Headless tests for deterministic action codegen.
*/
#include "ui_codegen.h"

#include <cstdio>
#include <cstring>
#include <string>
#include <vector>

#if defined(_WIN32)
#include <direct.h>
#else
#include <sys/stat.h>
#include <sys/types.h>
#endif

#include "ui_ir_doc.h"
#include "ui_ir_fileio.h"
#include "ui_ir_tlv.h"

static int g_failures = 0;

#define TEST_CHECK(expr) \
    do { \
        if (!(expr)) { \
            std::printf("FAIL %s:%d: %s\n", __FILE__, __LINE__, #expr); \
            g_failures += 1; \
        } \
    } while (0)

static void test_mkdir(const char* path)
{
#if defined(_WIN32)
    _mkdir(path);
#else
    mkdir(path, 0755);
#endif
}

static bool read_file_text(const char* path, std::string& out)
{
    std::vector<unsigned char> bytes;
    out.clear();
    if (!domui_read_file_bytes(path, bytes, 0)) {
        return false;
    }
    if (!bytes.empty()) {
        out.assign((const char*)&bytes[0], bytes.size());
    }
    return true;
}

static void remove_file(const char* path)
{
    if (!path) {
        return;
    }
    std::remove(path);
}

static void fill_doc(domui_doc& doc, const char* name, const char* action_a, const char* action_b)
{
    domui_widget_id root;
    domui_widget_id button;
    domui_widget* w;

    doc.clear();
    doc.meta.doc_version = 2u;
    doc.meta.doc_name.set(name ? name : "");
    doc.meta.target_backends.push_back(domui_string("win32"));
    doc.meta.target_tiers.push_back(domui_string("win32_t1"));

    root = doc.create_widget(DOMUI_WIDGET_CONTAINER, 0u);
    button = doc.create_widget(DOMUI_WIDGET_BUTTON, root);
    w = doc.find_by_id(button);
    if (w) {
        if (action_a) {
            w->events.set("on_click", action_a);
        }
        if (action_b) {
            w->events.set("on_submit", action_b);
        }
    }
}

static void test_codegen_determinism(void)
{
    const char* dir = "ui_codegen_test_tmp";
    const char* tlv_path = "ui_codegen_test_tmp/ui_doc.tlv";
    const char* reg_path = "ui_codegen_test_tmp/registry.json";
    const char* gen_dir = "ui_codegen_test_tmp/gen";
    const char* user_dir = "ui_codegen_test_tmp/user";
    domui_doc doc;
    domui_diag diag;
    domui_codegen_params params;
    std::string a;
    std::string b;

    test_mkdir(dir);
    test_mkdir(gen_dir);
    test_mkdir(user_dir);
    remove_file(reg_path);
    remove_file(tlv_path);

    fill_doc(doc, "test_doc", "action.one", "action.two");
    TEST_CHECK(domui_doc_save_tlv(&doc, tlv_path, &diag));

    params.input_tlv_path = tlv_path;
    params.registry_path = reg_path;
    params.out_gen_dir = gen_dir;
    params.out_user_dir = user_dir;

    TEST_CHECK(domui_codegen_run(&params, &diag));
    TEST_CHECK(read_file_text("ui_codegen_test_tmp/gen/ui_test_doc_actions_gen.h", a));
    TEST_CHECK(domui_codegen_run(&params, &diag));
    TEST_CHECK(read_file_text("ui_codegen_test_tmp/gen/ui_test_doc_actions_gen.h", b));
    TEST_CHECK(a == b);
}

static void test_registry_stability(void)
{
    const char* dir = "ui_codegen_test_tmp2";
    const char* tlv_path = "ui_codegen_test_tmp2/ui_doc.tlv";
    const char* reg_path = "ui_codegen_test_tmp2/registry.json";
    const char* gen_dir = "ui_codegen_test_tmp2/gen";
    const char* user_dir = "ui_codegen_test_tmp2/user";
    domui_doc doc;
    domui_diag diag;
    domui_codegen_params params;
    domui_action_registry reg;
    domui_u32 id_first = 0u;
    domui_u32 id_second = 0u;

    test_mkdir(dir);
    test_mkdir(gen_dir);
    test_mkdir(user_dir);
    remove_file(reg_path);
    remove_file(tlv_path);

    fill_doc(doc, "test_doc", "alpha.action", "beta.action");
    TEST_CHECK(domui_doc_save_tlv(&doc, tlv_path, &diag));

    params.input_tlv_path = tlv_path;
    params.registry_path = reg_path;
    params.out_gen_dir = gen_dir;
    params.out_user_dir = user_dir;

    TEST_CHECK(domui_codegen_run(&params, &diag));
    TEST_CHECK(domui_action_registry_load(reg_path, &reg, &diag));
    if (reg.key_to_id.find("beta.action") != reg.key_to_id.end()) {
        id_first = reg.key_to_id["beta.action"];
    }

    fill_doc(doc, "test_doc", "alpha.action", 0);
    TEST_CHECK(domui_doc_save_tlv(&doc, tlv_path, &diag));
    TEST_CHECK(domui_codegen_run(&params, &diag));

    fill_doc(doc, "test_doc", "alpha.action", "beta.action");
    TEST_CHECK(domui_doc_save_tlv(&doc, tlv_path, &diag));
    TEST_CHECK(domui_codegen_run(&params, &diag));
    TEST_CHECK(domui_action_registry_load(reg_path, &reg, &diag));
    if (reg.key_to_id.find("beta.action") != reg.key_to_id.end()) {
        id_second = reg.key_to_id["beta.action"];
    }

    TEST_CHECK(id_first != 0u);
    TEST_CHECK(id_first == id_second);
}

static void test_stub_preservation(void)
{
    const char* dir = "ui_codegen_test_tmp3";
    const char* tlv_path = "ui_codegen_test_tmp3/ui_doc.tlv";
    const char* reg_path = "ui_codegen_test_tmp3/registry.json";
    const char* gen_dir = "ui_codegen_test_tmp3/gen";
    const char* user_dir = "ui_codegen_test_tmp3/user";
    const char* user_cpp = "ui_codegen_test_tmp3/user/ui_test_doc_actions_user.cpp";
    domui_doc doc;
    domui_diag diag;
    domui_codegen_params params;
    std::string content;

    test_mkdir(dir);
    test_mkdir(gen_dir);
    test_mkdir(user_dir);
    remove_file(reg_path);
    remove_file(tlv_path);

    fill_doc(doc, "test_doc", "keep.one", 0);
    TEST_CHECK(domui_doc_save_tlv(&doc, tlv_path, &diag));

    params.input_tlv_path = tlv_path;
    params.registry_path = reg_path;
    params.out_gen_dir = gen_dir;
    params.out_user_dir = user_dir;

    TEST_CHECK(domui_codegen_run(&params, &diag));
    TEST_CHECK(read_file_text(user_cpp, content));
    content = std::string("/* custom header */\n") + content;
    TEST_CHECK(domui_atomic_write_file(user_cpp, content.data(), content.size(), &diag));

    TEST_CHECK(domui_codegen_run(&params, &diag));
    TEST_CHECK(read_file_text(user_cpp, content));
    TEST_CHECK(content.find("custom header") != std::string::npos);
}

int main(void)
{
    test_codegen_determinism();
    test_registry_stability();
    test_stub_preservation();
    if (g_failures != 0) {
        std::printf("ui_codegen_tests: %d failure(s)\n", g_failures);
    }
    return g_failures ? 1 : 0;
}
