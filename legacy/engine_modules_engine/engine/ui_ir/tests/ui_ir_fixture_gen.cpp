/*
FILE: source/domino/ui_ir/tests/ui_ir_fixture_gen.cpp
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / ui_ir tests
RESPONSIBILITY: Generate canonical UI IR fixture TLV/JSON files for tests.
*/
#include <cstdio>
#include <cstring>
#include <string>
#include <vector>

#if defined(_WIN32)
#include <direct.h>
#else
#include <unistd.h>
#endif

#include "domino/io/container.h"

#include "ui_ir_doc.h"
#include "ui_ir_diag.h"
#include "ui_ir_fileio.h"
#include "ui_ir_json.h"
#include "ui_ir_tlv.h"

#define DOMUI_TAG(a,b,c,d) ((domui_u32)((domui_u32)(a) << 24u) | ((domui_u32)(b) << 16u) | ((domui_u32)(c) << 8u) | ((domui_u32)(d)))

static const domui_u32 DOMUI_TLV_DOC_VERSION = DOMUI_TAG('V','E','R','S');

static bool domui_file_exists(const char* path)
{
    FILE* f;
    if (!path || !path[0]) {
        return false;
    }
    f = std::fopen(path, "rb");
    if (!f) {
        return false;
    }
    std::fclose(f);
    return true;
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

static bool domui_find_repo_root(std::string& out_root)
{
    std::string cur;
    if (!domui_get_cwd(cur)) {
        return false;
    }
    while (!cur.empty()) {
        std::string marker = cur + "/docs/ui_editor/README.md";
        if (domui_file_exists(marker.c_str())) {
            out_root = cur;
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

static void domui_print_diag(const domui_diag& diag)
{
    size_t i;
    for (i = 0u; i < diag.errors().size(); ++i) {
        std::fprintf(stderr, "error: %s\n", diag.errors()[i].message.c_str());
    }
    for (i = 0u; i < diag.warnings().size(); ++i) {
        std::fprintf(stderr, "warning: %s\n", diag.warnings()[i].message.c_str());
    }
}

static void domui_set_defaults(domui_doc& doc, const char* name)
{
    doc.clear();
    doc.meta.doc_version = 2u;
    doc.meta.doc_name.set(name ? name : "");
    doc.meta.target_backends.push_back(domui_string("win32"));
    doc.meta.target_tiers.push_back(domui_string("win32_t1"));
}

static void build_fixture_abs(domui_doc& doc)
{
    domui_widget_id root;
    domui_widget_id button;
    domui_widget_id label;
    domui_widget* w;

    domui_set_defaults(doc, "fixture_abs");
    root = doc.create_widget(DOMUI_WIDGET_CONTAINER, 0u);
    button = doc.create_widget(DOMUI_WIDGET_BUTTON, root);
    label = doc.create_widget(DOMUI_WIDGET_STATIC_TEXT, root);

    w = doc.find_by_id(root);
    if (w) {
        w->name.set("root");
        w->x = 0;
        w->y = 0;
        w->w = 640;
        w->h = 480;
        w->padding.left = 8;
        w->padding.top = 6;
    }

    w = doc.find_by_id(button);
    if (w) {
        w->name.set("ok_button");
        w->x = 12;
        w->y = 16;
        w->w = 120;
        w->h = 28;
        w->props.set("text", domui_value_string(domui_string("OK")));
        w->events.set("on_click", "action.ok");
    }

    w = doc.find_by_id(label);
    if (w) {
        w->name.set("status_label");
        w->x = 12;
        w->y = 60;
        w->w = 200;
        w->h = 20;
        w->props.set("text", domui_value_string(domui_string("Ready")));
    }
}

static void build_fixture_dock(domui_doc& doc)
{
    domui_widget_id root;
    domui_widget_id left;
    domui_widget_id top;
    domui_widget_id fill;
    domui_widget* w;

    domui_set_defaults(doc, "fixture_dock");
    root = doc.create_widget(DOMUI_WIDGET_CONTAINER, 0u);
    left = doc.create_widget(DOMUI_WIDGET_GROUPBOX, root);
    top = doc.create_widget(DOMUI_WIDGET_STATIC_TEXT, root);
    fill = doc.create_widget(DOMUI_WIDGET_CONTAINER, root);

    w = doc.find_by_id(root);
    if (w) {
        w->name.set("root");
        w->w = 320;
        w->h = 200;
    }

    w = doc.find_by_id(left);
    if (w) {
        w->name.set("left_panel");
        w->dock = DOMUI_DOCK_LEFT;
        w->w = 80;
        w->props.set("text", domui_value_string(domui_string("Tools")));
    }

    w = doc.find_by_id(top);
    if (w) {
        w->name.set("top_bar");
        w->dock = DOMUI_DOCK_TOP;
        w->h = 24;
        w->props.set("text", domui_value_string(domui_string("Toolbar")));
    }

    w = doc.find_by_id(fill);
    if (w) {
        w->name.set("content");
        w->dock = DOMUI_DOCK_FILL;
    }
}

static void build_fixture_tabs_split_scroll(domui_doc& doc)
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

    domui_set_defaults(doc, "fixture_tabs_split_scroll");
    root = doc.create_widget(DOMUI_WIDGET_CONTAINER, 0u);
    splitter = doc.create_widget(DOMUI_WIDGET_SPLITTER, root);
    pane_a = doc.create_widget(DOMUI_WIDGET_CONTAINER, splitter);
    pane_b = doc.create_widget(DOMUI_WIDGET_CONTAINER, splitter);

    w = doc.find_by_id(root);
    if (w) {
        w->name.set("root");
        w->w = 480;
        w->h = 240;
    }

    w = doc.find_by_id(splitter);
    if (w) {
        w->name.set("main_splitter");
        w->x = 0;
        w->y = 0;
        w->w = 480;
        w->h = 240;
        w->props.set("splitter.orientation", domui_value_string(domui_string("v")));
        w->props.set("splitter.pos", domui_value_int(160));
        w->props.set("splitter.thickness", domui_value_int(4));
        w->props.set("splitter.min_a", domui_value_int(60));
        w->props.set("splitter.min_b", domui_value_int(80));
    }

    tabs = doc.create_widget(DOMUI_WIDGET_TABS, pane_a);
    page_a = doc.create_widget(DOMUI_WIDGET_TAB_PAGE, tabs);
    page_b = doc.create_widget(DOMUI_WIDGET_TAB_PAGE, tabs);

    w = doc.find_by_id(tabs);
    if (w) {
        w->name.set("left_tabs");
        w->x = 0;
        w->y = 0;
        w->w = 200;
        w->h = 200;
        w->props.set("tabs.selected_index", domui_value_int(0));
        w->props.set("tabs.placement", domui_value_string(domui_string("top")));
    }
    w = doc.find_by_id(page_a);
    if (w) {
        w->name.set("page_a");
        w->props.set("tab.title", domui_value_string(domui_string("A")));
        w->props.set("tab.enabled", domui_value_bool(1));
    }
    w = doc.find_by_id(page_b);
    if (w) {
        w->name.set("page_b");
        w->props.set("tab.title", domui_value_string(domui_string("B")));
        w->props.set("tab.enabled", domui_value_bool(1));
    }

    scroll = doc.create_widget(DOMUI_WIDGET_SCROLLPANEL, pane_b);
    scroll_content = doc.create_widget(DOMUI_WIDGET_CONTAINER, scroll);

    w = doc.find_by_id(scroll);
    if (w) {
        w->name.set("right_scroll");
        w->x = 0;
        w->y = 0;
        w->w = 200;
        w->h = 200;
        w->props.set("scroll.h_enabled", domui_value_bool(1));
        w->props.set("scroll.v_enabled", domui_value_bool(1));
        w->props.set("scroll.x", domui_value_int(0));
        w->props.set("scroll.y", domui_value_int(0));
    }
    w = doc.find_by_id(scroll_content);
    if (w) {
        w->name.set("scroll_content");
        w->w = 320;
        w->h = 260;
    }
}

static void build_fixture_v1_migration(domui_doc& doc)
{
    domui_widget_id root;
    domui_widget_id splitter;
    domui_widget_id tabs;
    domui_widget_id page;
    domui_widget_id scroll;

    domui_set_defaults(doc, "fixture_migrate_v1");
    doc.meta.doc_version = 1u;
    root = doc.create_widget(DOMUI_WIDGET_CONTAINER, 0u);
    splitter = doc.create_widget(DOMUI_WIDGET_SPLITTER, root);
    tabs = doc.create_widget(DOMUI_WIDGET_TABS, root);
    page = doc.create_widget(DOMUI_WIDGET_TAB_PAGE, tabs);
    scroll = doc.create_widget(DOMUI_WIDGET_SCROLLPANEL, root);

    {
        domui_widget* w = doc.find_by_id(root);
        if (w) {
            w->name.set("root");
            w->w = 200;
            w->h = 120;
        }
        w = doc.find_by_id(splitter);
        if (w) {
            w->name.set("splitter");
        }
        w = doc.find_by_id(tabs);
        if (w) {
            w->name.set("tabs");
        }
        w = doc.find_by_id(page);
        if (w) {
            w->name.set("page");
        }
        w = doc.find_by_id(scroll);
        if (w) {
            w->name.set("scroll");
        }
    }
}

static bool domui_patch_doc_version(const char* path, domui_u32 version, domui_diag* diag)
{
    std::vector<unsigned char> bytes;
    dtlv_reader reader;
    const dtlv_dir_entry* meta_entry = 0;
    const unsigned char* meta_ptr = 0;
    u32 meta_len = 0u;
    u32 off = 0u;
    u32 tag = 0u;
    const unsigned char* payload = 0;
    u32 payload_len = 0u;

    if (!domui_read_file_bytes(path, bytes, diag)) {
        return false;
    }

    dtlv_reader_init(&reader);
    if (dtlv_reader_init_mem(&reader, &bytes[0], (u64)bytes.size()) != 0) {
        dtlv_reader_dispose(&reader);
        if (diag) {
            diag->add_error("fixture: invalid tlv container", 0u, path);
        }
        return false;
    }

    meta_entry = dtlv_reader_find_first(&reader, DOMUI_TAG('M','E','T','A'), 2u);
    if (!meta_entry) {
        meta_entry = dtlv_reader_find_first(&reader, DOMUI_TAG('M','E','T','A'), 1u);
    }
    if (!meta_entry) {
        dtlv_reader_dispose(&reader);
        if (diag) {
            diag->add_error("fixture: meta chunk missing", 0u, path);
        }
        return false;
    }

    if (dtlv_reader_chunk_memview(&reader, meta_entry, &meta_ptr, &meta_len) != 0) {
        dtlv_reader_dispose(&reader);
        if (diag) {
            diag->add_error("fixture: meta memview failed", 0u, path);
        }
        return false;
    }

    off = 0u;
    while (dtlv_tlv_next(meta_ptr, meta_len, &off, &tag, &payload, &payload_len) == 0) {
        if (tag == DOMUI_TLV_DOC_VERSION && payload_len >= 4u) {
            dtlv_le_write_u32((unsigned char*)payload, version);
            if (!domui_atomic_write_file(path, &bytes[0], bytes.size(), diag)) {
                dtlv_reader_dispose(&reader);
                return false;
            }
            dtlv_reader_dispose(&reader);
            return true;
        }
    }

    dtlv_reader_dispose(&reader);
    if (diag) {
        diag->add_error("fixture: doc_version tag missing", 0u, path);
    }
    return false;
}

static bool domui_write_fixture(const std::string& dir,
                                const char* base_name,
                                domui_doc& doc)
{
    std::string tlv_path = dir + "/" + base_name + ".tlv";
    domui_diag diag;
    if (!domui_doc_save_tlv(&doc, tlv_path.c_str(), &diag)) {
        domui_print_diag(diag);
        return false;
    }
    return true;
}

static bool domui_write_fixture_v1(const std::string& dir,
                                   const char* base_name,
                                   domui_doc& doc)
{
    const char* tmp_path = "ui_fixture_tmp_v1.tlv";
    const char* tmp_json = "ui_fixture_tmp_v1.json";
    std::string tlv_path = dir + "/" + base_name + ".tlv";
    domui_diag diag;

    if (!domui_doc_save_tlv(&doc, tmp_path, &diag)) {
        domui_print_diag(diag);
        return false;
    }
    if (!domui_patch_doc_version(tmp_path, 1u, &diag)) {
        domui_print_diag(diag);
        return false;
    }
    {
        std::vector<unsigned char> bytes;
        if (!domui_read_file_bytes(tmp_path, bytes, &diag)) {
            domui_print_diag(diag);
            return false;
        }
        if (!domui_atomic_write_file(tlv_path.c_str(), &bytes[0], bytes.size(), &diag)) {
            domui_print_diag(diag);
            return false;
        }
    }
    std::remove(tmp_path);
    std::remove(tmp_json);
    return true;
}

int main(int argc, char** argv)
{
    std::string root;
    std::string fixtures_dir;
    domui_doc doc;

    (void)argc;
    (void)argv;

    if (!domui_find_repo_root(root)) {
        std::fprintf(stderr, "fixture gen: unable to locate repo root\n");
        return 1;
    }
    fixtures_dir = root + "/docs/ui_editor/fixtures";

    build_fixture_abs(doc);
    if (!domui_write_fixture(fixtures_dir, "fixture_abs", doc)) {
        return 1;
    }
    build_fixture_dock(doc);
    if (!domui_write_fixture(fixtures_dir, "fixture_dock", doc)) {
        return 1;
    }
    build_fixture_tabs_split_scroll(doc);
    if (!domui_write_fixture(fixtures_dir, "fixture_tabs_split_scroll", doc)) {
        return 1;
    }
    build_fixture_v1_migration(doc);
    if (!domui_write_fixture_v1(fixtures_dir, "fixture_migrate_v1", doc)) {
        return 1;
    }

    std::printf("fixtures written to %s\n", fixtures_dir.c_str());
    return 0;
}
