#ifndef DSU_LINUX_INVOCATION_H_INCLUDED
#define DSU_LINUX_INVOCATION_H_INCLUDED

#include "dsu_linux_args.h"

#include "dsu/dsu_invocation.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dsu_linux_csv_list_t {
    char **items;
    unsigned long count;
} dsu_linux_csv_list_t;

void dsu_linux_csv_list_free(dsu_linux_csv_list_t *list);
int dsu_linux_csv_list_parse(const char *csv, dsu_linux_csv_list_t *out_list);

int dsu_linux_build_invocation(const dsu_linux_cli_args_t *args,
                               const char *platform_default,
                               const char *ui_mode_default,
                               const char *frontend_default,
                               dsu_invocation_t *out_invocation);

int dsu_linux_write_invocation(const dsu_invocation_t *inv, const char *path, dsu_u64 *out_digest);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DSU_LINUX_INVOCATION_H_INCLUDED */
