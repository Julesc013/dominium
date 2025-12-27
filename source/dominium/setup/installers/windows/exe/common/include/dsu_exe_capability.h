#ifndef DSU_EXE_CAPABILITY_H_INCLUDED
#define DSU_EXE_CAPABILITY_H_INCLUDED

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dsu_exe_capabilities_t {
    int is_win9x;
    int is_nt;
    int has_console;
} dsu_exe_capabilities_t;

void dsu_exe_detect_capabilities(dsu_exe_capabilities_t *out_caps);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DSU_EXE_CAPABILITY_H_INCLUDED */
