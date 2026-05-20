# DIAGNOSTIC-CODE-REGISTRY-01 Initial Diagnostic Inventory

Starting HEAD: `3fa25f5e20464e5b31fc138bd0bd704b7c6cd677`

## Inspected Surfaces

| Candidate | Location | Owner | Severity/Category Guess | Register Now | Notes |
| --- | --- | --- | --- | --- | --- |
| Repo layout violation | `contracts/repo/layout.contract.toml`, repo validators | `tools.repo` | error/repo | yes | Foundational structural failure. |
| Forbidden root | `contracts/repo/root_allowlist.toml`, root validators | `tools.repo` | error/repo | yes | Normal gate condition. |
| Dependency-direction violation | `contracts/repo/dependency_directions.contract.toml` | `tools.repo` | error/dependency | yes | Existing debt remains visible. |
| Public-header ABI violation | `contracts/abi/c_api.contract.toml` | `tools.abi` | error/abi | yes | ABI canon validator condition. |
| Public-surface invalid | `contracts/public_surface/public_surface.contract.toml` | `tools.repo` | error/validation | yes | Registry validation condition. |
| Command invalid input | `contracts/command/command_surface.contract.toml` | `contracts.command` | error/command | yes | Tied to command refusal scaffold. |
| Command unsupported surface | `contracts/command/command_surface.contract.toml` | `contracts.command` | error/command | yes | Tied to command refusal scaffold. |
| Capability missing | `contracts/refusal/refusal_code.registry.json` | `contracts.capability` | error/capability | yes | Provisional until capability/refusal law. |
| Package invalid manifest | package/content validators and docs | `runtime.package` | error/package | yes | Foundational pack/setup condition, no runtime behavior implemented. |
| Schema unsupported version | schema/protocol docs | `contracts.schema` | error/schema | yes | Foundational compatibility condition. |
| Evidence missing | AIDE reports, command/evidence schemas | `tools.validation` | warning/validation | yes | Proof-loop condition. |
| Full gate debt | fast strict and full-gate reports | `tools.test` | warning/test | yes | Records T4 full/release debt without hiding it. |
| AIDE task blocked | AIDE reports/status docs | `tools.aide` | error/aide | yes | Task/evidence condition, not product authority. |
| Release promotion blocked | release docs/proof reports | `release` | error/release | yes | Release gate condition, no release publication. |

## Deferred

- Runtime diagnostic dispatch conditions are deferred until runtime/service work.
- Workbench presentation diagnostics are deferred until Workbench validation
  slices.
- Detailed capability/refusal diagnostics are deferred until
  `CAPABILITY-REFUSAL-LAW-01`.
- Artifact identity diagnostics are deferred until `ARTIFACT-IDENTITY-LAW-01`.
