#ifndef DOMINO_LAUNCHER_PROCESS_H_INCLUDED
#define DOMINO_LAUNCHER_PROCESS_H_INCLUDED

#include "domino/baseline.h"
#include "domino/sys.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct launcher_proc {
    int             pid;
    int             running;
    int             exit_code;
    char            cmdline[260];
    char            cwd[260];
    dsys_process*   handle;
} launcher_proc;

int launcher_process_spawn(launcher_proc* p, const char* exe, const char* args, const char* cwd);
int launcher_process_poll(launcher_proc* p);
int launcher_process_kill(launcher_proc* p);
int launcher_process_read_stdout(launcher_proc* p, char* buf, int maxlen);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_LAUNCHER_PROCESS_H_INCLUDED */
