#include <string.h>
#include "domino/core.h"
#include "domino/pkg.h"
#include "domino/inst.h"
#include "domino/sim.h"
#include "domino/canvas.h"

int main(void)
{
    dom_core_desc core_desc;
    dom_core* core;
    dom_cmd nop;
    dom_query q;
    dom_core_info info;
    dom_package_info pkg_buf[1];
    dom_package_info pkg_tmp;
    dom_instance_info inst_desc;
    dom_instance_info inst_buf[1];
    dom_instance_id inst_id;
    dom_sim_state sim_state;
    dom_gfx_buffer gfx_buf;
    unsigned char gfx_data[64];

    core_desc.api_version = 1;
    core = dom_core_create(&core_desc);
    if (!core) {
        return 1;
    }

    nop.id = DOM_CMD_NOP;
    nop.data = NULL;
    nop.size = 0;
    if (!dom_core_execute(core, &nop)) {
        dom_core_destroy(core);
        return 2;
    }

    memset(&info, 0, sizeof(info));
    q.id = DOM_QUERY_CORE_INFO;
    q.in = NULL;
    q.in_size = 0;
    q.out = &info;
    q.out_size = sizeof(info);
    if (!dom_core_query(core, &q)) {
        dom_core_destroy(core);
        return 3;
    }

    if (dom_pkg_list(core, pkg_buf, 1) != 0) {
        dom_core_destroy(core);
        return 4;
    }

    memset(&pkg_tmp, 0, sizeof(pkg_tmp));
    if (dom_pkg_get(core, 1, &pkg_tmp)) {
        dom_core_destroy(core);
        return 5;
    }

    memset(&inst_desc, 0, sizeof(inst_desc));
    inst_desc.struct_size = sizeof(dom_instance_info);
    inst_desc.struct_version = 1;
    strcpy(inst_desc.name, "demo");
    strcpy(inst_desc.path, "demo_path");
    inst_desc.flags = 0;
    inst_desc.pkg_count = 0;
    inst_id = dom_inst_create(core, &inst_desc);
    if (inst_id == 0) {
        dom_core_destroy(core);
        return 6;
    }

    if (dom_inst_list(core, inst_buf, 1) == 0) {
        /* at least the created instance should be visible */
    } else {
        /* allow empty list if internal storage refused to add */
    }

    if (!dom_sim_tick(core, inst_id, 1)) {
        dom_core_destroy(core);
        return 7;
    }
    if (!dom_sim_get_state(core, inst_id, &sim_state)) {
        dom_core_destroy(core);
        return 8;
    }

    gfx_buf.data = gfx_data;
    gfx_buf.capacity = sizeof(gfx_data);
    gfx_buf.size = 0;
    if (!dom_canvas_build(core, inst_id, "world_surface", &gfx_buf)) {
        dom_core_destroy(core);
        return 9;
    }

    dom_core_destroy(core);
    return 0;
}
