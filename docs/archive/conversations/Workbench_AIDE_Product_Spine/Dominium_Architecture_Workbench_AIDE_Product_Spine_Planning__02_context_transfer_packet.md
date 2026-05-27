# Context Transfer Packet

### 29.1 Ultra-Condensed Bootstrap Brief

This chat developed and preserved the current Dominium architecture and task roadmap. Dominium is no longer being treated as a normal game project. The converged identity is: Domino is the reusable deterministic substrate, Dominium is the game/product family built on it, Workbench is the production/validation/editing/evidence environment, AIDE is the repo/control-plane harness, Codex is a bounded patch executor, contracts are law, and diagnostics/tests/replay/evidence are proof.

The core doctrines are: path is not identity; implementation is not contract; UI is not authority; generated output is not source truth; development should be non-blocking; promotion should be evidence-blocked. The project should be modular, deterministic, portable, extensible, replaceable, and evidence-backed.

Current expected state from this chat: Foundation Lock is `PASS_WITH_WARNINGS`, fast strict passes, dependency-direction strict has 0 violations with known warnings, full CTest remains T4/full-gate debt, and broad feature work remains blocked. `PACKAGE-MOUNT-SLICE-01` landed as `PASS_WITH_WARNINGS` and proved only a fixture-level package/profile mount decision, not runtime package mounting. The next intended product-spine task is `REPLAY-PROOF-SLICE-01`, followed by `BAREBONES-CLIENT-SHELL-01`, then `PRODUCT-SPINE-REVIEW-01`. Verify live repo state first, especially `.aide/queue/current.toml`, recent commits, and relevant audits.

Workbench should eventually be a visual and agentic production environment, but it is not authority. It edits documents and dispatches registered commands; runtime executes; contracts constrain; content packages; apps consume; tests prove. CLI, text/TUI, rendered GUI, native GUI, and headless must be projections of one command/result/refusal/document/view/action spine, not separate UI systems.

Future AIDE workflow: do not let agents all mutate shared `dev`. Use one task branch/worktree per prompt. AIDE integrates safe work into `origin/dev`; checkpoint branches prove integrated waves; `origin/main` receives only evidence-backed promotion. Limited parallel dev can start after replay proof, barebones client, and product-spine review. Large parallel dev should wait for `AIDE-WORKFLOW-LAW-01`, `AIDE-WORKUNIT-SCHEMA-01`, and `AIDE-DEV-MAIN-POLICY-01`.

### 29.2 Source Hierarchy

1. Direct user statements in this chat.
2. Explicit decisions accepted by the user.
3. Current task register.
4. Constraint register.
5. Artifact ledger.
6. Inferences.
7. Assistant suggestions not accepted by the user.
8. General model knowledge.

### 29.3 Operating Rules for Future Assistants

- Preserve FACT / INFERENCE / UNCERTAIN / PROJECT-CONTEXT labels.
- Verify live repo state before acting.
- Do not re-ask answered questions.
- Ask clarifying questions only when materially necessary.
- Do not invent missing details.
- Do not treat tentative items as final.
- Do not repeat rejected options.
- Preserve artifacts and warnings.
- Use structured outputs.
- Put future Codex prompts in one code block.
- Do not start broad feature work prematurely.

### 29.4 Active Workstreams

Active: product spine, AIDE workflow, Workbench platform, presentation architecture, package/replay/barebones product proof, repo governance.

Deferred: gameplay, renderer implementation, native GUI, runtime package/provider/module loaders, domain constitutions.

### 29.5 Current Priorities

1. Verify current repo state.
2. Run missing queue/replay/barebones prompts.
3. Run Product Spine Review.
4. Add minimum AIDE workflow law.
5. Begin limited parallel task-branch development.
6. Add presentation contracts.
7. Continue Workbench/runtime/product slices.

### 29.6 Current Open Questions

- Has replay proof run?
- Has barebones client shell run?
- Is queue reconciled?
- Does live build use C17/C++17?
- Does origin/dev exist?
- What warnings remain?

### 29.7 Recommended First Action

Inspect the live repo. Determine whether `REPLAY-PROOF-SLICE-01` and `BAREBONES-CLIENT-SHELL-01` have run. Generate the next missing prompt accordingly.