/*
FILE: source/domino/dnet.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / dnet
RESPONSIBILITY: Implements `dnet`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "domino/dnet.h"

#include <string.h>
#include <stddef.h>

#define DNET_MAX_NODES   4096
#define DNET_MAX_EDGES   8192

static NetNode   g_nodes[DNET_MAX_NODES];
static NetNodeId g_node_count = 0;

static PowerEdge g_power_edges[DNET_MAX_EDGES];
static NetEdgeId g_power_count = 0;

static FluidEdge g_fluid_edges[DNET_MAX_EDGES];
static NetEdgeId g_fluid_count = 0;

static GasEdge   g_gas_edges[DNET_MAX_EDGES];
static NetEdgeId g_gas_count = 0;

static HeatEdge  g_heat_edges[DNET_MAX_EDGES];
static NetEdgeId g_heat_count = 0;

static SignalEdge g_signal_edges[DNET_MAX_EDGES];
static NetEdgeId  g_signal_count = 0;

static DataEdge g_data_edges[DNET_MAX_EDGES];
static NetEdgeId g_data_count = 0;

static CommEdge g_comm_edges[DNET_MAX_EDGES];
static NetEdgeId g_comm_count = 0;

static NetNodeId dnet_alloc_node(NetKind kind)
{
    if (g_node_count >= (NetNodeId)DNET_MAX_NODES) return 0;
    g_node_count++;
    g_nodes[g_node_count - 1].id = g_node_count;
    g_nodes[g_node_count - 1].kind = kind;
    return g_node_count;
}

NetNodeId dnet_register_node(NetKind kind)
{
    return dnet_alloc_node(kind);
}

static NetEdgeId dnet_alloc_edge(NetEdgeId *counter, void *storage, size_t element_size)
{
    NetEdgeId idx;
    if (!counter) return 0;
    if (*counter >= (NetEdgeId)DNET_MAX_EDGES) return 0;
    idx = ++(*counter);
    memset((char*)storage + (idx - 1) * element_size, 0, element_size);
    return idx;
}

NetEdgeId dnet_register_power_edge(const PowerEdge *def)
{
    NetEdgeId id = dnet_alloc_edge(&g_power_count, g_power_edges, sizeof(PowerEdge));
    if (id == 0 || !def) return 0;
    g_power_edges[id - 1] = *def;
    g_power_edges[id - 1].id = id;
    return id;
}

NetEdgeId dnet_register_fluid_edge(const FluidEdge *def)
{
    NetEdgeId id = dnet_alloc_edge(&g_fluid_count, g_fluid_edges, sizeof(FluidEdge));
    if (id == 0 || !def) return 0;
    g_fluid_edges[id - 1] = *def;
    g_fluid_edges[id - 1].id = id;
    return id;
}

NetEdgeId dnet_register_gas_edge(const GasEdge *def)
{
    NetEdgeId id = dnet_alloc_edge(&g_gas_count, g_gas_edges, sizeof(GasEdge));
    if (id == 0 || !def) return 0;
    g_gas_edges[id - 1] = *def;
    g_gas_edges[id - 1].id = id;
    return id;
}

NetEdgeId dnet_register_heat_edge(const HeatEdge *def)
{
    NetEdgeId id = dnet_alloc_edge(&g_heat_count, g_heat_edges, sizeof(HeatEdge));
    if (id == 0 || !def) return 0;
    g_heat_edges[id - 1] = *def;
    g_heat_edges[id - 1].id = id;
    return id;
}

NetEdgeId dnet_register_signal_edge(const SignalEdge *def)
{
    NetEdgeId id = dnet_alloc_edge(&g_signal_count, g_signal_edges, sizeof(SignalEdge));
    if (id == 0 || !def) return 0;
    g_signal_edges[id - 1] = *def;
    g_signal_edges[id - 1].id = id;
    return id;
}

NetEdgeId dnet_register_data_edge(const DataEdge *def)
{
    NetEdgeId id = dnet_alloc_edge(&g_data_count, g_data_edges, sizeof(DataEdge));
    if (id == 0 || !def) return 0;
    g_data_edges[id - 1] = *def;
    g_data_edges[id - 1].id = id;
    return id;
}

NetEdgeId dnet_register_comm_edge(const CommEdge *def)
{
    NetEdgeId id = dnet_alloc_edge(&g_comm_count, g_comm_edges, sizeof(CommEdge));
    if (id == 0 || !def) return 0;
    g_comm_edges[id - 1] = *def;
    g_comm_edges[id - 1].id = id;
    return id;
}

const NetNode *dnet_get_node(NetNodeId id)
{
    if (id == 0 || id > g_node_count) return 0;
    return &g_nodes[id - 1];
}

const PowerEdge *dnet_get_power_edge(NetEdgeId id)
{
    if (id == 0 || id > g_power_count) return 0;
    return &g_power_edges[id - 1];
}

const FluidEdge *dnet_get_fluid_edge(NetEdgeId id)
{
    if (id == 0 || id > g_fluid_count) return 0;
    return &g_fluid_edges[id - 1];
}

const GasEdge *dnet_get_gas_edge(NetEdgeId id)
{
    if (id == 0 || id > g_gas_count) return 0;
    return &g_gas_edges[id - 1];
}

const HeatEdge *dnet_get_heat_edge(NetEdgeId id)
{
    if (id == 0 || id > g_heat_count) return 0;
    return &g_heat_edges[id - 1];
}

const SignalEdge *dnet_get_signal_edge(NetEdgeId id)
{
    if (id == 0 || id > g_signal_count) return 0;
    return &g_signal_edges[id - 1];
}

const DataEdge *dnet_get_data_edge(NetEdgeId id)
{
    if (id == 0 || id > g_data_count) return 0;
    return &g_data_edges[id - 1];
}

const CommEdge *dnet_get_comm_edge(NetEdgeId id)
{
    if (id == 0 || id > g_comm_count) return 0;
    return &g_comm_edges[id - 1];
}

static Q16_16 dnet_mul_q16(Q16_16 a, Q16_16 b)
{
    return (Q16_16)(((I64)a * (I64)b) >> 16);
}

static Q48_16 dnet_mul_q48_q16(Q48_16 a, Q16_16 b)
{
    return (Q48_16)(((I64)a * (I64)b) >> 16);
}

bool dnet_power_step(U32 ticks)
{
    U32 i;
    for (i = 0; i < g_power_count; ++i) {
        PowerEdge *e = &g_power_edges[i];
        PowerW available = e->capacity;
        PowerW loss = dnet_mul_q48_q16(available, e->loss_factor_0_1);
        (void)ticks;
        if (loss > available) loss = available;
        e->flow = available - loss;
    }
    return true;
}

bool dnet_fluid_step(U32 ticks)
{
    U32 i;
    for (i = 0; i < g_fluid_count; ++i) {
        FluidEdge *e = &g_fluid_edges[i];
        (void)ticks;
        e->flow_per_s = e->capacity_per_s - dnet_mul_q48_q16(e->capacity_per_s, e->friction_factor);
    }
    return true;
}

bool dnet_gas_step(U32 ticks)
{
    U32 i;
    for (i = 0; i < g_gas_count; ++i) {
        GasEdge *e = &g_gas_edges[i];
        (void)ticks;
        e->flow_per_s = e->capacity_per_s - dnet_mul_q48_q16(e->capacity_per_s, e->friction_factor);
    }
    return true;
}

bool dnet_heat_step(U32 ticks)
{
    U32 i;
    for (i = 0; i < g_heat_count; ++i) {
        HeatEdge *e = &g_heat_edges[i];
        (void)ticks;
        e->transfer = dnet_mul_q48_q16(e->capacity, e->conductance);
    }
    return true;
}

bool dnet_signal_step(U32 ticks)
{
    (void)ticks;
    return true;
}

bool dnet_data_step(U32 ticks)
{
    (void)ticks;
    return true;
}

bool dnet_comm_step(U32 ticks)
{
    (void)ticks;
    return true;
}
