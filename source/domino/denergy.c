/*
FILE: source/domino/denergy.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / denergy
RESPONSIBILITY: Implements `denergy`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "domino/denergy.h"

static PowerW denergy_clamp_power(PowerW p)
{
    return p;
}

EnergyJ denergy_from_charge(ChargeC q, VoltageV voltage)
{
    return (EnergyJ)(((I64)q * (I64)voltage) >> 16);
}

ChargeC denergy_to_charge(EnergyJ e, VoltageV voltage)
{
    if (voltage == 0) return 0;
    return (ChargeC)(((I64)e << 16) / (I64)voltage);
}

PowerW denergy_request_power(AggregateId agg, PowerW desired)
{
    (void)agg;
    return denergy_clamp_power(desired);
}

void denergy_report_consumption(AggregateId agg, PowerW consumed)
{
    (void)agg;
    (void)consumed;
}

void denergy_report_generation(AggregateId agg, PowerW produced)
{
    (void)agg;
    (void)produced;
}
