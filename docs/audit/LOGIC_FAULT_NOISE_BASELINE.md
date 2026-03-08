# LOGIC-8 Fault / Noise / Security Baseline

Status: in progress

## Fault Semantics

- placeholder

## Noise Policies

- placeholder

## EMI Coupling Stubs

- placeholder

## Security Hooks

- protocol-link security is enforced from LOGIC SENSE using `security_policy_id` on incoming `protocol_link` edges
- `sec.none`, `sec.auth_required_stub`, and `sec.encrypted_required_stub` are the declared baseline policies
- failed verification records deterministic `logic_security_fail_rows` and emits `explain.logic_spoof_detected`

## Safety Integration

- fault application can emit deterministic `safety_event_rows` during SENSE when a fault policy declares isolation or shutdown behavior
- session-runtime integration merges those rows into the authoritative safety event stream instead of bypassing SYS or watchdog governance

## Readiness

- placeholder
