# DOM-AIDE-02 Wrapper Plan

## Status

Status: `provisional_no_apply`

This plan creates a stable AIDE wrapper contract for the first low-risk
validator family. It is evidence and contract work only. It does not implement
new executable adapter code and does not enable execution of legacy tools.

## Selected Validator Family

Selected family: `aide_tool_wrapper_plan_validator`

Current AIDE command contract: `py -3 .aide/scripts/aide_lite.py tools validate`

Supporting evidence-generation commands already used by the baseline:

- `py -3 .aide/scripts/aide_lite.py tools classify`
- `py -3 .aide/scripts/aide_lite.py tools wrap-plan`

The selected validator checks AIDE-local tool inventory, classification,
wrap-plan, and adapter-map evidence. It verifies that discovered tools remain
non-executable, no-apply, not deletion-approved, not rename-approved, and not
migration-approved.

## Why AIDE Wraps Before Renaming

Dominium has useful existing validation surfaces: XStack, AuditX, RepoX, TestX,
BuildX-like build gates, CMake-driven checks, AIDE validators, root/layout
validators, and project-specific scripts. Some names and locations are legacy or
temporary, but the tools are still evidence assets.

Renaming or moving first would erase provenance and make future validation
harder to audit. AIDE wraps first so agents can preserve old names, classify
capabilities, prove side effects, adapt command surfaces, migrate references,
and only later retire old names with explicit review.

## Underlying Legacy/Current Tools

The selected family is current AIDE validator infrastructure, not a direct
legacy runtime tool invocation.

Evidence paths:

- `.aide/scripts/aide_lite.py`
- `.aide/policies/tool-absorption.yaml`
- `.aide/policies/tool-inventory.yaml`
- `.aide/policies/tool-fates.yaml`
- `.aide/policies/tool-wrapping.yaml`
- `.aide/policies/tool-risk.yaml`
- `.aide/policies/tool-capabilities.yaml`
- `.aide/tools/latest-tool-inventory.json`
- `.aide/tools/latest-tool-classification.json`
- `.aide/tools/latest-tool-wrap-plan.json`
- `.aide/tools/latest-tool-adapter-map.json`
- `.aide/tools/xstack-integration-contract.json`
- `.aide/tools/xstack-wrapper-registry.json`

## Preservation Rules

- Preserve XStack, AuditX, RepoX, TestX, BuildX-like surfaces, CMake validators,
  and all existing validators.
- Do not rename old tools before adapters exist.
- Do not delete or move old tools.
- Do not execute unknown tools.
- Treat old validator names as current evidence, not necessarily desired
  long-term architecture.
- Keep all wrapper implementation and promotion work review-gated.

## Execution Policy

Default policy:

- `execution_allowed = false`
- `apply_allowed = false`
- `network_allowed = false`
- `writes_allowed = false`
- `unknown_tools_allowed = false`
- `requires_human_promotion = true`

`tools validate` is safe to run as a validation command in this task because it
is already proven by Q51/Q53/DCHECK evidence and does not run discovered tools.
This DOM-AIDE-02 wrapper contract still keeps future wrapper execution disabled
until reviewed.

## Blockers

- 858 unknown tool candidates remain in the latest tool classification.
- 171 destructive, high, release, or security-risk candidates remain
  review-gated.
- Broad XStack FAST/FULL, full CTest, full eval, build, package, and release
  commands remain outside this task.
- Full eval remains timeout-prone locally.
- Repo validation still reports 1669 unknown file classifications.
- No move, salvage, or active path-alias map is approved or applied.
- Large `.aide/reports/file-quality-ledger.json` remains a tracked advisory
  warning.

## Safety Model

The selected validator family is low risk because it checks AIDE evidence and
policy files rather than running legacy validators. It has no network access, no
provider/model calls, no build output side effects, no package/release side
effects, and no product/runtime behavior effect.

Allowed inputs are the repo root and AIDE-local policy, schema, inventory,
classification, wrap-plan, and adapter-map files. Allowed outputs for this task
are `.aide/reports/**` and `.aide/tools/**` evidence only.

## Validation Plan

Required validation:

- `py -3 .aide/scripts/aide_lite.py doctor`
- `py -3 .aide/scripts/aide_lite.py validate`
- `py -3 .aide/scripts/aide_lite.py test`
- `py -3 .aide/scripts/aide_lite.py selftest`
- `py -3 .aide/scripts/aide_lite.py tools validate`
- `py -3 .aide/scripts/aide_lite.py tools classify`
- `py -3 .aide/scripts/aide_lite.py tools wrap-plan`
- `py -3 .aide/scripts/aide_lite.py roots validate`
- `py -3 .aide/scripts/aide_lite.py repo validate`
- `py -3 .aide/scripts/aide_lite.py xstack validate`
- `py -3 .aide/scripts/aide_lite.py xstack wrap-plan`
- `py -3 .aide/scripts/aide_lite.py commit check --latest`
- `git diff --check`
- `git status --short --branch`

Full eval, full FAST, full CTest, build, package, release, provider/model/API,
and unknown legacy commands remain skipped.

## Follow-Up Tasks

- `DOM-ROOT-02`: next root inventory/classification wave.
- `DOM-BUILD-01`: AIDE-controlled build/test proof, no build execution until
  scoped.
- `DOM-ROOT-03`: first salvage map planning wave, no apply.
- Later wrapper implementation: enable one executable wrapper only after the
  command contract, side effects, outputs, timeout, and validation are reviewed.

## Agent Guidance

- Do not delete XStack/AuditX/RepoX/TestX.
- Do not rename tools before adapters exist.
- Do not execute unknown tools.
- Do not assume old names are desired long-term architecture.
- AIDE is the control plane; Dominium architecture remains Dominium architecture.
- Existing validators are evidence assets to recycle.
