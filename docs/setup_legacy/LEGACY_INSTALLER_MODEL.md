# Legacy Installer Model (Tiered)

This document defines the legacy installer tier used for constrained OS targets.
Legacy installers must still emit a `dsu_invocation` and produce installed-state
compatible with the launcher, but they operate under a reduced capability set.

## Legacy mode flag

`dsu_invocation.policy_flags.legacy_mode` indicates legacy constraints.

When `legacy_mode` is true:

- Setup Core uses the legacy profile (build-time).
- A reduced operation set is enforced.
- Unsupported actions are rejected deterministically.

## Allowed operations (legacy_mode)

Allowed:

- `install`
- `uninstall`

Rejected:

- `upgrade`
- `repair`

Rejection must be deterministic with a stable error:

- `Legacy mode does not support this operation.`

Frontends may expose "repair" or "upgrade" UI affordances, but they must map
to a legacy-safe action (for example, explicit reinstall) or be disabled.

Verification is supported via installed-state validation (`dominium-setup verify`)
and does not require an invocation operation.

## Legacy Setup Core profile (build-time)

The legacy profile is a build-time configuration of Setup Core that:

- disables legacy-incompatible features (journaling, platform registrations, or
  any OS API that is not available on the legacy target)
- preserves deterministic plan generation and installed-state writing
- maintains the same manifest and plan formats for compatibility

The legacy profile must be explicit and isolated from the modern profile.

## Installed-state compatibility

Legacy installers must write `installed_state.dsustate` using the same schema
as modern installs. This allows:

- launcher discovery and validation on modern platforms
- import into modern installs for repair/verify workflows

## Legacy frontends

Legacy frontends must:

- follow `docs/setup/INSTALLER_UX_CONTRACT.md`
- emit `dsu_invocation` with `legacy_mode=true`
- avoid any installer-side logic; Setup Core remains the authority

## See also

- `docs/setup/INVOCATION_PAYLOAD.md`
- `docs/setup/INSTALLER_UX_CONTRACT.md`
