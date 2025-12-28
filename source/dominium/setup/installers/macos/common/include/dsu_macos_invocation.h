#ifndef DSU_MACOS_INVOCATION_H_INCLUDED
#define DSU_MACOS_INVOCATION_H_INCLUDED

#include "dsu_macos_args.h"

#include "dsu/dsu_invocation.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dsu_macos_csv_list_t {
    char **items;
    unsigned long count;
} dsu_macos_csv_list_t;

void dsu_macos_csv_list_free(dsu_macos_csv_list_t *list);
int dsu_macos_csv_list_parse(const char *csv, dsu_macos_csv_list_t *out_list);

int dsu_macos_build_invocation(const dsu_macos_cli_args_t *args,
                               const char *platform_default,
                               const char *ui_mode_default,
                               const char *frontend_default,
                               dsu_invocation_t *out_invocation);

int dsu_macos_write_invocation(const dsu_invocation_t *inv, const char *path, dsu_u64 *out_digest);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DSU_MACOS_INVOCATION_H_INCLUDED */
