/*
FILE: source/dominium/setup/core/include/dsu/dsu_fs.h
MODULE: Dominium Setup
PURPOSE: Strict, root-scoped filesystem abstraction for journaled transactions (Plan S-4).
*/
#ifndef DSU_FS_H_INCLUDED
#define DSU_FS_H_INCLUDED

#include "dsu_ctx.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dsu_fs dsu_fs_t;

typedef enum dsu_fs_perm_flags_t {
    DSU_FS_PERM_NONE  = 0,
    DSU_FS_PERM_READ  = 1u << 0,
    DSU_FS_PERM_WRITE = 1u << 1,
    DSU_FS_PERM_EXEC  = 1u << 2
} dsu_fs_perm_flags_t;

typedef struct dsu_fs_options_t {
    dsu_u32 struct_size;
    dsu_u32 struct_version;

    /* Array of absolute allowed roots (canonicalized internally). */
    const char *const *allowed_roots;
    dsu_u32 allowed_root_count;
} dsu_fs_options_t;

DSU_API void dsu_fs_options_init(dsu_fs_options_t *opts);

DSU_API dsu_status_t dsu_fs_create(dsu_ctx_t *ctx, const dsu_fs_options_t *opts, dsu_fs_t **out_fs);
DSU_API void dsu_fs_destroy(dsu_ctx_t *ctx, dsu_fs_t *fs);

DSU_API dsu_u32 dsu_fs_allowed_root_count(const dsu_fs_t *fs);
DSU_API const char *dsu_fs_allowed_root(const dsu_fs_t *fs, dsu_u32 index);

/* Path helpers (canonical DSU paths use '/' separators). */
DSU_API dsu_status_t dsu_fs_path_canonicalize(const char *path_in,
                                             char *path_out,
                                             dsu_u32 path_out_cap);
DSU_API dsu_status_t dsu_fs_path_join(const char *a,
                                     const char *b,
                                     char *out_path,
                                     dsu_u32 out_cap);
DSU_API dsu_status_t dsu_fs_path_split(const char *path,
                                      char *out_dir,
                                      dsu_u32 out_dir_cap,
                                      char *out_base,
                                      dsu_u32 out_base_cap);

/*
Resolve a relative path under an allowed root index into an absolute canonical path.

Rules:
- `rel` must be a relative DSU path (no drive/UNC, no leading '/', no '..' segments).
- All traversed existing prefixes must not be symlinks/reparse points.
*/
DSU_API dsu_status_t dsu_fs_resolve_under_root(dsu_fs_t *fs,
                                              dsu_u32 root_index,
                                              const char *rel,
                                              char *out_abs,
                                              dsu_u32 out_abs_cap);

/* Filesystem operations (all paths are root-scoped relative DSU paths). */
DSU_API dsu_status_t dsu_fs_mkdir_p(dsu_fs_t *fs, dsu_u32 root_index, const char *rel_dir);
DSU_API dsu_status_t dsu_fs_rmdir_empty(dsu_fs_t *fs, dsu_u32 root_index, const char *rel_dir);

DSU_API dsu_status_t dsu_fs_copy_file(dsu_fs_t *fs,
                                      dsu_u32 src_root,
                                      const char *src_rel,
                                      dsu_u32 dst_root,
                                      const char *dst_rel,
                                      dsu_bool replace_existing);
DSU_API dsu_status_t dsu_fs_move_path(dsu_fs_t *fs,
                                     dsu_u32 src_root,
                                     const char *src_rel,
                                     dsu_u32 dst_root,
                                     const char *dst_rel,
                                     dsu_bool replace_existing);
DSU_API dsu_status_t dsu_fs_delete_file(dsu_fs_t *fs, dsu_u32 root_index, const char *rel_path);

DSU_API dsu_status_t dsu_fs_write_file_atomic(dsu_fs_t *fs,
                                              dsu_u32 root_index,
                                              const char *rel_path,
                                              const dsu_u8 *bytes,
                                              dsu_u32 len,
                                              dsu_bool replace_existing);

/* Hash a file's contents (SHA-256; 32 bytes). */
DSU_API dsu_status_t dsu_fs_hash_file(dsu_fs_t *fs,
                                      dsu_u32 root_index,
                                      const char *rel_path,
                                      dsu_u8 out_sha256[32]);

/* Permission query (best-effort; may return 0 if unknown). */
DSU_API dsu_status_t dsu_fs_query_permissions(dsu_fs_t *fs,
                                              dsu_u32 root_index,
                                              const char *rel_path,
                                              dsu_u32 *out_perm_flags);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DSU_FS_H_INCLUDED */

