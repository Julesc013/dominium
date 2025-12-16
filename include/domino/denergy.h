/*
FILE: include/domino/denergy.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / denergy
RESPONSIBILITY: Defines the public contract for `denergy` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_DENERGY_H
#define DOMINO_DENERGY_H

#include "dnumeric.h"
#include "daggregate.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef Q16_16 VoltageV;

typedef struct {
    EnergyJ capacity;
    EnergyJ stored;
    VoltageV nominal_voltage;
} Battery;

typedef struct {
    ChargeC capacity;
    ChargeC stored;
    VoltageV nominal_voltage;
} Capacitor;

EnergyJ denergy_from_charge(ChargeC q, VoltageV voltage);
ChargeC denergy_to_charge(EnergyJ e, VoltageV voltage);

/* Stub power interfaces */
PowerW denergy_request_power(AggregateId agg, PowerW desired);
void   denergy_report_consumption(AggregateId agg, PowerW consumed);
void   denergy_report_generation(AggregateId agg, PowerW produced);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_DENERGY_H */
