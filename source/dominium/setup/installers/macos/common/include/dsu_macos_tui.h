#ifndef DSU_MACOS_TUI_H_INCLUDED
#define DSU_MACOS_TUI_H_INCLUDED

#ifdef __cplusplus
extern "C" {
#endif

int dsu_macos_tui_is_tty(void);
void dsu_macos_tui_clear(void);
void dsu_macos_tui_flush(void);
int dsu_macos_tui_read_line(char *buf, unsigned long cap);
void dsu_macos_tui_trim(char *s);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DSU_MACOS_TUI_H_INCLUDED */
