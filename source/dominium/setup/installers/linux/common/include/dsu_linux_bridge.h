#ifndef DSU_LINUX_BRIDGE_H_INCLUDED
#define DSU_LINUX_BRIDGE_H_INCLUDED

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dsu_linux_bridge_paths_t {
    const char *staging_root;
    const char *manifest_path;
    const char *core_exe_path;
    const char *adapter_exe_path;
} dsu_linux_bridge_paths_t;

int dsu_linux_bridge_spawn(const char *cmdline, int quiet);
int dsu_linux_bridge_export_invocation(const dsu_linux_bridge_paths_t *paths,
                                       const char *args,
                                       int deterministic,
                                       int quiet,
                                       int format_json);
int dsu_linux_bridge_plan(const dsu_linux_bridge_paths_t *paths,
                          const char *invocation_path,
                          const char *plan_path,
                          const char *state_path,
                          int deterministic,
                          int quiet,
                          int format_json);
int dsu_linux_bridge_apply_plan(const dsu_linux_bridge_paths_t *paths,
                                const char *plan_path,
                                int deterministic,
                                int dry_run,
                                int quiet,
                                int format_json);
int dsu_linux_bridge_apply_invocation(const dsu_linux_bridge_paths_t *paths,
                                      const char *invocation_path,
                                      int deterministic,
                                      int dry_run,
                                      int quiet,
                                      int format_json);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DSU_LINUX_BRIDGE_H_INCLUDED */
