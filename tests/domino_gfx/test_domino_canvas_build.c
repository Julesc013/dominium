#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "domino/core.h"
#include "domino/inst.h"
#include "domino/canvas.h"
#include "domino/gfx.h"
#include "domino/sys.h"

#if defined(_WIN32)
#include <direct.h>
#define MKDIR(path) _mkdir(path)
#else
#include <sys/stat.h>
#include <unistd.h>
#define MKDIR(path) mkdir(path, 0777)
#endif

static int ensure_dir(const char* path)
{
    if (!path) {
        return -1;
    }
    return MKDIR(path);
}

static void set_user_data_root(const char* path)
{
    if (!path) {
        return;
    }
#if defined(_WIN32)
    {
        size_t len;
        char*  buf;
        len = strlen(path) + strlen("DSYS_PATH_USER_DATA=") + 1u;
        buf = (char*)malloc(len);
        if (buf) {
            sprintf(buf, "DSYS_PATH_USER_DATA=%s", path);
            _putenv(buf);
        }
    }
#else
    setenv("DSYS_PATH_USER_DATA", path, 1);
#endif
}

static void remove_tree(const char* path)
{
    dsys_dir_iter* it;
    dsys_dir_entry ent;
    char child[512];

    if (!path) {
        return;
    }

    it = dsys_dir_open(path);
    if (it) {
        while (dsys_dir_next(it, &ent)) {
            if (ent.name[0] == '.' && (ent.name[1] == '\0' ||
                                       (ent.name[1] == '.' && ent.name[2] == '\0'))) {
                continue;
            }
            sprintf(child, "%s/%s", path, ent.name);
            if (ent.is_dir) {
                remove_tree(child);
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
#if defined(_WIN32)
    _rmdir(path);
#else
    rmdir(path);
#endif
}

static int dump_cmds(const char* name, const dom_gfx_buffer* buf)
{
    size_t    offset;
    uint32_t  cmd_count;

    if (!buf || !buf->data) {
        return 0;
    }

    printf("-- %s (%lu bytes)\n", name, (unsigned long)buf->size);

    offset = 0u;
    cmd_count = 0u;
    while (offset + sizeof(dgfx_cmd) <= buf->size) {
        const dgfx_cmd* cmd;
        size_t step;

        cmd = (const dgfx_cmd*)(buf->data + offset);
        step = sizeof(dgfx_cmd) + (size_t)cmd->payload_size;
        printf("  op=%u payload=%u\n",
               (unsigned int)cmd->opcode,
               (unsigned int)cmd->payload_size);

        if (step == 0u) {
            return 0;
        }
        offset += step;
        cmd_count += 1u;
    }

    if (offset != buf->size) {
        printf("  size mismatch (offset=%lu size=%lu)\n",
               (unsigned long)offset,
               (unsigned long)buf->size);
        return 0;
    }

    return cmd_count > 0u;
}

int main(void)
{
    const char* user_root = "test_domino_canvas_build";
    dom_core_desc core_desc;
    dom_core* core;
    dom_instance_info inst_desc;
    dom_instance_id inst_id;
    uint8_t scratch[2048];
    dom_gfx_buffer buf;
    const char* canvases[] = {
        "world_surface",
        "world_orbit",
        "construction_exterior",
        "construction_interior"
    };
    size_t i;

    remove_tree(user_root);
    if (ensure_dir(user_root) != 0) {
        return 1;
    }
    set_user_data_root(user_root);

    core_desc.api_version = 1;
    core = dom_core_create(&core_desc);
    if (!core) {
        return 2;
    }

    memset(&inst_desc, 0, sizeof(inst_desc));
    inst_desc.struct_size = sizeof(dom_instance_info);
    inst_desc.struct_version = 1;
    strcpy(inst_desc.name, "canvas_inst");
    inst_id = dom_inst_create(core, &inst_desc);
    if (inst_id == 0) {
        dom_core_destroy(core);
        return 3;
    }

    buf.data = scratch;
    buf.size = 0;
    buf.capacity = sizeof(scratch);

    for (i = 0u; i < sizeof(canvases) / sizeof(canvases[0]); ++i) {
        buf.size = 0;
        if (!dom_canvas_build(core, inst_id, canvases[i], &buf)) {
            dom_core_destroy(core);
            return 4;
        }
        if (buf.size == 0 || !dump_cmds(canvases[i], &buf)) {
            dom_core_destroy(core);
            return 5;
        }
    }

    dom_core_destroy(core);
    remove_tree(user_root);
    return 0;
}
