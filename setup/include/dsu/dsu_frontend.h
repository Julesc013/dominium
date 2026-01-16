/*
Public setup frontend API (stub).
*/
#ifndef DSU_FRONTEND_H_INCLUDED
#define DSU_FRONTEND_H_INCLUDED

#ifdef __cplusplus
extern "C" {
#endif

int dsu_gui_run(int argc, char** argv);
int dsu_tui_run(int argc, char** argv);

#ifdef __cplusplus
}
#endif

#endif /* DSU_FRONTEND_H_INCLUDED */
