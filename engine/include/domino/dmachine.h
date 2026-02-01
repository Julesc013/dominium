/*
FILE: include/domino/dmachine.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / dmachine
RESPONSIBILITY: Defines the public contract for `dmachine` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/specs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_DMACHINE_H
#define DOMINO_DMACHINE_H

#include "dnumeric.h"
#include "dmatter.h"
#include "dworld.h"
#include "daggregate.h"
#include "dnet.h"

#ifdef __cplusplus
extern "C" {
#endif

/* MachineTypeId: Identifier type for Machine Type objects in `dmachine`. */
typedef uint32_t MachineTypeId;
/* MachineId: Identifier type for Machine objects in `dmachine`. */
typedef uint32_t MachineId;

/* MachineFamily: Public type used by `dmachine`. */
typedef enum {
    MACH_FAMILY_GENERIC = 0,
    MACH_FAMILY_ASSEMBLER,
    MACH_FAMILY_SMELTER,
    MACH_FAMILY_REFINERY,
    MACH_FAMILY_PUMP,
    MACH_FAMILY_GENERATOR,
    MACH_FAMILY_BATTERY,
    MACH_FAMILY_LIFE_SUPPORT,
    MACH_FAMILY_LAB,
    MACH_FAMILY_THRUSTER,
    MACH_FAMILY_CUSTOM,
} MachineFamily;

/* MachinePortKind: Enumeration/classifier for Machine Port in `dmachine`. */
typedef enum {
    MACH_PORT_ITEM_IN = 0,
    MACH_PORT_ITEM_OUT,
    MACH_PORT_FLUID_IN,
    MACH_PORT_FLUID_OUT,
    MACH_PORT_GAS_IN,
    MACH_PORT_GAS_OUT,
    MACH_PORT_POWER_IN,
    MACH_PORT_POWER_OUT,
    MACH_PORT_HEAT_IN,
    MACH_PORT_HEAT_OUT,
    MACH_PORT_SIGNAL_IN,
    MACH_PORT_SIGNAL_OUT,
    MACH_PORT_DATA_IN,
    MACH_PORT_DATA_OUT,
} MachinePortKind;

/* MachinePortDesc: Public type used by `dmachine`. */
typedef struct {
    uint8_t         port_index;
    MachinePortKind kind;
    NetKind         net_kind;
    ItemTypeId      item_filter;
    SubstanceId     substance_filter;
} MachinePortDesc;

#define DMACH_MAX_PORTS 16

/* MachineType: Public type used by `dmachine`. */
typedef struct {
    MachineTypeId   id;
    const char     *name;

    MachineFamily   family;
    MaterialId      casing_material;

    PowerW          idle_power_W;
    PowerW          active_power_W;
    PowerW          max_power_W;

    uint8_t         port_count;
    MachinePortDesc ports[DMACH_MAX_PORTS];

    uint32_t        default_recipe_id;
} MachineType;

/* Machine: Public type used by `dmachine`. */
typedef struct Machine {
    MachineId     id;
    MachineTypeId type_id;

    AggregateId   agg;
    ElementId     element;

    Q16_16        progress_0_1;
    Q16_16        efficiency_0_1;
    Q16_16        health_0_1;

    uint32_t      recipe_id;

    PowerW        power_draw_W;
    PowerW        power_output_W;

    U32           flags;
} Machine;

/* Type registry */
MachineTypeId      dmachine_type_register(const MachineType *def);
/* Purpose: Get type.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: Non-NULL on success; NULL on failure or when not found.
 */
const MachineType *dmachine_type_get(MachineTypeId id);

/* Instances */
MachineId   dmachine_create(MachineTypeId type, AggregateId agg, ElementId element);
/* Purpose: Get dmachine.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: Non-NULL on success; NULL on failure or when not found.
 */
Machine    *dmachine_get(MachineId id);
/* Purpose: Destroy dmachine.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 */
void        dmachine_destroy(MachineId id);

/* Purpose: Tick dmachine.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 */
void        dmachine_tick(MachineId id, SimTick t);
/* Purpose: Tick all.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 */
void        dmachine_tick_all(SimTick t);

/* Purpose: Set recipe.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 */
void        dmachine_set_recipe(MachineId id, uint32_t recipe_id);
/* Purpose: Set enabled.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 */
void        dmachine_set_enabled(MachineId id, bool enabled);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_DMACHINE_H */
