Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Auditability and Disclosure (TESTX2)





Status: binding.


Scope: control capability discoverability and logging.





## Requirements


- `--build-info` must list enabled control capabilities.


- `--status` must report active control layers.


- Logs must record control decisions and reasons.


- No hidden enforcement paths are permitted.





## Output expectations


Build info must include:


- engine version


- game version


- build number


- protocol/schema versions


- enabled control capability IDs and keys





Status must include:


- active control layers (if any)


- refusal reasons when a capability is unavailable





## Determinism


Disclosure and logging must not mutate authoritative state or influence


ordering/timing. They are observational only.





## References


- `docs/architecture/CONTROL_LAYERS.md`


- `docs/architecture/NON_INTERFERENCE.md`
