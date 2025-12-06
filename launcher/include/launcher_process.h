// Process supervision primitives (platform-specific spawning).
#ifndef DOM_LAUNCHER_PROCESS_H
#define DOM_LAUNCHER_PROCESS_H

#include <string>
#include <vector>

struct LauncherProcessHandle {
    std::string instance_id;
#ifdef _WIN32
    void *process;
    unsigned long pid;
#else
    int pid;
#endif
};

bool launcher_spawn_process(const std::string &exe_path,
                            const std::vector<std::string> &args,
                            const std::string &workdir,
                            bool hide_window,
                            LauncherProcessHandle &out_handle,
                            std::string &err);

bool launcher_wait_process(const LauncherProcessHandle &handle, int &exit_code);
bool launcher_terminate_process(const LauncherProcessHandle &handle);

#endif /* DOM_LAUNCHER_PROCESS_H */
