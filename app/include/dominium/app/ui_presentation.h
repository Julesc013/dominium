/*
UI presentation helpers: accessibility presets and localization tables.
*/
#ifndef DOMINIUM_APP_UI_PRESENTATION_H
#define DOMINIUM_APP_UI_PRESENTATION_H

#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dom_app_ui_locale_entry {
    char* id;
    char* text;
} dom_app_ui_locale_entry;

typedef struct dom_app_ui_locale_table {
    dom_app_ui_locale_entry* entries;
    size_t count;
    size_t capacity;
} dom_app_ui_locale_table;

void dom_app_ui_locale_table_init(dom_app_ui_locale_table* table);
void dom_app_ui_locale_table_free(dom_app_ui_locale_table* table);
int dom_app_ui_locale_table_load_file(dom_app_ui_locale_table* table,
                                      const char* path,
                                      char* err,
                                      size_t err_cap);
int dom_app_ui_locale_table_load_pack(dom_app_ui_locale_table* table,
                                      const char* pack_root,
                                      const char* locale_id,
                                      char* err,
                                      size_t err_cap);
const char* dom_app_ui_locale_text(const dom_app_ui_locale_table* table,
                                   const char* id,
                                   const char* fallback);

typedef struct dom_app_ui_accessibility_preset {
    char preset_id[64];
    char preset_version[32];
    char ui_density[24];
    char verbosity[24];
    char keybind_profile_id[64];
    int has_ui_scale;
    int ui_scale_percent;
    int has_palette;
    int palette;
    int has_log_level;
    int log_level;
    int reduced_motion;
    int keyboard_only;
    int screen_reader;
    int low_cognitive_load;
} dom_app_ui_accessibility_preset;

void dom_app_ui_accessibility_preset_init(dom_app_ui_accessibility_preset* preset);
int dom_app_ui_accessibility_load_file(dom_app_ui_accessibility_preset* preset,
                                       const char* path,
                                       char* err,
                                       size_t err_cap);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_APP_UI_PRESENTATION_H */
