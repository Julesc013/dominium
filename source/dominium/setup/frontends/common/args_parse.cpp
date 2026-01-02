#include "args_parse.h"

#include <cctype>
#include <cstdlib>
#include <cstring>

void dsk_args_view_init(dsk_args_view_t *view, int argc, char **argv, int start) {
    if (!view) {
        return;
    }
    view->argc = argc;
    view->argv = argv;
    view->start = start;
}

const char *dsk_args_get_value(const dsk_args_view_t *view, const char *name) {
    int i;
    if (!view || !name) {
        return 0;
    }
    for (i = view->start; i < view->argc - 1; ++i) {
        if (view->argv[i] && std::strcmp(view->argv[i], name) == 0) {
            return view->argv[i + 1];
        }
    }
    return 0;
}

dsk_bool dsk_args_has_flag(const dsk_args_view_t *view, const char *name) {
    int i;
    if (!view || !name) {
        return DSK_FALSE;
    }
    for (i = view->start; i < view->argc; ++i) {
        if (view->argv[i] && std::strcmp(view->argv[i], name) == 0) {
            return DSK_TRUE;
        }
    }
    return DSK_FALSE;
}

dsk_bool dsk_args_parse_bool(const char *value, dsk_bool *out_value) {
    if (!out_value) {
        return DSK_FALSE;
    }
    if (!value) {
        *out_value = DSK_FALSE;
        return DSK_FALSE;
    }
    if (std::strcmp(value, "1") == 0 || std::strcmp(value, "true") == 0) {
        *out_value = DSK_TRUE;
        return DSK_TRUE;
    }
    if (std::strcmp(value, "0") == 0 || std::strcmp(value, "false") == 0) {
        *out_value = DSK_FALSE;
        return DSK_TRUE;
    }
    return DSK_FALSE;
}

dsk_bool dsk_args_parse_u32(const char *value, dsk_u32 *out_value) {
    const char *p;
    dsk_u32 result = 0u;
    if (!out_value || !value || !value[0]) {
        return DSK_FALSE;
    }
    p = value;
    while (*p) {
        char c = *p++;
        if (c < '0' || c > '9') {
            return DSK_FALSE;
        }
        result = (result * 10u) + (dsk_u32)(c - '0');
    }
    *out_value = result;
    return DSK_TRUE;
}

std::string dsk_args_trim_copy(const std::string &value) {
    size_t start = 0u;
    size_t end = value.size();
    while (start < end && (value[start] == ' ' || value[start] == '\t')) {
        ++start;
    }
    while (end > start && (value[end - 1u] == ' ' || value[end - 1u] == '\t')) {
        --end;
    }
    return value.substr(start, end - start);
}

void dsk_args_split_csv(const char *value, std::vector<std::string> *out_values) {
    std::string input = value ? value : "";
    size_t start = 0u;
    size_t i;
    if (!out_values) {
        return;
    }
    out_values->clear();
    for (i = 0u; i <= input.size(); ++i) {
        if (i == input.size() || input[i] == ',') {
            std::string token = input.substr(start, i - start);
            token = dsk_args_trim_copy(token);
            if (!token.empty()) {
                out_values->push_back(token);
            }
            start = i + 1u;
        }
    }
}
