#ifndef DSU_MACOS_ARGS_H_INCLUDED
#define DSU_MACOS_ARGS_H_INCLUDED

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dsu_macos_cli_args_t {
    int want_help;
    int want_version;
    int want_json;
    int deterministic;
    int dry_run;
    int quiet;
    int non_interactive;
    int use_defaults;
    int export_invocation;
    int apply_invocation;
    int run_plan;
    int run_apply;

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
} dsu_macos_cli_args_t;

int dsu_macos_args_parse(int argc, char **argv, dsu_macos_cli_args_t *out_cli);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DSU_MACOS_ARGS_H_INCLUDED */
