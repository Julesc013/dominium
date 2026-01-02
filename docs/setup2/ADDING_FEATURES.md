# Adding Features to Setup2

## Required steps
1) Add TLV schema fields (optional, skip-unknown safe).
2) Update kernel validation and defaults.
3) Update planning rules and determinism constraints.
4) Update job DAG and transaction intents if required.
5) Emit audit fields/events for the new behavior.
6) Add unit + conformance tests.
7) Update documentation and CLI JSON schemas.
8) Update parity tests if contract markers change.

## Explicitly forbidden
- Adapter-side install logic.
- Hidden feature flags without audit visibility.
- Environment-dependent behavior in the kernel.
