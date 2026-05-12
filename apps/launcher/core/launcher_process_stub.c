/*
Stub launcher process management.
*/
#include "launcher/launcher_process.h"

#include <string.h>

int launcher_process_spawn(launcher_proc* p, const char* exe, const char* args, const char* cwd)
{
    (void)exe;
    (void)args;
    (void)cwd;
    if (p) {
        memset(p, 0, sizeof(*p));
        p->pid = -1;
        p->running = 0;
        p->exit_code = -1;
    }
    return -1;
}

int launcher_process_poll(launcher_proc* p)
{
    (void)p;
    return -1;
}

int launcher_process_kill(launcher_proc* p)
{
    (void)p;
    return -1;
}

int launcher_process_read_stdout(launcher_proc* p, char* buf, int maxlen)
{
    (void)p;
    (void)buf;
    (void)maxlen;
    return -1;
}
