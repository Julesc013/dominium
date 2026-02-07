# Code Change Justification

Touched: game/, tests/, docs/, CMakeLists.txt

Why can this not be data?
The changes touch authoritative runtime behavior and build/test enforcement
(stub refusals, header-compile include paths, TestX gate timeout). These are
code and build-system concerns that cannot be represented as data-only packs.

Summary:
- Replace forbidden runtime stubs with explicit refusal paths and tests.
- Align public header compile checks with engine include visibility for game headers.
- Add deterministic TestX gate timeout and documentation.
