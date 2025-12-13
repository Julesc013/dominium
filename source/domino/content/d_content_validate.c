#include <stdio.h>
#include <string.h>

#include "content/d_content.h"

static int d_content_validate_utf8(const char *s) {
    const unsigned char *p = (const unsigned char *)s;
    if (!p) {
        return 0;
    }
    while (*p) {
        unsigned char c = *p++;
        if (c < 0x20 && c != '\t' && c != '\n' && c != '\r') {
            return 0;
        }
        if (c < 0x80) {
            continue;
        }
        if ((c & 0xE0u) == 0xC0u) {
            if ((*p & 0xC0u) != 0x80u) return 0;
            p += 1;
        } else if ((c & 0xF0u) == 0xE0u) {
            if ((*p & 0xC0u) != 0x80u) return 0;
            if ((*(p + 1) & 0xC0u) != 0x80u) return 0;
            p += 2;
        } else {
            return 0;
        }
    }
    return 1;
}

static int validate_name(const char *name) {
    if (!name || name[0] == '\0') {
        return 0;
    }
    return d_content_validate_utf8(name);
}

static int validate_materials(void) {
    u32 count = d_content_material_count();
    u32 i;
    for (i = 0u; i < count; ++i) {
        const d_proto_material *m = d_content_get_material_by_index(i);
        if (!m || m->id == 0u || !validate_name(m->name)) {
            fprintf(stderr, "content validate: invalid material #%u\n", (unsigned)i);
            return -1;
        }
        if (m->permeability < 0 || m->permeability > d_q16_16_from_int(1)) {
            fprintf(stderr, "content validate: material %u permeability out of range\n", (unsigned)m->id);
            return -1;
        }
        if (m->porosity < 0 || m->porosity > d_q16_16_from_int(1)) {
            fprintf(stderr, "content validate: material %u porosity out of range\n", (unsigned)m->id);
            return -1;
        }
        if (m->thermal_conductivity < 0) {
            fprintf(stderr, "content validate: material %u thermal_conductivity negative\n", (unsigned)m->id);
            return -1;
        }
        if (m->erosion_resistance < 0) {
            fprintf(stderr, "content validate: material %u erosion_resistance negative\n", (unsigned)m->id);
            return -1;
        }
    }
    return 0;
}

static int validate_items(void) {
    u32 count = d_content_item_count();
    u32 i;
    for (i = 0u; i < count; ++i) {
        const d_proto_item *it = d_content_get_item_by_index(i);
        if (!it || it->id == 0u || !validate_name(it->name)) {
            fprintf(stderr, "content validate: invalid item #%u\n", (unsigned)i);
            return -1;
        }
        if (it->material_id != 0u && !d_content_get_material(it->material_id)) {
            fprintf(stderr, "content validate: item %u references missing material %u\n",
                    (unsigned)it->id, (unsigned)it->material_id);
            return -1;
        }
    }
    return 0;
}

static int validate_deposits(void) {
    u32 count = d_content_deposit_count();
    u32 i;
    for (i = 0u; i < count; ++i) {
        const d_proto_deposit *dep = d_content_get_deposit_by_index(i);
        if (!dep || dep->id == 0u || !validate_name(dep->name)) {
            fprintf(stderr, "content validate: invalid deposit #%u\n", (unsigned)i);
            return -1;
        }
        if (dep->material_id != 0u && !d_content_get_material(dep->material_id)) {
            fprintf(stderr, "content validate: deposit %u references missing material %u\n",
                    (unsigned)dep->id, (unsigned)dep->material_id);
            return -1;
        }
    }
    return 0;
}

static int validate_structures(void) {
    u32 count = d_content_structure_count();
    u32 i;
    for (i = 0u; i < count; ++i) {
        const d_proto_structure *st = d_content_get_structure_by_index(i);
        if (!st || st->id == 0u || !validate_name(st->name)) {
            fprintf(stderr, "content validate: invalid structure #%u\n", (unsigned)i);
            return -1;
        }
    }
    return 0;
}

static int validate_processes(void) {
    u32 count = d_content_process_count();
    u32 i;
    for (i = 0u; i < count; ++i) {
        const d_proto_process *p = d_content_get_process_by_index(i);
        if (!p || p->id == 0u || !validate_name(p->name)) {
            fprintf(stderr, "content validate: invalid process #%u\n", (unsigned)i);
            return -1;
        }
    }
    return 0;
}

static int validate_containers(void) {
    u32 count = d_content_container_count();
    u32 i;
    for (i = 0u; i < count; ++i) {
        const d_proto_container *c = d_content_get_container_by_index(i);
        if (!c || c->id == 0u || !validate_name(c->name)) {
            fprintf(stderr, "content validate: invalid container #%u\n", (unsigned)i);
            return -1;
        }
        if (c->max_volume < 0 || c->max_mass < 0) {
            fprintf(stderr, "content validate: container %u has negative limits\n", (unsigned)c->id);
            return -1;
        }
    }
    return 0;
}

static int validate_spline_profiles(void) {
    u32 count = d_content_spline_profile_count();
    u32 i;
    for (i = 0u; i < count; ++i) {
        const d_proto_spline_profile *sp = d_content_get_spline_profile_by_index(i);
        if (!sp || sp->id == 0u || !validate_name(sp->name)) {
            fprintf(stderr, "content validate: invalid spline profile #%u\n", (unsigned)i);
            return -1;
        }
        if (sp->base_speed < 0 || sp->max_grade < 0 || sp->capacity < 0) {
            fprintf(stderr, "content validate: spline profile %u has negative fields\n", (unsigned)sp->id);
            return -1;
        }
    }
    return 0;
}

static int validate_blueprints(void) {
    u32 count = d_content_blueprint_count();
    u32 i;
    for (i = 0u; i < count; ++i) {
        const d_proto_blueprint *bp = d_content_get_blueprint_by_index(i);
        if (!bp || bp->id == 0u || !validate_name(bp->name)) {
            fprintf(stderr, "content validate: invalid blueprint #%u\n", (unsigned)i);
            return -1;
        }
    }
    return 0;
}

int d_content_validate_all(void) {
    if (validate_materials() != 0) return -1;
    if (validate_items() != 0) return -1;
    if (validate_containers() != 0) return -1;
    if (validate_processes() != 0) return -1;
    if (validate_deposits() != 0) return -1;
    if (validate_structures() != 0) return -1;
    if (validate_spline_profiles() != 0) return -1;
    if (validate_blueprints() != 0) return -1;
    return 0;
}
