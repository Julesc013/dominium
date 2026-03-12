Status: DERIVED
Last Reviewed: 2026-03-11
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# APPSHELL-1 Retro Audit

## Scope

APPSHELL-1 hardens the APPSHELL-0 bootstrap into a single registered command
surface with stable refusals, exit codes, and generated CLI documentation.

## Existing Command Surfaces

- `src/appshell/bootstrap.py` currently handled root commands through an ad hoc
  `_handle_root_command(...)` branch.
- `src/appshell/args_parser.py` only recognized a small hardcoded root-command
  set and did not support longest-prefix command paths such as `packs verify`
  or future namespaced product subcommands.
- `src/appshell/command_registry.py` generated descriptors in code rather than
  loading a canonical registry.
- `tools/setup/setup_cli.py`, `tools/launcher/launch.py`, and
  `src/server/server_main.py` still own product-specific legacy command trees
  behind AppShell bootstrap delegation.

## Naming And Overlap Risks

- `compat-status` in APPSHELL-0 was an alias to offline pack verification,
  which conflicts with CAP-NEG terminology where compatibility status should
  report negotiated modes and disabled capabilities.
- `profiles` and `packs` existed only as flat root commands, while the desired
  stable surface is namespaced: `profiles list/show`, `packs list/verify/build-lock`.
- Server console commands exist in `src/server/server_console.py` but are not
  part of the shared shell registry yet.

## Glossary / Deprecated-Term Audit

- No AppShell source scanned in this audit introduced deprecated glossary terms
  or legacy hardcoded mode-language.
- Shared refusal and command vocabulary is still using canon-safe terms:
  `compat`, `packs`, `profiles`, `descriptor`, `diag`, and `console`.

## Integration Decision

APPSHELL-1 should:

1. move command shape into `data/registries/command_registry.json`
2. keep `--help`, `--descriptor`, and `--version` stable
3. route runnable shared commands through a deterministic command engine
4. keep legacy product startup available only behind the AppShell boundary
5. make unavailable product namespaces explicit through registered placeholder
   command trees rather than silent omission
