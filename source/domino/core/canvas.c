#include <stddef.h>
#include <string.h>
#include "core_internal.h"
#include "domino/gfx.h"
#include "dominium/world.h"
#include "dominium/constructions.h"

bool dom_canvas_build(dom_core* core, dom_instance_id inst, const char* canvas_id, dom_gfx_buffer* out)
{
    if (!core || !canvas_id || !out) {
        return false;
    }

    out->size = 0;

    if (strcmp(canvas_id, "world_surface") == 0) {
        return dom_world_build_surface_canvas(core, inst, out);
    }
    if (strcmp(canvas_id, "world_orbit") == 0) {
        return dom_world_build_orbit_canvas(core, inst, out);
    }
    if (strcmp(canvas_id, "construction_exterior") == 0 ||
        strcmp(canvas_id, "construction_interior") == 0) {
        return dom_construction_build_canvas(core, inst, canvas_id, out);
    }

    {
        uint32_t i;
        for (i = 0u; i < core->launcher_ext_count; ++i) {
            const dom_launcher_ext_v1* ext = &core->launcher_exts[i];
            if (ext->on_build_canvas) {
                if (ext->on_build_canvas(core, inst, canvas_id, out)) {
                    return true;
                }
            }
        }
    }

    /* Unknown canvas: succeed with empty buffer */
    return true;
}
