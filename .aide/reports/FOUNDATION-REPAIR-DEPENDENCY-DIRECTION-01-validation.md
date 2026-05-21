Status: DERIVED
Last Reviewed: 2026-05-21
Task: FOUNDATION-REPAIR-DEPENDENCY-DIRECTION-01
Result: PASS

# Validation

Dependency-direction strict:

- PASS: `0` violations, `68` warnings, `16579` files scanned.

AIDE:

- PASS: doctor.
- PASS: validate, with known review packet reference warnings.
- PASS: test.
- PASS: selftest.
- PASS: tools validate.
- PASS: roots validate.
- PASS: repo validate.

Standalone validators:

- PASS: repo layout, root allowlist, distribution layout, component matrices.
- PASS: public surface.
- PASS: public headers, with `2851` stable-promotion warnings.
- PASS: command, diagnostics, artifact, schema/protocol, capability/refusal, provider, module, Workbench workspace, app descriptor, replacement, version/deprecation, mod/pack trust, and portability validators.
- PASS: docs sanity, build target boundaries, UI shell purity, ABI boundaries.
- PASS: RepoX STRICT, with `INV-AUDITX-OUTPUT-STALE` warning.

FAST strict:

- PASS: `32` commands in `312.147` seconds.
- CMake configure/build: PASS through FAST strict.
- Smoke CTest: PASS through FAST strict.

Not run:

- Full CTest. It remains T4/full-gate debt.
