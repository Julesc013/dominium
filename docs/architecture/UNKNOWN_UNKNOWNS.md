Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Unknown Unknowns (FUTURE0)





Status: binding.


Scope: how new paradigms are absorbed without architectural refactor.





When encountering new hardware, network paradigms, or gameplay genres, the


project follows a fixed rule:





If it changes how work executes, add a backend.  


If it changes what exists, add data and contracts.  


If it changes who may act, add law and capabilities.





## Invariants


- Deterministic execution is mandatory for authoritative work.


- Law and capability gates remain the only path to authority.


- Data and contracts define what exists.





## Examples


- New accelerators (NPU, FPGA, GPU clusters): implement a backend for Work IR.


- New networking paradigms: implement transport/backpressure adapters only.


- New genres: express rules as data and contracts; no new execution model.


- New AI integration: advisory or derived layers only; no authority bypass.





## Forbidden assumptions


- Never rewrite core logic to chase trends.


- Never bypass law or audit to integrate new paradigms.


- Never trade determinism for convenience.





## Dependencies


- Execution model: `docs/architecture/EXECUTION_MODEL.md`


- Canon and invariants: `docs/architecture/INVARIANTS.md`





## See also


- `docs/architecture/FUTURE_PROOFING.md`


- `docs/architecture/EXECUTION_MODEL.md`
