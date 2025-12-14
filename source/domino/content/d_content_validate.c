#include <stdio.h>
#include <stdlib.h>
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

static int validate_research_nodes(void) {
    u32 count = d_content_research_count();
    u32 i;

    for (i = 0u; i < count; ++i) {
        const d_proto_research *r = d_content_get_research_by_index(i);
        u32 pi;
        if (!r || r->id == 0u || !validate_name(r->name)) {
            fprintf(stderr, "content validate: invalid research #%u\n", (unsigned)i);
            return -1;
        }
        if (r->prereq_count > 0u && !r->prereq_ids) {
            fprintf(stderr, "content validate: research %u has null prereq_ids\n", (unsigned)r->id);
            return -1;
        }
        for (pi = 0u; pi < (u32)r->prereq_count; ++pi) {
            d_research_id pid = r->prereq_ids[pi];
            if (pid == 0u) {
                fprintf(stderr, "content validate: research %u has zero prereq id\n", (unsigned)r->id);
                return -1;
            }
            if (pid == r->id) {
                fprintf(stderr, "content validate: research %u prereqs itself\n", (unsigned)r->id);
                return -1;
            }
            if (!d_content_get_research(pid)) {
                fprintf(stderr, "content validate: research %u references missing prereq %u\n",
                        (unsigned)r->id, (unsigned)pid);
                return -1;
            }
        }
    }

    /* Cycle detection (by id list, O(n^2) is fine for small counts). */
    if (count > 0u) {
        d_research_id *ids = (d_research_id *)malloc(sizeof(d_research_id) * count);
        unsigned char *state = (unsigned char *)malloc(sizeof(unsigned char) * count);
        if (!ids || !state) {
            if (ids) free(ids);
            if (state) free(state);
            fprintf(stderr, "content validate: research cycle check OOM\n");
            return -1;
        }
        memset(state, 0, sizeof(unsigned char) * count);

        for (i = 0u; i < count; ++i) {
            const d_proto_research *r = d_content_get_research_by_index(i);
            ids[i] = r ? r->id : 0u;
        }

        {
            u32 si;
            for (si = 0u; si < count; ++si) {
                u32 stack[128];
                u32 stack_top = 0u;

                if (state[si] != 0u) {
                    continue;
                }

                /* Iterative DFS with explicit stack of indices. */
                stack[stack_top++] = si;
                while (stack_top > 0u) {
                    u32 idx = stack[stack_top - 1u];
                    const d_proto_research *r;
                    u32 pi;

                    if (idx >= count) {
                        return -1;
                    }
                    if (state[idx] == 2u) {
                        stack_top -= 1u;
                        continue;
                    }
                    if (state[idx] == 0u) {
                        state[idx] = 1u; /* visiting */
                    }

                    r = d_content_get_research(ids[idx]);
                    if (!r) {
                        state[idx] = 2u;
                        stack_top -= 1u;
                        continue;
                    }

                    /* Expand prereqs; push first unvisited, otherwise finish. */
                    for (pi = 0u; pi < (u32)r->prereq_count; ++pi) {
                        d_research_id pid = r->prereq_ids[pi];
                        u32 pj;
                        for (pj = 0u; pj < count; ++pj) {
                            if (ids[pj] == pid) {
                                break;
                            }
                        }
                        if (pj >= count) {
                            continue;
                        }
                        if (state[pj] == 1u) {
                            fprintf(stderr, "content validate: research cycle detected at %u -> %u\n",
                                    (unsigned)r->id, (unsigned)pid);
                            free(ids);
                            free(state);
                            return -1;
                        }
                        if (state[pj] == 0u) {
                            if (stack_top < 128u) {
                                stack[stack_top++] = pj;
                                break;
                            }
                            /* Stack too deep: fall back to conservative failure. */
                            fprintf(stderr, "content validate: research graph too deep\n");
                            free(ids);
                            free(state);
                            return -1;
                        }
                    }

                    /* If we didn't push any new node, mark done and pop. */
                    if (pi == (u32)r->prereq_count) {
                        state[idx] = 2u;
                        stack_top -= 1u;
                    }
                }
            }
        }

        free(ids);
        free(state);
    }

    return 0;
}

static int validate_research_point_sources(void) {
    u32 count = d_content_research_point_source_count();
    u32 i;
    for (i = 0u; i < count; ++i) {
        const d_proto_research_point_source *s = d_content_get_research_point_source_by_index(i);
        if (!s || s->id == 0u || !validate_name(s->name)) {
            fprintf(stderr, "content validate: invalid research point source #%u\n", (unsigned)i);
            return -1;
        }
    }
    return 0;
}

static int validate_policy_rules(void) {
    u32 count = d_content_policy_rule_count();
    u32 i;
    for (i = 0u; i < count; ++i) {
        const d_proto_policy_rule *p = d_content_get_policy_rule_by_index(i);
        if (!p || p->id == 0u || !validate_name(p->name)) {
            fprintf(stderr, "content validate: invalid policy rule #%u\n", (unsigned)i);
            return -1;
        }
        if (p->scope.len > 0u && !p->scope.ptr) {
            fprintf(stderr, "content validate: policy %u has null scope blob\n", (unsigned)p->id);
            return -1;
        }
        if (p->scope.len == 0u) {
            fprintf(stderr, "content validate: policy %u has empty scope\n", (unsigned)p->id);
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
    if (validate_research_nodes() != 0) return -1;
    if (validate_research_point_sources() != 0) return -1;
    if (validate_policy_rules() != 0) return -1;
    return 0;
}
