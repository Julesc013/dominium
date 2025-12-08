#ifndef DOMINO_DNET_H
#define DOMINO_DNET_H

#include <stdint.h>
#include <stdbool.h>

#include "dnumeric.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef uint32_t NetNodeId;
typedef uint32_t NetEdgeId;

typedef enum {
    NET_POWER = 0,
    NET_FLUID,
    NET_GAS,
    NET_HEAT,
    NET_SIGNAL,
    NET_DATA,
    NET_COMM,
} NetKind;

typedef struct {
    NetNodeId id;
    NetKind   kind;
} NetNode;

typedef struct {
    NetEdgeId id;
    NetNodeId a, b;
    PowerW    capacity;
    Q16_16    loss_factor_0_1;
    PowerW    flow;
} PowerEdge;

typedef struct {
    NetEdgeId id;
    NetNodeId a, b;
    VolM3     capacity_per_s;
    Q16_16    friction_factor;
    VolM3     flow_per_s;
} FluidEdge;

typedef struct {
    NetEdgeId id;
    NetNodeId a, b;
    VolM3     capacity_per_s;
    Q16_16    friction_factor;
    VolM3     flow_per_s;
} GasEdge;

typedef struct {
    NetEdgeId id;
    NetNodeId a, b;
    EnergyJ   capacity;
    Q16_16    conductance;
    EnergyJ   transfer;
} HeatEdge;

typedef struct {
    NetEdgeId id;
    NetNodeId a, b;
    SecondsQ16 latency_s;
    Q16_16     bandwidth_bps; /* simplified; scaled */
    Q16_16     reliability_0_1;
} SignalEdge;

typedef SignalEdge DataEdge;
typedef SignalEdge CommEdge;

NetNodeId dnet_register_node(NetKind kind);

NetEdgeId dnet_register_power_edge(const PowerEdge *def);
NetEdgeId dnet_register_fluid_edge(const FluidEdge *def);
NetEdgeId dnet_register_gas_edge(const GasEdge *def);
NetEdgeId dnet_register_heat_edge(const HeatEdge *def);
NetEdgeId dnet_register_signal_edge(const SignalEdge *def);
NetEdgeId dnet_register_data_edge(const DataEdge *def);
NetEdgeId dnet_register_comm_edge(const CommEdge *def);

const NetNode   *dnet_get_node(NetNodeId id);
const PowerEdge *dnet_get_power_edge(NetEdgeId id);
const FluidEdge *dnet_get_fluid_edge(NetEdgeId id);
const GasEdge   *dnet_get_gas_edge(NetEdgeId id);
const HeatEdge  *dnet_get_heat_edge(NetEdgeId id);
const SignalEdge *dnet_get_signal_edge(NetEdgeId id);
const DataEdge   *dnet_get_data_edge(NetEdgeId id);
const CommEdge   *dnet_get_comm_edge(NetEdgeId id);

bool dnet_power_step(U32 ticks);
bool dnet_fluid_step(U32 ticks);
bool dnet_gas_step(U32 ticks);
bool dnet_heat_step(U32 ticks);
bool dnet_signal_step(U32 ticks);
bool dnet_data_step(U32 ticks);
bool dnet_comm_step(U32 ticks);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_DNET_H */
