#ifndef DSU_EXE_WIN32_H_INCLUDED
#define DSU_EXE_WIN32_H_INCLUDED

#include "dsu_exe_bridge.h"
#include "dsu_exe_ui.h"

#ifdef __cplusplus
extern "C" {
#endif

int dsu_exe_entry_run(int argc, char **argv, const char *platform, const char *frontend_id);

int dsu_exe_run_gui(const dsu_exe_bridge_paths_t *paths,
                    const char *platform,
                    const char *frontend_id,
                    int quiet);
int dsu_exe_run_tui(const dsu_exe_bridge_paths_t *paths,
                    const char *platform,
                    const char *frontend_id,
                    int quiet);

int dsu_exe_apply_from_state(const dsu_exe_bridge_paths_t *paths,
                             const char *platform,
                             const char *frontend_id,
                             const dsu_ui_state_t *state,
                             const char *components_csv,
                             const char *exclude_csv,
                             const char *ui_mode,
                             int quiet);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DSU_EXE_WIN32_H_INCLUDED */
