/*
FILE: tests/domino_sim/test_domino_dominium_sim.c
MODULE: Repository
LAYER / SUBSYSTEM: tests/domino_sim
RESPONSIBILITY: Owns documentation for this translation unit.
ALLOWED DEPENDENCIES: Project-local headers; C89/C++98 standard headers.
FORBIDDEN DEPENDENCIES: N/A.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include "domino/core.h"
#include "domino/inst.h"
#include "domino/sim.h"
#include "domino/sys.h"
#include "dominium/game_api.h"
#include "dominium/world.h"
#include "dominium/constructions.h"
#include "dominium/actors.h"

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

static int double_near(double a, double b, double epsilon)
{
    double diff;
    if (epsilon < 0.0) {
        return 0;
    }
    diff = a - b;
    if (diff < 0.0) {
        diff = -diff;
    }
    return diff <= epsilon;
}

int main(void)
{
    const char* user_root = "test_domino_sim_dominium";
    dom_core_desc core_desc;
    dom_core* core;
    dom_instance_info inst_desc;
    dom_instance_id inst_id;
    dom_sim_state sim_state;

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
    strcpy(inst_desc.name, "sim_dominium");
    inst_id = dom_inst_create(core, &inst_desc);
    if (inst_id == 0) {
        dom_core_destroy(core);
        return 3;
    }

    if (!dom_sim_tick(core, inst_id, 10u)) {
        dom_core_destroy(core);
        return 4;
    }

    memset(&sim_state, 0, sizeof(sim_state));
    if (!dom_sim_get_state(core, inst_id, &sim_state)) {
        dom_core_destroy(core);
        return 5;
    }
    if (sim_state.ticks != 10u ||
        sim_state.struct_size != sizeof(dom_sim_state) ||
        sim_state.struct_version != 1u ||
        !double_near(sim_state.dt_s, 1.0 / 60.0, 1e-6)) {
        dom_core_destroy(core);
        return 6;
    }

    if (dom_game_debug_sim_steps(inst_id) != 10u ||
        dom_world_debug_step_count(inst_id) != 10u ||
        dom_constructions_debug_step_count(inst_id) != 10u ||
        dom_actors_debug_step_count(inst_id) != 10u) {
        dom_core_destroy(core);
        return 7;
    }

    dom_core_destroy(core);
    remove_tree(user_root);
    return 0;
}
