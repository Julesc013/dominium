/*
FILE: tools/ui_preview_host/common/ui_preview_common.h
MODULE: Dominium tools
RESPONSIBILITY: Shared helpers for UI preview hosts (doc loading, schema/state build, logging).
*/
#ifndef DOMINIUM_UI_PREVIEW_COMMON_H_INCLUDED
#define DOMINIUM_UI_PREVIEW_COMMON_H_INCLUDED

#include <map>
#include <stdio.h>
#include <string>
#include <vector>

#include "dui/domui_event.h"
#include "dui/dui_schema_tlv.h"

#include "ui_caps.h"
#include "ui_ir_diag.h"
#include "ui_ir_doc.h"
#include "ui_ir_props.h"
#include "ui_ir_string.h"
#include "ui_layout.h"
#include "ui_validate.h"

struct UiPreviewLog {
    UiPreviewLog();
    ~UiPreviewLog();

    bool open_file(const std::string& path);
    void close_file();
    void line(const std::string& text);

    FILE* file;
};

struct UiPreviewActionRegistry {
    UiPreviewActionRegistry();

    void clear();
    domui_action_id lookup_or_fallback(const std::string& key);
    const char* key_from_id(domui_action_id id) const;

    std::map<std::string, domui_action_id> key_to_id;
    std::map<domui_action_id, std::string> id_to_key;
    int loaded;
};

struct UiPreviewTargets {
    domui_target_set targets;
    std::vector<std::string> tokens;
};

struct UiPreviewDoc {
    domui_doc doc;
    domui_widget_id root_id;
    std::map<domui_widget_id, domui_layout_rect> layout;
    std::vector<domui_layout_result> layout_results;
    std::vector<unsigned char> schema;
    std::vector<unsigned char> state;
};

struct UiPreviewActionContext {
    UiPreviewLog* log;
    UiPreviewActionRegistry* registry;
};

bool ui_preview_parse_targets(const char* list, UiPreviewTargets& out_targets, std::string& out_err);
bool ui_preview_load_action_registry(const std::string& path, UiPreviewActionRegistry& out_registry, std::string& out_err);
std::string ui_preview_guess_registry_path(const std::string& ui_doc_path);
void ui_preview_collect_watch_dirs(const std::string& ui_doc_path,
                                   const std::string& registry_path,
                                   std::vector<std::string>& out_dirs);

bool ui_preview_file_exists(const std::string& path);
bool ui_preview_is_dir(const std::string& path);
std::string ui_preview_dirname(const std::string& path);
std::string ui_preview_basename(const std::string& path);
std::string ui_preview_basename_no_ext(const std::string& path);
std::string ui_preview_join(const std::string& a, const std::string& b);
std::string ui_preview_to_lower(const std::string& in);

bool ui_preview_load_doc(const char* path, UiPreviewDoc& out_doc, UiPreviewLog& log, domui_diag* out_diag);
bool ui_preview_build_layout(UiPreviewDoc& doc, int width, int height, domui_diag* out_diag);
bool ui_preview_build_schema(UiPreviewDoc& doc, UiPreviewActionRegistry& actions);
bool ui_preview_build_state(UiPreviewDoc& doc);
bool ui_preview_validate_doc(const UiPreviewDoc& doc, const UiPreviewTargets& targets, domui_diag* out_diag);
void ui_preview_log_diag(UiPreviewLog& log, const domui_diag& diag);

void ui_preview_action_dispatch(void* user_ctx, const domui_event* e);

#endif /* DOMINIUM_UI_PREVIEW_COMMON_H_INCLUDED */
