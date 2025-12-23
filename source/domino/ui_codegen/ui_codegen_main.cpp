/*
FILE: source/domino/ui_codegen/ui_codegen_main.cpp
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / ui_codegen cli
RESPONSIBILITY: CLI wrapper for deterministic UI action codegen.
*/
#include "ui_codegen.h"

#include <cstdio>
#include <cstring>

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

static void domui_print_usage(void)
{
    std::fprintf(stderr, "usage: domui_codegen --input <ui_doc.tlv> --registry <registry.json> --out-gen <dir> --out-user <dir> [--doc-name <name>]\n");
}

int main(int argc, char** argv)
{
    domui_codegen_params params;
    domui_diag diag;
    int i;

    for (i = 1; i < argc; ++i) {
        const char* arg = argv[i];
        if (!arg) {
            continue;
        }
        if (std::strcmp(arg, "--input") == 0 && i + 1 < argc) {
            params.input_tlv_path = argv[++i];
        } else if (std::strcmp(arg, "--registry") == 0 && i + 1 < argc) {
            params.registry_path = argv[++i];
        } else if (std::strcmp(arg, "--out-gen") == 0 && i + 1 < argc) {
            params.out_gen_dir = argv[++i];
        } else if (std::strcmp(arg, "--out-user") == 0 && i + 1 < argc) {
            params.out_user_dir = argv[++i];
        } else if (std::strcmp(arg, "--doc-name") == 0 && i + 1 < argc) {
            params.doc_name_override = argv[++i];
        } else {
            domui_print_usage();
            return 2;
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
    domui_print_diag(diag);
    return 0;
}
