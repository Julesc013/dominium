# Energy

- Types live in `include/domino/denergy.h`: `VoltageV` (Q16.16 volts), `Battery { capacity, stored, nominal_voltage }`, `Capacitor { capacity (ChargeC), stored, nominal_voltage }`.
- Conversions: `denergy_from_charge(q, voltage)` → `EnergyJ`; `denergy_to_charge(e, voltage)` → `ChargeC`. Integer/fixed-point only.
- Stub interfaces for machines: `denergy_request_power(agg, desired)` returns granted power (currently passthrough); `denergy_report_consumption/ generation` are hooks for accounting/telemetry.
- Integrations with networks: power network edges carry capacity and loss; generators/consumers will later bind to aggregates and networks via these stubs.
