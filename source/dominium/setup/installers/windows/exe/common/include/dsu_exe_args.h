#ifndef DSU_EXE_ARGS_H_INCLUDED
#define DSU_EXE_ARGS_H_INCLUDED

#ifdef __cplusplus
extern "C" {
#endif

typedef enum dsu_exe_mode_t {
    DSU_EXE_MODE_GUI = 0,
    DSU_EXE_MODE_TUI = 1,
    DSU_EXE_MODE_CLI = 2
} dsu_exe_mode_t;

typedef enum dsu_exe_command_t {
    DSU_EXE_CMD_NONE = 0,
    DSU_EXE_CMD_INSTALL,
    DSU_EXE_CMD_UPGRADE,
    DSU_EXE_CMD_REPAIR,
    DSU_EXE_CMD_UNINSTALL,
    DSU_EXE_CMD_VERIFY,
    DSU_EXE_CMD_DETECT,
    DSU_EXE_CMD_EXPORT_INVOCATION,
    DSU_EXE_CMD_APPLY_INVOCATION,
    DSU_EXE_CMD_PLAN,
    DSU_EXE_CMD_APPLY
} dsu_exe_command_t;

typedef struct dsu_exe_cli_args_t {
    dsu_exe_command_t command;
    int want_help;
    int want_version;
    int want_json;
    int deterministic;
    int dry_run;
    int quiet;

    const char *manifest_path;
    const char *state_path;
    const char *invocation_path;
    const char *plan_path;
    const char *log_path;
    const char *install_root;
    const char *components_csv;
    const char *exclude_csv;
    const char *scope;
    const char *operation;
    const char *platform;
    const char *out_path;
    const char *ui_mode;
    const char *frontend_id;

    int policy_offline;
    int policy_allow_prerelease;
    int policy_legacy;
    int policy_shortcuts;
    int policy_file_assoc;
    int policy_url_handlers;
} dsu_exe_cli_args_t;

int dsu_exe_args_parse(int argc, char **argv, dsu_exe_mode_t *out_mode, dsu_exe_cli_args_t *out_cli);
const char *dsu_exe_command_name(dsu_exe_command_t cmd);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DSU_EXE_ARGS_H_INCLUDED */
