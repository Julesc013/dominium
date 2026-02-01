/*
FILE: include/domino/denergy.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / denergy
RESPONSIBILITY: Defines the public contract for `denergy` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/specs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_DENERGY_H
#define DOMINO_DENERGY_H

#include "dnumeric.h"
#include "daggregate.h"

#ifdef __cplusplus
extern "C" {
#endif

/* VoltageV: Public type used by `denergy`. */
typedef Q16_16 VoltageV;

/* Battery: Public type used by `denergy`. */
typedef struct {
    EnergyJ capacity;
    EnergyJ stored;
    VoltageV nominal_voltage;
} Battery;

/* Capacitor: Public type used by `denergy`. */
typedef struct {
    ChargeC capacity;
    ChargeC stored;
    VoltageV nominal_voltage;
} Capacitor;

/* Purpose: From charge.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/specs/CONTRACTS.md#Return Values / Errors`.
 */
EnergyJ denergy_from_charge(ChargeC q, VoltageV voltage);
/* Purpose: To charge.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/specs/CONTRACTS.md#Return Values / Errors`.
 */
ChargeC denergy_to_charge(EnergyJ e, VoltageV voltage);

/* Stub power interfaces */
PowerW denergy_request_power(AggregateId agg, PowerW desired);
/* Purpose: Report consumption.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 */
void   denergy_report_consumption(AggregateId agg, PowerW consumed);
/* Purpose: Report generation.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 */
void   denergy_report_generation(AggregateId agg, PowerW produced);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_DENERGY_H */
