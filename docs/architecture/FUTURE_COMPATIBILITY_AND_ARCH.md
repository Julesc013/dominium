Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Future Compatibility and Architecture Targets (REPOX)





Status: binding.


Scope: architecture identifiers, portability rules, and support levels.





## Architecture identifiers


Canonical IDs (extensible):


- x86_16


- x86_32


- x86_64


- arm32


- arm64


- ppc


- ppc64


- mips32 (optional)


- riscv64 (optional)


- s390x (optional)





## Endianness and word size


- Endianness must be explicit in serialization formats.


- Word size assumptions must be documented per target.


- Serialization must be portable across 32/64-bit boundaries.





## Alignment and packing


- Struct layout expectations must be validated by portability tests.


- Packing assumptions are never implicit; use explicit serialization.


- ABI boundaries use stable C types only.





## Support levels


Define support in three tiers:


- CI-built: built and tested in CI.


- Buildable: known to build with documented toolchain.


- Best-effort: documented intent with no current CI coverage.





## Cross-compiling


- Use `DOM_TARGET_ARCH` to declare target architecture.


- Toolchain files live under `/cmake/toolchains/`.


- No auto-detection; explicit presets only.





## Cross-references


- `docs/architecture/IDE_AND_TOOLCHAIN_POLICY.md`


- `docs/architecture/PROJECTION_LIFECYCLE.md`
