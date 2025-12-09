#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <errno.h>

#if defined(_WIN32)
# include <direct.h>
#else
# include <sys/stat.h>
# include <unistd.h>
#endif

#include "dominium/setup_api.h"
#include "domino/sys.h"
#include "domino/core.h"
#include "domino/inst.h"
#include "domino/pkg.h"

#define DOM_SETUP_DESC_VERSION      1u
#define DOM_SETUP_COMMAND_VERSION   1u
#define DOM_SETUP_PROGRESS_VERSION  1u

typedef struct dom_setup_paths_t {
    char install_dir[512];
    char data_dir[512];
    char log_dir[512];
} dom_setup_paths;

typedef struct dom_setup_ctx_t {
    dom_core      *core;
    dom_setup_desc desc;
    dom_setup_paths paths;
} dom_setup_ctx_t;

typedef struct dom_setup_file_entry_t {
    const char* rel_source;
    const char* rel_dest;
} dom_setup_file_entry;

static const dom_setup_file_entry g_setup_manifest[] = {
    { "bin/dominium-placeholder.txt", "bin/dominium-placeholder.txt" },
    { "data/readme.txt",              "data/readme.txt" }
};

static void dom_setup_copy_string(char* dst, size_t cap, const char* src)
{
    size_t len;

    if (!dst || cap == 0u) {
        return;
    }
    if (!src) {
        dst[0] = '\0';
        return;
    }

    len = strlen(src);
    if (len >= cap) {
        len = cap - 1u;
    }
    memcpy(dst, src, len);
    dst[len] = '\0';
}

static int dom_setup_path_join(char* dst, size_t cap, const char* a, const char* b)
{
    size_t len;
    size_t i;

    if (!dst || cap == 0u) {
        return 0;
    }

    dst[0] = '\0';
    len = 0u;

    if (a && a[0] != '\0') {
        len = strlen(a);
        if (len >= cap) {
            len = cap - 1u;
        }
        memcpy(dst, a, len);
        dst[len] = '\0';
    }

    if (b && b[0] != '\0') {
        if (len > 0u && dst[len - 1u] != '/' && dst[len - 1u] != '\\') {
            if (len + 1u >= cap) {
                return 0;
            }
            dst[len] = '/';
            len += 1u;
            dst[len] = '\0';
        }
        for (i = 0u; b[i] != '\0'; ++i) {
            if (len + 1u >= cap) {
                dst[len] = '\0';
                return 0;
            }
            dst[len] = b[i];
            len += 1u;
        }
        dst[len] = '\0';
    }

    return 1;
}

static void dom_setup_dirname(const char* path, char* out, size_t cap)
{
    const char* last;
    size_t len;

    if (!out || cap == 0u) {
        return;
    }
    out[0] = '\0';

    if (!path) {
        return;
    }

    last = strrchr(path, '/');
    if (!last) {
        last = strrchr(path, '\\');
    }
    if (!last) {
        return;
    }
    len = (size_t)(last - path);
    if (len >= cap) {
        len = cap - 1u;
    }
    memcpy(out, path, len);
    out[len] = '\0';
}

static int dom_setup_make_dir(const char* path)
{
    int res;

    if (!path || path[0] == '\0') {
        return 0;
    }
#if defined(_WIN32)
    res = _mkdir(path);
#else
    res = mkdir(path, 0777);
#endif
    if (res == 0) {
        return 1;
    }
    if (errno == EEXIST) {
        return 1;
    }
    return 0;
}

static int dom_setup_mkdirs(const char* path)
{
    char partial[512];
    size_t i;
    size_t len;

    if (!path || path[0] == '\0') {
        return 0;
    }

    dom_setup_copy_string(partial, sizeof(partial), path);
    len = strlen(partial);
    for (i = 0u; i < len; ++i) {
        if (partial[i] == '/' || partial[i] == '\\') {
            char saved;
            if (i == 0u) {
                continue;
            }
            saved = partial[i];
            partial[i] = '\0';
            (void)dom_setup_make_dir(partial);
            partial[i] = saved;
        }
    }
    return dom_setup_make_dir(partial);
}

static int dom_setup_remove_tree(const char* path)
{
    dsys_dir_iter* it;
    dsys_dir_entry ent;
    char child[512];
    int ok;

    if (!path || path[0] == '\0') {
        return 0;
    }

    ok = 1;
    it = dsys_dir_open(path);
    if (it) {
        while (dsys_dir_next(it, &ent)) {
            if (ent.name[0] == '.' && (ent.name[1] == '\0' ||
                                       (ent.name[1] == '.' && ent.name[2] == '\0'))) {
                continue;
            }
            if (!dom_setup_path_join(child, sizeof(child), path, ent.name)) {
                ok = 0;
                break;
            }
            if (ent.is_dir) {
                if (!dom_setup_remove_tree(child)) {
                    ok = 0;
                    break;
                }
#if defined(_WIN32)
                _rmdir(child);
#else
                rmdir(child);
#endif
            } else {
                remove(child);
            }
        }
        dsys_dir_close(it);
    }

    if (!ok) {
        return 0;
    }

#if defined(_WIN32)
    if (_rmdir(path) != 0) {
        return 0;
    }
#else
    if (rmdir(path) != 0) {
        return 0;
    }
#endif
    return 1;
}

static uint64_t dom_setup_file_size(const char* path, int* ok)
{
    void* fh;
    long end_pos;
    uint64_t size;

    if (ok) {
        *ok = 0;
    }
    if (!path) {
        return 0u;
    }

    fh = dsys_file_open(path, "rb");
    if (!fh) {
        return 0u;
    }

    if (dsys_file_seek(fh, 0, SEEK_END) != 0) {
        dsys_file_close(fh);
        return 0u;
    }
    end_pos = dsys_file_tell(fh);
    if (end_pos < 0) {
        dsys_file_close(fh);
        return 0u;
    }
    size = (uint64_t)end_pos;
    (void)dsys_file_seek(fh, 0, SEEK_SET);
    dsys_file_close(fh);
    if (ok) {
        *ok = 1;
    }
    return size;
}

static void dom_setup_paths_for_scope(const dom_setup_desc* desc,
                                      dom_setup_paths* paths)
{
    char base[512];
    char user_data[512];
    char temp[512];

    dom_setup_copy_string(base, sizeof(base), "");
    dom_setup_copy_string(user_data, sizeof(user_data), "");

    if (desc->target_dir && desc->target_dir[0] != '\0') {
        dom_setup_copy_string(base, sizeof(base), desc->target_dir);
    } else {
        switch (desc->scope) {
        case DOM_SETUP_SCOPE_PORTABLE:
            if (!dsys_get_path(DSYS_PATH_APP_ROOT, base, sizeof(base))) {
                dom_setup_copy_string(base, sizeof(base), ".");
            }
            break;
        case DOM_SETUP_SCOPE_PER_USER:
            if (!dsys_get_path(DSYS_PATH_USER_DATA, base, sizeof(base))) {
                dom_setup_copy_string(base, sizeof(base), ".");
            }
            dom_setup_copy_string(temp, sizeof(temp), base);
            dom_setup_path_join(base, sizeof(base), temp, "Dominium");
            break;
        case DOM_SETUP_SCOPE_ALL_USERS:
        default:
            if (!dsys_get_path(DSYS_PATH_APP_ROOT, base, sizeof(base))) {
                dom_setup_copy_string(base, sizeof(base), ".");
            }
            dom_setup_copy_string(temp, sizeof(temp), base);
            dom_setup_path_join(base, sizeof(base), temp, "Dominium");
            break;
        }
    }

    dom_setup_copy_string(paths->install_dir, sizeof(paths->install_dir), base);

    if (desc->scope == DOM_SETUP_SCOPE_PORTABLE) {
        dom_setup_copy_string(paths->data_dir, sizeof(paths->data_dir), base);
    } else {
        if (!dsys_get_path(DSYS_PATH_USER_DATA, user_data, sizeof(user_data))) {
            dom_setup_copy_string(user_data, sizeof(user_data), ".");
        }
        dom_setup_copy_string(paths->data_dir, sizeof(paths->data_dir), user_data);
    }

    dom_setup_path_join(paths->log_dir, sizeof(paths->log_dir),
                        paths->data_dir, "logs");
}

static void dom_setup_emit_progress(dom_setup_progress_cb cb,
                                    void* user,
                                    dom_setup_progress* prog,
                                    const char* step)
{
    if (!prog) {
        return;
    }
    prog->current_step = step;
    if (cb) {
        cb(prog, user);
    }
}

static dom_setup_status dom_setup_calculate_totals(const char* dist_root,
                                                   dom_setup_progress* prog)
{
    size_t i;
    uint64_t total_bytes;
    uint32_t total_files;

    total_bytes = 0u;
    total_files = 0u;

    for (i = 0u; i < sizeof(g_setup_manifest) / sizeof(g_setup_manifest[0]); ++i) {
        char src_path[512];
        int ok;
        uint64_t sz;

        if (!dom_setup_path_join(src_path, sizeof(src_path),
                                 dist_root, g_setup_manifest[i].rel_source)) {
            return DOM_SETUP_STATUS_ERROR;
        }
        sz = dom_setup_file_size(src_path, &ok);
        if (!ok) {
            return DOM_SETUP_STATUS_IO_ERROR;
        }
        total_bytes += sz;
        total_files += 1u;
    }

    if (prog) {
        prog->bytes_total = total_bytes;
        prog->files_total = total_files;
    }
    return DOM_SETUP_STATUS_OK;
}

static dom_setup_status dom_setup_prepare_roots(const dom_setup_paths* paths)
{
    if (!paths) {
        return DOM_SETUP_STATUS_INVALID_ARGUMENT;
    }
    if (!dom_setup_mkdirs(paths->install_dir)) {
        return DOM_SETUP_STATUS_IO_ERROR;
    }
    if (!dom_setup_mkdirs(paths->data_dir)) {
        return DOM_SETUP_STATUS_IO_ERROR;
    }
    (void)dom_setup_mkdirs(paths->log_dir);
    return DOM_SETUP_STATUS_OK;
}

static dom_setup_status dom_setup_copy_file(const char* src,
                                            const char* dst,
                                            uint64_t* bytes_copied)
{
    void* src_fh;
    void* dst_fh;
    char buf[4096];
    size_t read_count;
    uint64_t total;
    char dst_dir[512];

    if (bytes_copied) {
        *bytes_copied = 0u;
    }

    src_fh = dsys_file_open(src, "rb");
    if (!src_fh) {
        return DOM_SETUP_STATUS_IO_ERROR;
    }

    dom_setup_dirname(dst, dst_dir, sizeof(dst_dir));
    if (dst_dir[0] != '\0') {
        if (!dom_setup_mkdirs(dst_dir)) {
            dsys_file_close(src_fh);
            return DOM_SETUP_STATUS_IO_ERROR;
        }
    }

    dst_fh = dsys_file_open(dst, "wb");
    if (!dst_fh) {
        dsys_file_close(src_fh);
        return DOM_SETUP_STATUS_IO_ERROR;
    }

    total = 0u;
    while (1) {
        read_count = dsys_file_read(src_fh, buf, sizeof(buf));
        if (read_count == 0u) {
            break;
        }
        if (dsys_file_write(dst_fh, buf, read_count) != read_count) {
            dsys_file_close(src_fh);
            dsys_file_close(dst_fh);
            return DOM_SETUP_STATUS_IO_ERROR;
        }
        total += read_count;
    }

    dsys_file_close(src_fh);
    dsys_file_close(dst_fh);

    if (bytes_copied) {
        *bytes_copied = total;
    }
    return DOM_SETUP_STATUS_OK;
}

static dom_setup_status dom_setup_copy_manifest(const dom_setup_paths* paths,
                                                const char* dist_root,
                                                dom_setup_progress* prog,
                                                dom_setup_progress_cb cb,
                                                void* cb_user)
{
    size_t i;

    for (i = 0u; i < sizeof(g_setup_manifest) / sizeof(g_setup_manifest[0]); ++i) {
        char src_path[512];
        char dst_path[512];
        dom_setup_status st;
        uint64_t copied;

        if (!dom_setup_path_join(src_path, sizeof(src_path),
                                 dist_root, g_setup_manifest[i].rel_source) ||
            !dom_setup_path_join(dst_path, sizeof(dst_path),
                                 paths->install_dir, g_setup_manifest[i].rel_dest)) {
            return DOM_SETUP_STATUS_ERROR;
        }

        st = dom_setup_copy_file(src_path, dst_path, &copied);
        if (st != DOM_SETUP_STATUS_OK) {
            return st;
        }

        if (prog) {
            prog->bytes_done += copied;
            prog->files_done += 1u;
            dom_setup_emit_progress(cb, cb_user, prog, "Copying files");
        }
    }

    return DOM_SETUP_STATUS_OK;
}

static int dom_setup_find_instance(dom_core* core,
                                   const char* path,
                                   dom_instance_id* out_id)
{
    dom_instance_info infos[16];
    uint32_t count;
    uint32_t i;

    if (out_id) {
        *out_id = 0u;
    }

    if (!core || !path) {
        return 0;
    }

    count = dom_inst_list(core, infos, 16u);
    for (i = 0u; i < count; ++i) {
        if (strcmp(infos[i].path, path) == 0) {
            if (out_id) {
                *out_id = infos[i].id;
            }
            return 1;
        }
    }
    return 0;
}

static dom_setup_status dom_setup_create_instance(dom_setup_ctx_t* ctx,
                                                  const dom_setup_paths* paths)
{
    dom_instance_info info;
    char inst_root[512];
    dom_instance_id existing_id;
    dom_instance_id new_id;

    if (!ctx || !paths) {
        return DOM_SETUP_STATUS_INVALID_ARGUMENT;
    }

    if (ctx->desc.scope == DOM_SETUP_SCOPE_PORTABLE) {
        if (!dom_setup_path_join(inst_root, sizeof(inst_root),
                                 paths->install_dir, "instances/default")) {
            return DOM_SETUP_STATUS_ERROR;
        }
    } else {
        if (!dom_setup_path_join(inst_root, sizeof(inst_root),
                                 paths->data_dir, "instances/default")) {
            return DOM_SETUP_STATUS_ERROR;
        }
    }

    if (dom_setup_find_instance(ctx->core, inst_root, &existing_id)) {
        (void)existing_id;
        return DOM_SETUP_STATUS_OK;
    }

    memset(&info, 0, sizeof(info));
    info.struct_size = sizeof(dom_instance_info);
    info.struct_version = 1;
    dom_setup_copy_string(info.name, sizeof(info.name), "default");
    dom_setup_copy_string(info.path, sizeof(info.path), inst_root);
    dom_setup_path_join(info.saves_path, sizeof(info.saves_path), inst_root, "saves");
    dom_setup_path_join(info.config_path, sizeof(info.config_path), inst_root, "config");
    dom_setup_path_join(info.logs_path, sizeof(info.logs_path), inst_root, "logs");
    info.flags = (uint32_t)ctx->desc.scope;
    info.pkg_count = 0u;

    new_id = dom_inst_create(ctx->core, &info);
    if (new_id == 0u) {
        return DOM_SETUP_STATUS_ERROR;
    }
    return DOM_SETUP_STATUS_OK;
}

static dom_setup_status dom_setup_delete_instance(dom_setup_ctx_t* ctx,
                                                  const dom_setup_paths* paths)
{
    char inst_root[512];
    dom_instance_id inst_id;

    if (!ctx || !paths) {
        return DOM_SETUP_STATUS_INVALID_ARGUMENT;
    }

    if (ctx->desc.scope == DOM_SETUP_SCOPE_PORTABLE) {
        if (!dom_setup_path_join(inst_root, sizeof(inst_root),
                                 paths->install_dir, "instances/default")) {
            return DOM_SETUP_STATUS_ERROR;
        }
    } else {
        if (!dom_setup_path_join(inst_root, sizeof(inst_root),
                                 paths->data_dir, "instances/default")) {
            return DOM_SETUP_STATUS_ERROR;
        }
    }

    if (dom_setup_find_instance(ctx->core, inst_root, &inst_id)) {
        if (!dom_inst_delete(ctx->core, inst_id)) {
            return DOM_SETUP_STATUS_ERROR;
        }
    } else {
        (void)dom_setup_remove_tree(inst_root);
    }

    return DOM_SETUP_STATUS_OK;
}

static dom_setup_status dom_setup_do_install(dom_setup_ctx_t* ctx,
                                             dom_setup_paths* paths,
                                             dom_setup_progress* prog,
                                             dom_setup_progress_cb cb,
                                             void* cb_user)
{
    dom_setup_status st;
    char dist_root[512];
    char dist_base[512];

    dom_setup_emit_progress(cb, cb_user, prog, "Preparing directories");
    st = dom_setup_prepare_roots(paths);
    if (st != DOM_SETUP_STATUS_OK) {
        return st;
    }

    if (!dsys_get_path(DSYS_PATH_APP_ROOT, dist_root, sizeof(dist_root))) {
        dom_setup_copy_string(dist_root, sizeof(dist_root), ".");
    }
    dom_setup_copy_string(dist_base, sizeof(dist_base), dist_root);
    dom_setup_path_join(dist_root, sizeof(dist_root), dist_base, "dist");

    st = dom_setup_calculate_totals(dist_root, prog);
    if (st != DOM_SETUP_STATUS_OK) {
        return st;
    }

    dom_setup_emit_progress(cb, cb_user, prog, "Copying files");
    st = dom_setup_copy_manifest(paths, dist_root, prog, cb, cb_user);
    if (st != DOM_SETUP_STATUS_OK) {
        return st;
    }

    dom_setup_emit_progress(cb, cb_user, prog, "Registering instance");
    st = dom_setup_create_instance(ctx, paths);
    if (st != DOM_SETUP_STATUS_OK) {
        return st;
    }

    dom_setup_emit_progress(cb, cb_user, prog, "Install complete");
    return DOM_SETUP_STATUS_OK;
}

static dom_setup_status dom_setup_do_repair(dom_setup_ctx_t* ctx,
                                            dom_setup_paths* paths,
                                            dom_setup_progress* prog,
                                            dom_setup_progress_cb cb,
                                            void* cb_user)
{
    dom_setup_status st;
    char dist_root[512];
    char dist_base[512];

    dom_setup_emit_progress(cb, cb_user, prog, "Preparing directories");
    st = dom_setup_prepare_roots(paths);
    if (st != DOM_SETUP_STATUS_OK) {
        return st;
    }

    if (!dsys_get_path(DSYS_PATH_APP_ROOT, dist_root, sizeof(dist_root))) {
        dom_setup_copy_string(dist_root, sizeof(dist_root), ".");
    }
    dom_setup_copy_string(dist_base, sizeof(dist_base), dist_root);
    dom_setup_path_join(dist_root, sizeof(dist_root), dist_base, "dist");

    st = dom_setup_calculate_totals(dist_root, prog);
    if (st != DOM_SETUP_STATUS_OK) {
        return st;
    }

    dom_setup_emit_progress(cb, cb_user, prog, "Repairing files");
    st = dom_setup_copy_manifest(paths, dist_root, prog, cb, cb_user);
    if (st != DOM_SETUP_STATUS_OK) {
        return st;
    }

    dom_setup_emit_progress(cb, cb_user, prog, "Ensuring instance");
    st = dom_setup_create_instance(ctx, paths);
    if (st != DOM_SETUP_STATUS_OK) {
        return st;
    }

    dom_setup_emit_progress(cb, cb_user, prog, "Repair complete");
    return DOM_SETUP_STATUS_OK;
}

static dom_setup_status dom_setup_do_uninstall(dom_setup_ctx_t* ctx,
                                               dom_setup_paths* paths,
                                               dom_setup_progress* prog,
                                               dom_setup_progress_cb cb,
                                               void* cb_user)
{
    dom_setup_status st;

    dom_setup_emit_progress(cb, cb_user, prog, "Removing instance");
    st = dom_setup_delete_instance(ctx, paths);
    if (st != DOM_SETUP_STATUS_OK) {
        return st;
    }

    dom_setup_emit_progress(cb, cb_user, prog, "Removing files");
    (void)dom_setup_remove_tree(paths->install_dir);

    dom_setup_emit_progress(cb, cb_user, prog, "Uninstall complete");
    return DOM_SETUP_STATUS_OK;
}

static dom_setup_status dom_setup_do_verify(dom_setup_ctx_t* ctx,
                                            dom_setup_paths* paths,
                                            dom_setup_progress* prog,
                                            dom_setup_progress_cb cb,
                                            void* cb_user)
{
    size_t i;
    char dist_root[512];
    char dist_base[512];
    dom_setup_status st;

    (void)ctx;
    (void)paths;

    if (!dsys_get_path(DSYS_PATH_APP_ROOT, dist_root, sizeof(dist_root))) {
        dom_setup_copy_string(dist_root, sizeof(dist_root), ".");
    }
    dom_setup_copy_string(dist_base, sizeof(dist_base), dist_root);
    dom_setup_path_join(dist_root, sizeof(dist_root), dist_base, "dist");

    st = dom_setup_calculate_totals(dist_root, prog);
    if (st != DOM_SETUP_STATUS_OK) {
        return st;
    }

    dom_setup_emit_progress(cb, cb_user, prog, "Verifying files");
    for (i = 0u; i < sizeof(g_setup_manifest) / sizeof(g_setup_manifest[0]); ++i) {
        char src_path[512];
        char dst_path[512];
        int ok;
        uint64_t sz;

        if (!dom_setup_path_join(src_path, sizeof(src_path),
                                 dist_root, g_setup_manifest[i].rel_source) ||
            !dom_setup_path_join(dst_path, sizeof(dst_path),
                                 paths->install_dir, g_setup_manifest[i].rel_dest)) {
            return DOM_SETUP_STATUS_ERROR;
        }

        sz = dom_setup_file_size(dst_path, &ok);
        if (!ok || sz == 0u) {
            return DOM_SETUP_STATUS_IO_ERROR;
        }

        prog->bytes_done += sz;
        prog->files_done += 1u;
        dom_setup_emit_progress(cb, cb_user, prog, "Verifying files");
    }

    dom_setup_emit_progress(cb, cb_user, prog, "Verify complete");
    return DOM_SETUP_STATUS_OK;
}

dom_setup_status dom_setup_create(dom_core* core,
                                  const dom_setup_desc* desc,
                                  void** out_ctx)
{
    dom_setup_ctx_t* ctx;

    if (!core || !desc || !out_ctx) {
        return DOM_SETUP_STATUS_INVALID_ARGUMENT;
    }

    if (desc->struct_size != sizeof(dom_setup_desc) ||
        desc->struct_version != DOM_SETUP_DESC_VERSION) {
        return DOM_SETUP_STATUS_INVALID_ARGUMENT;
    }

    ctx = (dom_setup_ctx_t*)malloc(sizeof(dom_setup_ctx_t));
    if (!ctx) {
        return DOM_SETUP_STATUS_ERROR;
    }
    memset(ctx, 0, sizeof(*ctx));

    ctx->core = core;
    ctx->desc = *desc;
    dom_setup_paths_for_scope(desc, &ctx->paths);

    *out_ctx = ctx;
    return DOM_SETUP_STATUS_OK;
}

void dom_setup_destroy(void* ctx_ptr)
{
    dom_setup_ctx_t* ctx;

    ctx = (dom_setup_ctx_t*)ctx_ptr;
    if (!ctx) {
        return;
    }
    free(ctx);
}

dom_setup_status dom_setup_execute(void* ctx_ptr,
                                   const dom_setup_command* cmd,
                                   dom_setup_progress_cb cb,
                                   void* cb_user)
{
    dom_setup_ctx_t* ctx;
    dom_setup_progress prog;
    dom_setup_paths active_paths;
    dom_setup_status st;

    ctx = (dom_setup_ctx_t*)ctx_ptr;
    if (!ctx || !cmd) {
        return DOM_SETUP_STATUS_INVALID_ARGUMENT;
    }

    if (cmd->struct_size != sizeof(dom_setup_command) ||
        cmd->struct_version != DOM_SETUP_COMMAND_VERSION) {
        return DOM_SETUP_STATUS_INVALID_ARGUMENT;
    }

    memset(&prog, 0, sizeof(prog));
    prog.struct_size = sizeof(dom_setup_progress);
    prog.struct_version = DOM_SETUP_PROGRESS_VERSION;
    prog.bytes_total = 0u;
    prog.bytes_done = 0u;
    prog.files_total = 0u;
    prog.files_done = 0u;
    prog.current_step = NULL;

    active_paths = ctx->paths;
    if (cmd->existing_install_dir && cmd->existing_install_dir[0] != '\0') {
        dom_setup_copy_string(active_paths.install_dir, sizeof(active_paths.install_dir),
                              cmd->existing_install_dir);
        if (ctx->desc.scope == DOM_SETUP_SCOPE_PORTABLE) {
            dom_setup_copy_string(active_paths.data_dir, sizeof(active_paths.data_dir),
                                  active_paths.install_dir);
            dom_setup_path_join(active_paths.log_dir, sizeof(active_paths.log_dir),
                                active_paths.data_dir, "logs");
        }
    }

    switch (cmd->action) {
    case DOM_SETUP_ACTION_INSTALL:
        st = dom_setup_do_install(ctx, &active_paths, &prog, cb, cb_user);
        break;
    case DOM_SETUP_ACTION_REPAIR:
        st = dom_setup_do_repair(ctx, &active_paths, &prog, cb, cb_user);
        break;
    case DOM_SETUP_ACTION_UNINSTALL:
        st = dom_setup_do_uninstall(ctx, &active_paths, &prog, cb, cb_user);
        break;
    case DOM_SETUP_ACTION_VERIFY:
        st = dom_setup_do_verify(ctx, &active_paths, &prog, cb, cb_user);
        break;
    default:
        st = DOM_SETUP_STATUS_INVALID_ARGUMENT;
        break;
    }

    return st;
}
