/*
FILE: include/dominium/_internal/dom_priv/dom_setup/dom_setup_config.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / _internal/dom_priv/dom_setup/dom_setup_config
RESPONSIBILITY: Defines the internal setup CLI contract (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/dominium/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Internal header; no ABI guarantees.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_SETUP_CONFIG_H
#define DOM_SETUP_CONFIG_H

#include <string>

/* Purpose: Setup CLI/runtime configuration assembled from CLI and optional JSON config.
 *
 * Fields:
 *   - command: Subcommand selector ("install", "repair", "uninstall", "list", "info").
 *   - mode: Installation mode ("portable", "per-user", "system").
 *   - install_root: Target install root path.
 *   - version: Optional version string.
 *   - create_shortcuts: Whether to create shortcuts for the install.
 *   - register_system: Whether to register the install with the host system.
 *   - portable_self_contained: Whether portable mode is self-contained.
 *   - interactive: True when stdin is interactive or CLI forces interaction.
 *   - config_file: Optional JSON config file path.
 *   - remove_user_data_on_uninstall: Remove user data during uninstall when true.
 */
struct SetupConfig {
    std::string command;
    std::string mode;
    std::string install_root;
    std::string version;
    bool create_shortcuts;
    bool register_system;
    bool portable_self_contained;
    bool interactive;
    std::string config_file;
    bool remove_user_data_on_uninstall;
};

/* Purpose: Parse CLI arguments into `cfg`.
 *
 * Parameters:
 *   - argc/argv: Command-line arguments from `main` (borrowed; not retained).
 *   - cfg: In/out configuration updated with parsed values.
 *
 * Returns:
 *   - true if a supported subcommand is provided; false otherwise.
 *
 * Side effects:
 *   - Prints usage to stdout on invalid input.
 */
bool parse_setup_cli(int argc, char **argv, SetupConfig &cfg);

/* Purpose: Load JSON config values from `cfg.config_file` into `cfg`.
 *
 * Parameters:
 *   - cfg: In/out configuration; unchanged if no config file is set or parsing fails.
 *
 * Side effects:
 *   - Reads from disk and emits log warnings on failure.
 */
void load_setup_config_file(SetupConfig &cfg);

/* Purpose: Apply CLI flag overrides to `cfg` after loading defaults/config files.
 *
 * Parameters:
 *   - cfg: In/out configuration updated with CLI overrides.
 *   - argc/argv: Command-line arguments from `main` (borrowed; not retained).
 */
void apply_cli_overrides(SetupConfig &cfg, int argc, char **argv);

/* Purpose: Resolve default mode/paths and derived flags in `cfg`.
 *
 * Parameters:
 *   - cfg: In/out configuration updated with defaults.
 *
 * Returns:
 *   - true if a valid install root is resolved; false otherwise.
 */
bool resolve_setup_defaults(SetupConfig &cfg);

/* Purpose: Execute the install subcommand.
 *
 * Parameters:
 *   - cfg: Fully resolved configuration (input).
 *
 * Returns:
 *   - 0 on success; non-zero on failure.
 */
int run_install(const SetupConfig &cfg);

/* Purpose: Execute the repair subcommand.
 *
 * Parameters:
 *   - cfg: Fully resolved configuration (input).
 *
 * Returns:
 *   - 0 on success; non-zero on failure.
 */
int run_repair(const SetupConfig &cfg);

/* Purpose: Execute the uninstall subcommand.
 *
 * Parameters:
 *   - cfg: Fully resolved configuration (input).
 *
 * Returns:
 *   - 0 on success; non-zero on failure.
 */
int run_uninstall(const SetupConfig &cfg);

/* Purpose: Execute the list subcommand.
 *
 * Parameters:
 *   - cfg: Configuration used for discovery (input).
 *
 * Returns:
 *   - 0 on success; non-zero on failure.
 */
int run_list(const SetupConfig &cfg);

/* Purpose: Execute the info subcommand.
 *
 * Parameters:
 *   - cfg: Configuration with `install_root` set (input).
 *
 * Returns:
 *   - 0 on success; non-zero on failure.
 */
int run_info(const SetupConfig &cfg);

#endif /* DOM_SETUP_CONFIG_H */
