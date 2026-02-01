Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Threat Model (TESTX2)





Status: binding.


Scope: control layers and hostile environments.





## Assumptions


- Engine/game must assume hostile clients by default.


- Control policy is external and untrusted by default.


- Replay verification must remain intact regardless of control layers.





## Threats


1) Hostile client


   - May tamper with local state, inputs, or binaries.


   - Expected outcome: refusal, disconnect, or quarantine.


   - Must never corrupt authoritative state or alter ordering.





2) Malicious mod


   - May attempt to bypass law or capability gates.


   - Expected outcome: refusal and audit logging.


   - Must not change deterministic outcomes.





3) Compromised OS


   - May alter runtime environment or hooks.


   - Expected outcome: denial of access or isolation.


   - Must not inject nondeterminism into simulation.





4) Dishonest server operator


   - May attempt to alter authority policy.


   - Expected outcome: audit detection, refusal for invalid claims.


   - Must not rewrite archival history.





5) Replay forgery


   - May attempt to produce falsified replay artifacts.


   - Expected outcome: verification failure with explicit reason.





## Non-interference enforcement


Control responses are limited to access/connectivity gating. They never alter


simulation results. See `docs/architecture/NON_INTERFERENCE.md`.
