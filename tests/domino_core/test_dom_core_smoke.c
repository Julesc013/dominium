#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include "domino/core.h"
#include "domino/event.h"
#include "domino/pkg.h"
#include "domino/inst.h"
#include "domino/sim.h"
#include "domino/canvas.h"

#if defined(_WIN32)
#include <direct.h>
#define MKDIR(path) _mkdir(path)
#else
#include <sys/stat.h>
#include <unistd.h>
#define MKDIR(path) mkdir(path, 0777)
#endif

typedef struct test_events {
    uint32_t pkg_installed;
    uint32_t inst_created;
    uint32_t sim_ticked;
} test_events;

static int ensure_dir(const char* path)
{
    if (!path) {
        return -1;
    }
    return MKDIR(path);
}

static int write_text_file(const char* path, const char* text)
{
    FILE* f;

    f = fopen(path, "w");
    if (!f) {
        return 0;
    }
    fputs(text, f);
    fclose(f);
    return 1;
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

static void test_event_handler(dom_core* core, const dom_event* ev, void* user)
{
    test_events* counts;

    (void)core;

    counts = (test_events*)user;
    if (!counts || !ev) {
        return;
    }

    switch (ev->kind) {
    case DOM_EVT_PKG_INSTALLED:
        counts->pkg_installed += 1;
        break;
    case DOM_EVT_INST_CREATED:
        counts->inst_created += 1;
        break;
    case DOM_EVT_SIM_TICKED:
        counts->sim_ticked += 1;
        break;
    default:
        break;
    }
}

int main(void)
{
    const char* user_root = "test_dom_core_fs";
    char pkg_src_root[260];
    char pkg_src_path[260];
    char pkg_manifest_path[260];
    char pkg_content_path[260];
    char mods_manifest_path[260];
    char inst_descriptor_path[260];
    dom_core_desc core_desc;
    dom_core* core;
    dom_cmd cmd;
    dom_query query;
    dom_cmd_pkg_install cmd_pkg_install;
    dom_cmd_inst_create cmd_inst_create;
    dom_cmd_sim_tick cmd_sim_tick;
    dom_query_core_info_out core_info;
    dom_query_pkg_list_out pkg_list;
    dom_package_info pkg_buf[4];
    dom_query_pkg_info_in pkg_info_in;
    dom_query_pkg_info_out pkg_info_out;
    dom_query_inst_list_out inst_list;
    dom_instance_info inst_buf[4];
    dom_query_inst_info_in inst_info_in;
    dom_query_inst_info_out inst_info_out;
    dom_query_sim_state_in sim_in;
    dom_query_sim_state_out sim_out;
    dom_instance_id inst_id;
    dom_package_id pkg_id;
    test_events events;
    FILE* file_check;

    remove_tree(user_root);
    if (ensure_dir(user_root) != 0) {
        return 1;
    }
    sprintf(pkg_src_root, "%s/src_pkg", user_root);
    sprintf(pkg_src_path, "%s/demo_pkg", pkg_src_root);
    sprintf(pkg_manifest_path, "%s/manifest.ini", pkg_src_path);
    sprintf(pkg_content_path, "%s/content", pkg_src_path);
    if (ensure_dir(pkg_src_root) != 0 ||
        ensure_dir(pkg_src_path) != 0 ||
        ensure_dir(pkg_content_path) != 0 ||
        !write_text_file(pkg_manifest_path,
                         "id=demo_pkg\n"
                         "kind=mod\n"
                         "version=1.0.0\n"
                         "author=tester\n"
                         "deps=\n"
                         "game_version_min=0.0.0\n"
                         "game_version_max=*\n")) {
        return 1;
    }
    set_user_data_root(user_root);
    sprintf(mods_manifest_path, "%s/mods/tester/demo_pkg/manifest.ini", user_root);
    sprintf(inst_descriptor_path, "%s/instances/demo_inst/instance.ini", user_root);

    core_desc.api_version = 1;
    core = dom_core_create(&core_desc);
    if (!core) {
        return 1;
    }

    memset(&events, 0, sizeof(events));
    if (!dom_event_subscribe(core, DOM_EVT_PKG_INSTALLED, test_event_handler, &events) ||
        !dom_event_subscribe(core, DOM_EVT_INST_CREATED, test_event_handler, &events) ||
        !dom_event_subscribe(core, DOM_EVT_SIM_TICKED, test_event_handler, &events)) {
        dom_core_destroy(core);
        return 2;
    }

    /* Install a package */
    cmd_pkg_install.source_path = pkg_src_path;
    cmd.id = DOM_CMD_PKG_INSTALL;
    cmd.data = &cmd_pkg_install;
    cmd.size = sizeof(cmd_pkg_install);
    if (!dom_core_execute(core, &cmd)) {
        dom_core_destroy(core);
        return 3;
    }

    /* List packages and grab the id */
    memset(&pkg_list, 0, sizeof(pkg_list));
    pkg_list.items = pkg_buf;
    pkg_list.max_items = 4;
    query.id = DOM_QUERY_PKG_LIST;
    query.in = NULL;
    query.in_size = 0;
    query.out = &pkg_list;
    query.out_size = sizeof(pkg_list);
    if (!dom_core_query(core, &query) || pkg_list.count != 1) {
        dom_core_destroy(core);
        return 4;
    }
    file_check = fopen(mods_manifest_path, "r");
    if (!file_check) {
        dom_core_destroy(core);
        return 13;
    }
    fclose(file_check);
    if (strcmp(pkg_list.items[0].manifest_path, mods_manifest_path) != 0) {
        dom_core_destroy(core);
        return 14;
    }
    pkg_id = pkg_list.items[0].id;

    memset(&pkg_info_out, 0, sizeof(pkg_info_out));
    pkg_info_in.id = pkg_id;
    query.id = DOM_QUERY_PKG_INFO;
    query.in = &pkg_info_in;
    query.in_size = sizeof(pkg_info_in);
    query.out = &pkg_info_out;
    query.out_size = sizeof(pkg_info_out);
    if (!dom_core_query(core, &query) || pkg_info_out.info.id != pkg_id) {
        dom_core_destroy(core);
        return 5;
    }

    /* Create an instance */
    memset(&cmd_inst_create, 0, sizeof(cmd_inst_create));
    cmd_inst_create.info.struct_size = sizeof(dom_instance_info);
    cmd_inst_create.info.struct_version = 1;
    strcpy(cmd_inst_create.info.name, "demo_inst");
    cmd_inst_create.info.pkg_count = 1;
    cmd_inst_create.info.pkgs[0] = pkg_id;

    cmd.id = DOM_CMD_INST_CREATE;
    cmd.data = &cmd_inst_create;
    cmd.size = sizeof(cmd_inst_create);
    if (!dom_core_execute(core, &cmd)) {
        dom_core_destroy(core);
        return 6;
    }
    file_check = fopen(inst_descriptor_path, "r");
    if (!file_check) {
        dom_core_destroy(core);
        return 15;
    }
    fclose(file_check);

    memset(&inst_list, 0, sizeof(inst_list));
    inst_list.items = inst_buf;
    inst_list.max_items = 4;
    query.id = DOM_QUERY_INST_LIST;
    query.in = NULL;
    query.in_size = 0;
    query.out = &inst_list;
    query.out_size = sizeof(inst_list);
    if (!dom_core_query(core, &query) || inst_list.count != 1) {
        dom_core_destroy(core);
        return 7;
    }
    if (strcmp(inst_list.items[0].descriptor_path, inst_descriptor_path) != 0) {
        dom_core_destroy(core);
        return 16;
    }
    inst_id = inst_list.items[0].id;

    memset(&inst_info_out, 0, sizeof(inst_info_out));
    inst_info_in.id = inst_id;
    query.id = DOM_QUERY_INST_INFO;
    query.in = &inst_info_in;
    query.in_size = sizeof(inst_info_in);
    query.out = &inst_info_out;
    query.out_size = sizeof(inst_info_out);
    if (!dom_core_query(core, &query) ||
        inst_info_out.info.id != inst_id ||
        inst_info_out.info.pkg_count != 1) {
        dom_core_destroy(core);
        return 8;
    }

    /* Tick sim */
    cmd_sim_tick.id = inst_id;
    cmd_sim_tick.ticks = 5;
    cmd.id = DOM_CMD_SIM_TICK;
    cmd.data = &cmd_sim_tick;
    cmd.size = sizeof(cmd_sim_tick);
    if (!dom_core_execute(core, &cmd)) {
        dom_core_destroy(core);
        return 9;
    }

    sim_in.id = inst_id;
    memset(&sim_out, 0, sizeof(sim_out));
    query.id = DOM_QUERY_SIM_STATE;
    query.in = &sim_in;
    query.in_size = sizeof(sim_in);
    query.out = &sim_out;
    query.out_size = sizeof(sim_out);
    if (!dom_core_query(core, &query) ||
        sim_out.state.ticks != 5 ||
        sim_out.state.struct_size != sizeof(dom_sim_state)) {
        dom_core_destroy(core);
        return 10;
    }

    memset(&core_info, 0, sizeof(core_info));
    query.id = DOM_QUERY_CORE_INFO;
    query.in = NULL;
    query.in_size = 0;
    query.out = &core_info;
    query.out_size = sizeof(core_info);
    if (!dom_core_query(core, &query) ||
        core_info.package_count != 1 ||
        core_info.instance_count != 1) {
        dom_core_destroy(core);
        return 11;
    }

    if (events.pkg_installed != 1 ||
        events.inst_created != 1 ||
        events.sim_ticked != 1) {
        dom_core_destroy(core);
        return 12;
    }

    dom_core_destroy(core);
    return 0;
}
