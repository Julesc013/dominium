/*
FILE: source/dominium/setup/core/src/fs/dsu_platform_iface.h
MODULE: Dominium Setup
PURPOSE: Host OS interface for filesystem primitives (OS-specific code lives in dsu_platform_iface.c).
*/
#ifndef DSU_PLATFORM_IFACE_H_INCLUDED
#define DSU_PLATFORM_IFACE_H_INCLUDED

#include "../util/dsu_util_internal.h"

typedef struct dsu_platform_dir_entry_t {
    char *name; /* owned (as provided by OS) */
    dsu_u8 is_dir;
    dsu_u8 is_symlink;
    dsu_u8 reserved8[2];
} dsu_platform_dir_entry_t;

dsu_status_t dsu_platform_path_info(const char *path,
                                   dsu_u8 *out_exists,
                                   dsu_u8 *out_is_dir,
                                   dsu_u8 *out_is_symlink);

dsu_status_t dsu_platform_mkdir(const char *path);
dsu_status_t dsu_platform_rmdir(const char *path);
dsu_status_t dsu_platform_remove_file(const char *path);

dsu_status_t dsu_platform_rename(const char *src, const char *dst, dsu_u8 replace_existing);

dsu_status_t dsu_platform_list_dir(const char *path, dsu_platform_dir_entry_t **out_entries, dsu_u32 *out_count);
void dsu_platform_free_dir_entries(dsu_platform_dir_entry_t *entries, dsu_u32 count);

dsu_status_t dsu_platform_disk_free_bytes(const char *path, dsu_u64 *out_free_bytes);

#endif /* DSU_PLATFORM_IFACE_H_INCLUDED */

