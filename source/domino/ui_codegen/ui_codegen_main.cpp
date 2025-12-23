/*
FILE: source/domino/ui_codegen/ui_codegen_main.cpp
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / ui_codegen cli
RESPONSIBILITY: CLI wrapper for deterministic UI action codegen.
*/
#include "ui_codegen.h"

#include <algorithm>
#include <cctype>
#include <cstdio>
#include <cstring>
#include <string>
#include <vector>

#include "ui_ir_doc.h"
#include "ui_ir_tlv.h"

static void domui_print_diag(const domui_diag& diag)
{
    size_t i;
    for (i = 0u; i < diag.errors().size(); ++i) {
        const domui_diag_item& item = diag.errors()[i];
        std::fprintf(stderr, "error: %s\n", item.message.c_str());
    }
    for (i = 0u; i < diag.warnings().size(); ++i) {
        const domui_diag_item& item = diag.warnings()[i];
        std::fprintf(stderr, "warning: %s\n", item.message.c_str());
    }
}

static std::string domui_join_path(const std::string& a, const std::string& b)
{
    if (a.empty()) {
        return b;
    }
    if (b.empty()) {
        return a;
    }
    if (a[a.size() - 1u] == '/' || a[a.size() - 1u] == '\\') {
        return a + b;
    }
    return a + "/" + b;
}

static std::string domui_sanitize_doc_name(const std::string& in)
{
    std::string out;
    size_t i;
    out.reserve(in.size() + 8u);
    for (i = 0u; i < in.size(); ++i) {
        unsigned char c = (unsigned char)in[i];
        if (std::isalnum(c)) {
            out.push_back((char)std::tolower(c));
        } else {
            out.push_back('_');
        }
    }
    if (out.empty()) {
        out = "doc";
    }
    if (out[0] >= '0' && out[0] <= '9') {
        out.insert(0u, "ui_");
    }
    return out;
}

static void domui_collect_action_keys(const domui_doc& doc, std::vector<std::string>& out_keys)
{
    std::vector<domui_widget_id> order;
    size_t i;
    out_keys.clear();
    doc.canonical_widget_order(order);
    for (i = 0u; i < order.size(); ++i) {
        const domui_widget* w = doc.find_by_id(order[i]);
        if (!w) {
            continue;
        }
        const domui_events::list_type& entries = w->events.entries();
        for (size_t e = 0u; e < entries.size(); ++e) {
            const std::string& key = entries[e].action_key.str();
            if (!key.empty()) {
                out_keys.push_back(key);
            }
        }
    }
    std::sort(out_keys.begin(), out_keys.end());
    out_keys.erase(std::unique(out_keys.begin(), out_keys.end()), out_keys.end());
}

static void domui_print_summary(const domui_codegen_params& params, const domui_doc& doc)
{
    std::vector<std::string> keys;
    std::string doc_name;
    std::string doc_sym;
    std::string gen_header;
    std::string gen_cpp;
    std::string user_header;
    std::string user_cpp;

    if (params.doc_name_override && params.doc_name_override[0]) {
        doc_name = params.doc_name_override;
    } else {
        doc_name = doc.meta.doc_name.str();
    }
    doc_sym = "ui_" + domui_sanitize_doc_name(doc_name);

    domui_collect_action_keys(doc, keys);

    gen_header = domui_join_path(params.out_gen_dir ? params.out_gen_dir : "", doc_sym + "_actions_gen.h");
    gen_cpp = domui_join_path(params.out_gen_dir ? params.out_gen_dir : "", doc_sym + "_actions_gen.cpp");
    user_header = domui_join_path(params.out_user_dir ? params.out_user_dir : "", doc_sym + "_actions_user.h");
    user_cpp = domui_join_path(params.out_user_dir ? params.out_user_dir : "", doc_sym + "_actions_user.cpp");

    std::printf("doc: %s\n", params.input_tlv_path ? params.input_tlv_path : "");
    std::printf("registry: %s\n", params.registry_path ? params.registry_path : "");
    std::printf("actions: %u\n", (unsigned int)keys.size());
    std::printf("out_gen_dir: %s\n", params.out_gen_dir ? params.out_gen_dir : "");
    std::printf("out_user_dir: %s\n", params.out_user_dir ? params.out_user_dir : "");
    std::printf("out_gen_h: %s\n", gen_header.c_str());
    std::printf("out_gen_cpp: %s\n", gen_cpp.c_str());
    std::printf("out_user_h: %s\n", user_header.c_str());
    std::printf("out_user_cpp: %s\n", user_cpp.c_str());
}

static void domui_print_usage(void)
{
    std::fprintf(stderr,
                 "usage: domui_codegen --in <ui_doc.tlv> --out <dir> --registry <registry.json> [--docname <name>]\n"
                 "       domui_codegen --input <ui_doc.tlv> --registry <registry.json> --out-gen <dir> --out-user <dir> [--doc-name <name>]\n");
}

int main(int argc, char** argv)
{
    domui_codegen_params params;
    domui_diag diag;
    std::string out_base;
    std::string out_gen_storage;
    std::string out_user_storage;
    domui_doc doc;
    domui_diag summary_diag;
    int i;

    for (i = 1; i < argc; ++i) {
        const char* arg = argv[i];
        if (!arg) {
            continue;
        }
        if ((std::strcmp(arg, "--input") == 0 || std::strcmp(arg, "--in") == 0) && i + 1 < argc) {
            params.input_tlv_path = argv[++i];
        } else if (std::strcmp(arg, "--registry") == 0 && i + 1 < argc) {
            params.registry_path = argv[++i];
        } else if (std::strcmp(arg, "--out-gen") == 0 && i + 1 < argc) {
            params.out_gen_dir = argv[++i];
        } else if (std::strcmp(arg, "--out-user") == 0 && i + 1 < argc) {
            params.out_user_dir = argv[++i];
        } else if (std::strcmp(arg, "--out") == 0 && i + 1 < argc) {
            out_base = argv[++i];
        } else if ((std::strcmp(arg, "--doc-name") == 0 || std::strcmp(arg, "--docname") == 0) && i + 1 < argc) {
            params.doc_name_override = argv[++i];
        } else {
            domui_print_usage();
            return 2;
        }
    }

    if (!out_base.empty()) {
        if (!params.out_gen_dir) {
            out_gen_storage = domui_join_path(out_base, "gen");
            params.out_gen_dir = out_gen_storage.c_str();
        }
        if (!params.out_user_dir) {
            out_user_storage = domui_join_path(out_base, "user");
            params.out_user_dir = out_user_storage.c_str();
        }
    }

    if (!params.input_tlv_path || !params.registry_path ||
        !params.out_gen_dir || !params.out_user_dir) {
        domui_print_usage();
        return 2;
    }

    if (!domui_codegen_run(&params, &diag)) {
        domui_print_diag(diag);
        return 1;
    }
    if (domui_doc_load_tlv(&doc, params.input_tlv_path, &summary_diag)) {
        domui_print_summary(params, doc);
    }
    domui_print_diag(diag);
    return 0;
}
