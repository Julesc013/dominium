Status: CANONICAL
Last Reviewed: 2026-05-21
Supersedes: none
Superseded By: none
Stability: provisional

# Native Architecture Policy

Dominium mainline native products use the `source_native_64` architecture tier. The only mainline full-native architectures are `x86_64` and `arm64`, with 64-bit word size and little-endian execution.

The normative machine-readable policy is `contracts/platform/architecture_policy.contract.toml`. The tier registry is `contracts/platform/architecture_tier.registry.json`, and claims are validated by `tools/validators/platform/check_architecture_policy.py`.

## Tiers

`source_native_64` is the full native product tier. Support claims in this tier require architecture, word size, endian, ABI, toolchain, language floor, provider capability status, evidence, limitations, diagnostics, and refusals. A supported or release candidate full-native claim requires build, smoke, product, package, and release evidence.

`constrained_native_32` is an optional reduced native lane for 32-bit systems such as `x86` or `armv7`. It is not a mainline product obligation and must declare limitations and refusal behavior.

`contract_projection` is for replay viewers, snapshot clients, thin clients, generated subsets, data viewers, or similar compatibility projections. It is not native product support.

`archive_runner` is for VM, emulator, museum, historical, or research execution. It does not create normal support obligations.

## Mainline Rule

Full native products are source-native 64-bit. Legacy, vintage, and 32-bit targets may be researched or projected, but they do not govern the mainline build, runtime, renderer, Workbench, or product obligations.

The `x64` spelling remains a compatibility alias for `x86_64` in existing matrix rows. New policy surfaces should use `x86_64` unless they are preserving existing row identity.

## Support Claims

No platform, provider, product mode, package, or release row may claim full native support from a folder, preset, compiler installation, or host fact. Support is a row plus evidence.

Rows must state architecture tier, architecture, word size, endian policy, ABI, toolchain, language baseline, provider capabilities, limitations, diagnostics, refusals, and evidence appropriate to their status.

## Endian Rule

Mainline native execution is little-endian. Persisted and protocol formats use explicit little-endian encoders and decoders. Big-endian is unsupported unless a future projection or research lane declares explicit limitations and refusal behavior.

## Pointer Width Rule

Native pointer width is not simulation truth. It must not become artifact identity, replay truth, save truth, network truth, package truth, renderer-IR truth, or serialized domain law.

Stable data uses fixed-width types and explicit encoding. In-process implementation may use native types for local memory work, but those types cannot cross into stable contracts.

## Proof

Use:

```text
python tools/validators/platform/check_architecture_policy.py --repo-root . --strict
python tools/validators/platform/check_architecture_policy.py --repo-root . --fixtures
python tools/validators/platform/check_architecture_policy.py --repo-root . --inventory
```

Pointer-width inventory is descriptive. A deeper source audit belongs in a separate pointer-width serialization audit task.
