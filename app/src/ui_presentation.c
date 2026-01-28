/*
UI presentation helpers: accessibility presets and localization tables.
*/
#include "dominium/app/ui_presentation.h"

#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define DOM_UI_LOCALE_MAGIC "DOMINIUM_L10N_V1"
#define DOM_UI_ACCESS_MAGIC "DOMINIUM_ACCESSIBILITY_V1"

static void dom_ui_trim(char* text)
{
    char* end;
    char* p;
    if (!text || !text[0]) {
        return;
    }
    p = text;
    while (*p && isspace((unsigned char)*p)) {
        ++p;
    }
    if (p != text) {
        memmove(text, p, strlen(p) + 1u);
    }
    end = text + strlen(text);
    while (end > text && isspace((unsigned char)end[-1])) {
        --end;
    }
    *end = '\0';
}

static int dom_ui_is_comment(const char* text)
{
    if (!text || !text[0]) {
        return 1;
    }
    if (text[0] == '#') {
        return 1;
    }
    if (text[0] == ';') {
        return 1;
    }
    if (text[0] == '/' && text[1] == '/') {
        return 1;
    }
    return 0;
}

static char* dom_ui_strdup(const char* text)
{
    size_t len;
    char* out;
    if (!text) {
        return NULL;
    }
    len = strlen(text);
    out = (char*)malloc(len + 1u);
    if (!out) {
        return NULL;
    }
    memcpy(out, text, len + 1u);
    return out;
}

static int dom_ui_parse_bool(const char* text, int* out_value)
{
    if (!text || !out_value) {
        return 0;
    }
    if (strcmp(text, "1") == 0 || strcmp(text, "true") == 0 || strcmp(text, "yes") == 0) {
        *out_value = 1;
        return 1;
    }
    if (strcmp(text, "0") == 0 || strcmp(text, "false") == 0 || strcmp(text, "no") == 0) {
        *out_value = 0;
        return 1;
    }
    return 0;
}

static void dom_ui_unescape(char* text)
{
    char* src;
    char* dst;
    if (!text) {
        return;
    }
    src = text;
    dst = text;
    while (*src) {
        if (src[0] == '\\' && src[1]) {
            char c = src[1];
            if (c == 'n') {
                *dst++ = '\n';
                src += 2;
                continue;
            }
            if (c == 't') {
                *dst++ = '\t';
                src += 2;
                continue;
            }
            if (c == '\\') {
                *dst++ = '\\';
                src += 2;
                continue;
            }
        }
        *dst++ = *src++;
    }
    *dst = '\0';
}

static int dom_ui_split_kv(char* line, char** out_key, char** out_value)
{
    char* eq;
    if (!line || !out_key || !out_value) {
        return 0;
    }
    eq = strchr(line, '=');
    if (!eq) {
        return 0;
    }
    *eq = '\0';
    *out_key = line;
    *out_value = eq + 1;
    dom_ui_trim(*out_key);
    dom_ui_trim(*out_value);
    return (*out_key)[0] != '\0';
}

void dom_app_ui_locale_table_init(dom_app_ui_locale_table* table)
{
    if (!table) {
        return;
    }
    table->entries = NULL;
    table->count = 0u;
    table->capacity = 0u;
}

void dom_app_ui_locale_table_free(dom_app_ui_locale_table* table)
{
    size_t i;
    if (!table) {
        return;
    }
    for (i = 0; i < table->count; ++i) {
        free(table->entries[i].id);
        free(table->entries[i].text);
    }
    free(table->entries);
    table->entries = NULL;
    table->count = 0u;
    table->capacity = 0u;
}

static int dom_ui_locale_set(dom_app_ui_locale_table* table, const char* id, const char* text)
{
    size_t i;
    if (!table || !id || !id[0] || !text) {
        return 0;
    }
    for (i = 0; i < table->count; ++i) {
        if (strcmp(table->entries[i].id, id) == 0) {
            char* dup = dom_ui_strdup(text);
            if (!dup) {
                return 0;
            }
            free(table->entries[i].text);
            table->entries[i].text = dup;
            return 1;
        }
    }
    if (table->count >= table->capacity) {
        size_t next = table->capacity ? (table->capacity * 2u) : 16u;
        dom_app_ui_locale_entry* grow = (dom_app_ui_locale_entry*)realloc(table->entries,
                                                                          next * sizeof(dom_app_ui_locale_entry));
        if (!grow) {
            return 0;
        }
        table->entries = grow;
        table->capacity = next;
    }
    table->entries[table->count].id = dom_ui_strdup(id);
    table->entries[table->count].text = dom_ui_strdup(text);
    if (!table->entries[table->count].id || !table->entries[table->count].text) {
        free(table->entries[table->count].id);
        free(table->entries[table->count].text);
        return 0;
    }
    table->count += 1u;
    return 1;
}

int dom_app_ui_locale_table_load_file(dom_app_ui_locale_table* table,
                                      const char* path,
                                      char* err,
                                      size_t err_cap)
{
    FILE* handle;
    char line[2048];
    int saw_magic = 0;
    unsigned int line_no = 0u;
    if (err && err_cap > 0u) {
        err[0] = '\0';
    }
    if (!table || !path || !path[0]) {
        if (err && err_cap > 0u) {
            snprintf(err, err_cap, "locale path missing");
        }
        return 0;
    }
    handle = fopen(path, "rb");
    if (!handle) {
        if (err && err_cap > 0u) {
            snprintf(err, err_cap, "locale open failed");
        }
        return 0;
    }
    while (fgets(line, (int)sizeof(line), handle)) {
        char* key = NULL;
        char* value = NULL;
        ++line_no;
        dom_ui_trim(line);
        if (!line[0] || dom_ui_is_comment(line)) {
            continue;
        }
        if (!saw_magic) {
            if (strcmp(line, DOM_UI_LOCALE_MAGIC) != 0) {
                if (err && err_cap > 0u) {
                    snprintf(err, err_cap, "locale missing magic");
                }
                fclose(handle);
                return 0;
            }
            saw_magic = 1;
            continue;
        }
        if (!dom_ui_split_kv(line, &key, &value)) {
            if (err && err_cap > 0u) {
                snprintf(err, err_cap, "invalid locale line %u", line_no);
            }
            fclose(handle);
            return 0;
        }
        if (!key[0]) {
            continue;
        }
        dom_ui_unescape(value);
        if (!dom_ui_locale_set(table, key, value)) {
            if (err && err_cap > 0u) {
                snprintf(err, err_cap, "locale insert failed");
            }
            fclose(handle);
            return 0;
        }
    }
    fclose(handle);
    if (!saw_magic) {
        if (err && err_cap > 0u) {
            snprintf(err, err_cap, "locale missing magic");
        }
        return 0;
    }
    return 1;
}

int dom_app_ui_locale_table_load_pack(dom_app_ui_locale_table* table,
                                      const char* pack_root,
                                      const char* locale_id,
                                      char* err,
                                      size_t err_cap)
{
    char path[512];
    size_t len;
    if (!table || !pack_root || !pack_root[0] || !locale_id || !locale_id[0]) {
        if (err && err_cap > 0u) {
            snprintf(err, err_cap, "locale pack path missing");
        }
        return 0;
    }
    len = strlen(pack_root);
    if (len >= sizeof(path) - 64u) {
        if (err && err_cap > 0u) {
            snprintf(err, err_cap, "locale pack path too long");
        }
        return 0;
    }
    snprintf(path, sizeof(path), "%s/data/locale/%s.l10n", pack_root, locale_id);
    return dom_app_ui_locale_table_load_file(table, path, err, err_cap);
}

const char* dom_app_ui_locale_text(const dom_app_ui_locale_table* table,
                                   const char* id,
                                   const char* fallback)
{
    size_t i;
    if (!id || !id[0]) {
        return fallback ? fallback : "";
    }
    if (!table) {
        return fallback ? fallback : id;
    }
    for (i = 0; i < table->count; ++i) {
        if (strcmp(table->entries[i].id, id) == 0) {
            return table->entries[i].text ? table->entries[i].text : fallback;
        }
    }
    return fallback ? fallback : id;
}

void dom_app_ui_accessibility_preset_init(dom_app_ui_accessibility_preset* preset)
{
    if (!preset) {
        return;
    }
    memset(preset, 0, sizeof(*preset));
    preset->preset_id[0] = '\0';
    preset->preset_version[0] = '\0';
    preset->ui_density[0] = '\0';
    preset->verbosity[0] = '\0';
    preset->keybind_profile_id[0] = '\0';
    preset->has_ui_scale = 0;
    preset->ui_scale_percent = 0;
    preset->has_palette = 0;
    preset->palette = 0;
    preset->has_log_level = 0;
    preset->log_level = 0;
    preset->reduced_motion = 0;
    preset->keyboard_only = 0;
    preset->screen_reader = 0;
    preset->low_cognitive_load = 0;
}

int dom_app_ui_accessibility_load_file(dom_app_ui_accessibility_preset* preset,
                                       const char* path,
                                       char* err,
                                       size_t err_cap)
{
    FILE* handle;
    char line[2048];
    int saw_magic = 0;
    unsigned int line_no = 0u;
    if (err && err_cap > 0u) {
        err[0] = '\0';
    }
    if (!preset || !path || !path[0]) {
        if (err && err_cap > 0u) {
            snprintf(err, err_cap, "accessibility path missing");
        }
        return 0;
    }
    handle = fopen(path, "rb");
    if (!handle) {
        if (err && err_cap > 0u) {
            snprintf(err, err_cap, "accessibility open failed");
        }
        return 0;
    }
    while (fgets(line, (int)sizeof(line), handle)) {
        char* key = NULL;
        char* value = NULL;
        ++line_no;
        dom_ui_trim(line);
        if (!line[0] || dom_ui_is_comment(line)) {
            continue;
        }
        if (!saw_magic) {
            if (strcmp(line, DOM_UI_ACCESS_MAGIC) != 0) {
                if (err && err_cap > 0u) {
                    snprintf(err, err_cap, "accessibility missing magic");
                }
                fclose(handle);
                return 0;
            }
            saw_magic = 1;
            continue;
        }
        if (!dom_ui_split_kv(line, &key, &value)) {
            if (err && err_cap > 0u) {
                snprintf(err, err_cap, "invalid accessibility line %u", line_no);
            }
            fclose(handle);
            return 0;
        }
        if (strcmp(key, "preset_id") == 0) {
            strncpy(preset->preset_id, value, sizeof(preset->preset_id) - 1u);
            preset->preset_id[sizeof(preset->preset_id) - 1u] = '\0';
            continue;
        }
        if (strcmp(key, "preset_version") == 0) {
            strncpy(preset->preset_version, value, sizeof(preset->preset_version) - 1u);
            preset->preset_version[sizeof(preset->preset_version) - 1u] = '\0';
            continue;
        }
        if (strcmp(key, "ui_density") == 0) {
            strncpy(preset->ui_density, value, sizeof(preset->ui_density) - 1u);
            preset->ui_density[sizeof(preset->ui_density) - 1u] = '\0';
            continue;
        }
        if (strcmp(key, "verbosity") == 0) {
            strncpy(preset->verbosity, value, sizeof(preset->verbosity) - 1u);
            preset->verbosity[sizeof(preset->verbosity) - 1u] = '\0';
            continue;
        }
        if (strcmp(key, "keybind_profile_id") == 0) {
            strncpy(preset->keybind_profile_id, value, sizeof(preset->keybind_profile_id) - 1u);
            preset->keybind_profile_id[sizeof(preset->keybind_profile_id) - 1u] = '\0';
            continue;
        }
        if (strcmp(key, "ui_scale_percent") == 0) {
            long val = strtol(value, NULL, 10);
            if (val < 50 || val > 200) {
                if (err && err_cap > 0u) {
                    snprintf(err, err_cap, "ui_scale_percent out of range");
                }
                fclose(handle);
                return 0;
            }
            preset->ui_scale_percent = (int)val;
            preset->has_ui_scale = 1;
            continue;
        }
        if (strcmp(key, "palette") == 0) {
            if (strcmp(value, "default") == 0) {
                preset->palette = 0;
                preset->has_palette = 1;
                continue;
            }
            if (strcmp(value, "high-contrast") == 0 || strcmp(value, "high_contrast") == 0) {
                preset->palette = 1;
                preset->has_palette = 1;
                continue;
            }
            if (err && err_cap > 0u) {
                snprintf(err, err_cap, "invalid palette");
            }
            fclose(handle);
            return 0;
        }
        if (strcmp(key, "log_level") == 0) {
            if (strcmp(value, "info") == 0) {
                preset->log_level = 0;
                preset->has_log_level = 1;
                continue;
            }
            if (strcmp(value, "warn") == 0 || strcmp(value, "warning") == 0) {
                preset->log_level = 1;
                preset->has_log_level = 1;
                continue;
            }
            if (strcmp(value, "error") == 0) {
                preset->log_level = 2;
                preset->has_log_level = 1;
                continue;
            }
            if (err && err_cap > 0u) {
                snprintf(err, err_cap, "invalid log_level");
            }
            fclose(handle);
            return 0;
        }
        if (strcmp(key, "reduced_motion") == 0) {
            if (!dom_ui_parse_bool(value, &preset->reduced_motion)) {
                if (err && err_cap > 0u) {
                    snprintf(err, err_cap, "invalid reduced_motion");
                }
                fclose(handle);
                return 0;
            }
            continue;
        }
        if (strcmp(key, "keyboard_only") == 0) {
            if (!dom_ui_parse_bool(value, &preset->keyboard_only)) {
                if (err && err_cap > 0u) {
                    snprintf(err, err_cap, "invalid keyboard_only");
                }
                fclose(handle);
                return 0;
            }
            continue;
        }
        if (strcmp(key, "screen_reader") == 0) {
            if (!dom_ui_parse_bool(value, &preset->screen_reader)) {
                if (err && err_cap > 0u) {
                    snprintf(err, err_cap, "invalid screen_reader");
                }
                fclose(handle);
                return 0;
            }
            continue;
        }
        if (strcmp(key, "low_cognitive_load") == 0) {
            if (!dom_ui_parse_bool(value, &preset->low_cognitive_load)) {
                if (err && err_cap > 0u) {
                    snprintf(err, err_cap, "invalid low_cognitive_load");
                }
                fclose(handle);
                return 0;
            }
            continue;
        }
    }
    fclose(handle);
    if (!saw_magic) {
        if (err && err_cap > 0u) {
            snprintf(err, err_cap, "accessibility missing magic");
        }
        return 0;
    }
    return 1;
}
