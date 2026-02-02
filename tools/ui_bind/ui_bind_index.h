/*
FILE: tools/ui_bind/ui_bind_index.h
MODULE: Dominium
PURPOSE: Minimal UI index loader for UI binding tools (JSON entries list).
NOTES: Deterministic; strict string parsing only.
*/
#ifndef DOMINIUM_UI_BIND_INDEX_H
#define DOMINIUM_UI_BIND_INDEX_H

#include <string>
#include <vector>

struct ui_bind_index_entry {
    std::string ui_type;
    std::string path;
    std::string tool;
};

bool ui_bind_load_index(const char* path,
                        std::vector<ui_bind_index_entry>& out_entries,
                        std::string* out_error);

#endif /* DOMINIUM_UI_BIND_INDEX_H */
