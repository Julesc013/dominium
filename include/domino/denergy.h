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
