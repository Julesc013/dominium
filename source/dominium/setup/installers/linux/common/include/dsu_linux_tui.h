#ifndef DSU_LINUX_TUI_H_INCLUDED
#define DSU_LINUX_TUI_H_INCLUDED

#ifdef __cplusplus
extern "C" {
#endif

int dsu_linux_tui_is_tty(void);
void dsu_linux_tui_clear(void);
void dsu_linux_tui_flush(void);
int dsu_linux_tui_read_line(char *buf, unsigned long cap);
void dsu_linux_tui_trim(char *s);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DSU_LINUX_TUI_H_INCLUDED */
