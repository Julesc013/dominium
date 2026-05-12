#ifndef DSK_FRONTEND_ARGS_PARSE_H
#define DSK_FRONTEND_ARGS_PARSE_H

#include "dsk/dsk_types.h"

#include <string>
#include <vector>

struct dsk_args_view_t {
    int argc;
    char **argv;
    int start;
};

void dsk_args_view_init(dsk_args_view_t *view, int argc, char **argv, int start);
const char *dsk_args_get_value(const dsk_args_view_t *view, const char *name);
dsk_bool dsk_args_has_flag(const dsk_args_view_t *view, const char *name);
dsk_bool dsk_args_parse_bool(const char *value, dsk_bool *out_value);
dsk_bool dsk_args_parse_u32(const char *value, dsk_u32 *out_value);
void dsk_args_split_csv(const char *value, std::vector<std::string> *out_values);
std::string dsk_args_trim_copy(const std::string &value);

#endif
