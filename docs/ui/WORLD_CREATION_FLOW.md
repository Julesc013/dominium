# World Creation Flow (P3)

Status: binding for P3. Applies to CLI, TUI, and GUI.

## Preconditions

- Built-in templates only. No packs are required.
- If no templates are available, creation is refused with an explicit reason.

## Inputs (Deterministic)

1. Template selection (built-in registry).
2. Seed selection (integer; user-controlled).
3. Profile selection:
   - casual, hardcore, creator
   - affects UI density/verbosity only (no simulation changes).
4. Meta-law preset selection:
   - baseline, strict, creator
   - applies policy sets for authority/mode/debug/playtest.
5. Policy toggles (per preset):
   - mode: free/orbit/surface
   - authority: policy.authority.shell
   - debug: policy.debug.readonly

## Execution (CLI Canonical)

- CLI command: `create-world` (or `new-world` + `save`).
- TUI/GUI wrap the same CLI intent.

Required behavior:

- Generate compatibility summary before creation.
- If compatibility is failed, refuse explicitly and do not create.
- Create a world using the selected template, seed, and policies.
- Automatically save a world artifact to the instance data_root.

## Output Artifact

- Save location: `{data_root}/saves/`
- Save naming: `world_<seed>.save` (auto-suffixed if already present).
- No silent overwrite; preserve existing saves.

## Result States

- Success: world is active, save exists, user enters World View.
- Refusal: reason is explicit; user remains in the wizard.

## Non-Goals

- No content-pack dependent templates.
- No gameplay mechanics or progression.
