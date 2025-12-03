#include "dom_sim_ecs.h"
#include <string.h>

static dom_u32 g_entity_count = 0;
static dom_entity_id g_entities[DOM_ECS_MAX_ENTITIES];
static dom_u32 g_generations[DOM_ECS_MAX_ENTITIES];
static dom_bool8 g_alive[DOM_ECS_MAX_ENTITIES];

static DomComponentInfo g_components[DOM_ECS_MAX_COMPONENTS];
static dom_u32 g_component_count = 0;

dom_err_t dom_sim_ecs_init(void)
{
    g_entity_count = 0;
    memset(g_entities, 0, sizeof(g_entities));
    memset(g_generations, 0, sizeof(g_generations));
    memset(g_alive, 0, sizeof(g_alive));
    g_component_count = 0;
    memset(g_components, 0, sizeof(g_components));
    return DOM_OK;
}

DomComponentId dom_sim_ecs_register_component(const DomComponentInfo *info)
{
    DomComponentId id;
    if (!info) return 0;
    if (g_component_count >= DOM_ECS_MAX_COMPONENTS) return 0;
    id = (DomComponentId)(g_component_count + 1);
    g_components[g_component_count] = *info;
    g_components[g_component_count].id = id;
    g_component_count++;
    return id;
}

dom_entity_id dom_sim_ecs_create_entity(void)
{
    dom_u32 idx;
    if (g_entity_count >= DOM_ECS_MAX_ENTITIES) return 0;
    idx = g_entity_count;
    g_entities[idx] = dom_entity_make(idx, g_generations[idx]);
    g_alive[idx] = 1;
    g_entity_count++;
    return g_entities[idx];
}

void dom_sim_ecs_destroy_entity(dom_entity_id e)
{
    dom_u32 idx = dom_entity_index(e);
    if (idx >= DOM_ECS_MAX_ENTITIES) return;
    if (!g_alive[idx]) return;
    g_alive[idx] = 0;
    g_generations[idx] += 1;
    /* compact active list deterministically */
    {
        dom_u32 i;
        for (i = 0; i < g_entity_count; ++i) {
            if (!g_alive[i]) {
                dom_u32 j;
                for (j = i + 1; j < g_entity_count; ++j) {
                    if (g_alive[j]) {
                        dom_entity_id tmp = g_entities[i];
                        g_entities[i] = g_entities[j];
                        g_entities[j] = tmp;
                        g_alive[i] = 1;
                        g_alive[j] = 0;
                        break;
                    }
                }
            }
        }
        while (g_entity_count > 0 && !g_alive[g_entity_count - 1]) {
            g_entity_count--;
        }
    }
}

dom_bool8 dom_sim_ecs_is_alive(dom_entity_id e)
{
    dom_u32 idx = dom_entity_index(e);
    return (idx < DOM_ECS_MAX_ENTITIES) ? g_alive[idx] : 0;
}

dom_u32 dom_sim_ecs_active_count(void)
{
    return g_entity_count;
}

dom_entity_id dom_sim_ecs_active_at(dom_u32 index)
{
    if (index >= g_entity_count) return 0;
    return g_entities[index];
}
