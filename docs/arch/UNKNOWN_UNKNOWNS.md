# Unknown Unknowns (FUTURE0)

Status: binding.
Scope: how new paradigms are absorbed without architectural refactor.

When encountering new hardware, network paradigms, or gameplay genres, the
project follows a fixed rule:

If it changes how work executes, add a backend.  
If it changes what exists, add data and contracts.  
If it changes who may act, add law and capabilities.

## Examples
- New accelerators (NPU, FPGA, GPU clusters): implement a backend for Work IR.
- New networking paradigms: implement transport/backpressure adapters only.
- New genres: express rules as data and contracts; no new execution model.
- New AI integration: advisory or derived layers only; no authority bypass.

## Anti-refactor stance
Never rewrite core logic to chase trends. Add adapters, backends, or data
extensions that preserve deterministic and law-gated behavior.

## See also
- `docs/arch/FUTURE_PROOFING.md`
- `docs/arch/EXECUTION_MODEL.md`
