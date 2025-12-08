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
