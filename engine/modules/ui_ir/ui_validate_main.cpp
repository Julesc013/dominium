/*
FILE: source/domino/ui_ir/ui_validate_main.cpp
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / ui_ir validate cli
RESPONSIBILITY: Headless validator CLI for UI IR documents.
*/
#include "ui_validate.h"

#include <cstdio>
#include <cstring>

#include "ui_ir_tlv.h"

static void domui_print_usage(void)
{
    std::fprintf(stderr, "usage: domui_validate --input <ui_doc.tlv> [--backend <id>] [--tier <id>]\n");
}

static void domui_print_diag(const domui_diag& diag)
{
    size_t i;
    for (i = 0u; i < diag.errors().size(); ++i) {
        const domui_diag_item& item = diag.errors()[i];
        std::printf("ERROR|%u|%s|%s\n",
                    (unsigned int)item.widget_id,
                    item.context.c_str(),
                    item.message.c_str());
    }
    for (i = 0u; i < diag.warnings().size(); ++i) {
        const domui_diag_item& item = diag.warnings()[i];
        std::printf("WARN|%u|%s|%s\n",
                    (unsigned int)item.widget_id,
                    item.context.c_str(),
                    item.message.c_str());
    }
}

int main(int argc, char** argv)
{
    const char* input_path = 0;
    domui_target_set targets;
    domui_doc doc;
    domui_diag diag;
    int i;

    for (i = 1; i < argc; ++i) {
        const char* arg = argv[i];
        if (!arg) {
            continue;
        }
        if ((std::strcmp(arg, "--input") == 0 || std::strcmp(arg, "--in") == 0) && i + 1 < argc) {
            input_path = argv[++i];
        } else if (std::strcmp(arg, "--backend") == 0 && i + 1 < argc) {
            targets.backends.push_back(domui_string(argv[++i]));
        } else if (std::strcmp(arg, "--tier") == 0 && i + 1 < argc) {
            targets.tiers.push_back(domui_string(argv[++i]));
        } else if (std::strcmp(arg, "--help") == 0 || std::strcmp(arg, "-h") == 0) {
            domui_print_usage();
            return 0;
        } else {
            domui_print_usage();
            return 2;
        }
    }

    if (!input_path) {
        domui_print_usage();
        return 2;
    }

    if (!domui_doc_load_tlv(&doc, input_path, &diag)) {
        domui_print_diag(diag);
        return 1;
    }

    if (!domui_validate_doc(&doc, (targets.backends.empty() && targets.tiers.empty()) ? 0 : &targets, &diag)) {
        domui_print_diag(diag);
        return 1;
    }

    domui_print_diag(diag);
    return 0;
}
