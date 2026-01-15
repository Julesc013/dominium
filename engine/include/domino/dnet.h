/*
FILE: include/domino/dnet.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / dnet
RESPONSIBILITY: Defines the public contract for `dnet` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_DNET_H
#define DOMINO_DNET_H

#include "dnumeric.h"

#ifdef __cplusplus
extern "C" {
#endif

/* NetNodeId: Identifier type for Net Node objects in `dnet`. */
typedef uint32_t NetNodeId;
/* NetEdgeId: Identifier type for Net Edge objects in `dnet`. */
typedef uint32_t NetEdgeId;

/* NetKind: Enumeration/classifier for Net in `dnet`. */
typedef enum {
    NET_POWER = 0,
    NET_FLUID,
    NET_GAS,
    NET_HEAT,
    NET_SIGNAL,
    NET_DATA,
    NET_COMM,
} NetKind;

/* NetNode: Public type used by `dnet`. */
typedef struct {
    NetNodeId id;
    NetKind   kind;
} NetNode;

/* PowerEdge: Public type used by `dnet`. */
typedef struct {
    NetEdgeId id;
    NetNodeId a, b;
    PowerW    capacity;
    Q16_16    loss_factor_0_1;
    PowerW    flow;
} PowerEdge;

/* FluidEdge: Public type used by `dnet`. */
typedef struct {
    NetEdgeId id;
    NetNodeId a, b;
    VolM3     capacity_per_s;
    Q16_16    friction_factor;
    VolM3     flow_per_s;
} FluidEdge;

/* GasEdge: Public type used by `dnet`. */
typedef struct {
    NetEdgeId id;
    NetNodeId a, b;
    VolM3     capacity_per_s;
    Q16_16    friction_factor;
    VolM3     flow_per_s;
} GasEdge;

/* HeatEdge: Public type used by `dnet`. */
typedef struct {
    NetEdgeId id;
    NetNodeId a, b;
    EnergyJ   capacity;
    Q16_16    conductance;
    EnergyJ   transfer;
} HeatEdge;

/* SignalEdge: Public type used by `dnet`. */
typedef struct {
    NetEdgeId id;
    NetNodeId a, b;
    SecondsQ16 latency_s;
    Q16_16     bandwidth_bps; /* simplified; scaled */
    Q16_16     reliability_0_1;
} SignalEdge;

/* DataEdge: Public type used by `dnet`. */
typedef SignalEdge DataEdge;
/* CommEdge: Public type used by `dnet`. */
typedef SignalEdge CommEdge;

/* Purpose: Register node.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: Id value (0 is commonly used as the invalid/failure sentinel for `*Id` typedefs).
 */
NetNodeId dnet_register_node(NetKind kind);

/* Purpose: Register power edge.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: Id value (0 is commonly used as the invalid/failure sentinel for `*Id` typedefs).
 */
NetEdgeId dnet_register_power_edge(const PowerEdge *def);
/* Purpose: Register fluid edge.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: Id value (0 is commonly used as the invalid/failure sentinel for `*Id` typedefs).
 */
NetEdgeId dnet_register_fluid_edge(const FluidEdge *def);
/* Purpose: Register gas edge.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: Id value (0 is commonly used as the invalid/failure sentinel for `*Id` typedefs).
 */
NetEdgeId dnet_register_gas_edge(const GasEdge *def);
/* Purpose: Register heat edge.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: Id value (0 is commonly used as the invalid/failure sentinel for `*Id` typedefs).
 */
NetEdgeId dnet_register_heat_edge(const HeatEdge *def);
/* Purpose: Register signal edge.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: Id value (0 is commonly used as the invalid/failure sentinel for `*Id` typedefs).
 */
NetEdgeId dnet_register_signal_edge(const SignalEdge *def);
/* Purpose: Register data edge.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: Id value (0 is commonly used as the invalid/failure sentinel for `*Id` typedefs).
 */
NetEdgeId dnet_register_data_edge(const DataEdge *def);
/* Purpose: Register comm edge.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: Id value (0 is commonly used as the invalid/failure sentinel for `*Id` typedefs).
 */
NetEdgeId dnet_register_comm_edge(const CommEdge *def);

/* Purpose: Get node.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: Non-NULL on success; NULL on failure or when not found.
 */
const NetNode   *dnet_get_node(NetNodeId id);
/* Purpose: Get power edge.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: Non-NULL on success; NULL on failure or when not found.
 */
const PowerEdge *dnet_get_power_edge(NetEdgeId id);
/* Purpose: Get fluid edge.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: Non-NULL on success; NULL on failure or when not found.
 */
const FluidEdge *dnet_get_fluid_edge(NetEdgeId id);
/* Purpose: Get gas edge.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: Non-NULL on success; NULL on failure or when not found.
 */
const GasEdge   *dnet_get_gas_edge(NetEdgeId id);
/* Purpose: Get heat edge.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: Non-NULL on success; NULL on failure or when not found.
 */
const HeatEdge  *dnet_get_heat_edge(NetEdgeId id);
/* Purpose: Get signal edge.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: Non-NULL on success; NULL on failure or when not found.
 */
const SignalEdge *dnet_get_signal_edge(NetEdgeId id);
/* Purpose: Get data edge.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: Non-NULL on success; NULL on failure or when not found.
 */
const DataEdge   *dnet_get_data_edge(NetEdgeId id);
/* Purpose: Get comm edge.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: Non-NULL on success; NULL on failure or when not found.
 */
const CommEdge   *dnet_get_comm_edge(NetEdgeId id);

/* Purpose: Power step.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: `true` on success; `false` on failure.
 */
bool dnet_power_step(U32 ticks);
/* Purpose: Fluid step.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: `true` on success; `false` on failure.
 */
bool dnet_fluid_step(U32 ticks);
/* Purpose: Gas step.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: `true` on success; `false` on failure.
 */
bool dnet_gas_step(U32 ticks);
/* Purpose: Heat step.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: `true` on success; `false` on failure.
 */
bool dnet_heat_step(U32 ticks);
/* Purpose: Signal step.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: `true` on success; `false` on failure.
 */
bool dnet_signal_step(U32 ticks);
/* Purpose: Data step.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: `true` on success; `false` on failure.
 */
bool dnet_data_step(U32 ticks);
/* Purpose: Comm step.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: `true` on success; `false` on failure.
 */
bool dnet_comm_step(U32 ticks);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_DNET_H */
