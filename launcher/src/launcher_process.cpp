#include "launcher_process.h"

#include <sstream>

#ifdef _WIN32
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#else
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>
#include <signal.h>
#endif

static std::string quote_arg(const std::string &arg)
{
    if (arg.find(' ') == std::string::npos && arg.find('\t') == std::string::npos) {
        return arg;
    }
    std::string out = "\"";
    out += arg;
    out += "\"";
    return out;
}

bool launcher_spawn_process(const std::string &exe_path,
                            const std::vector<std::string> &args,
                            const std::string &workdir,
                            bool hide_window,
                            LauncherProcessHandle &out_handle,
                            std::string &err)
{
    (void)hide_window;
#ifdef _WIN32
    std::stringstream ss;
    ss << "\"" << exe_path << "\"";
    for (size_t i = 0; i < args.size(); ++i) {
        ss << " " << quote_arg(args[i]);
    }
    std::string cmd = ss.str();
    STARTUPINFOA si;
    PROCESS_INFORMATION pi;
    ZeroMemory(&si, sizeof(si));
    ZeroMemory(&pi, sizeof(pi));
    si.cb = sizeof(si);
    DWORD flags = hide_window ? CREATE_NO_WINDOW : 0;
    if (!CreateProcessA(NULL,
                        const_cast<char *>(cmd.c_str()),
                        NULL,
                        NULL,
                        FALSE,
                        flags,
                        NULL,
                        workdir.empty() ? NULL : workdir.c_str(),
                        &si,
                        &pi)) {
        err = "CreateProcess failed";
        return false;
    }
    CloseHandle(pi.hThread);
    out_handle.process = pi.hProcess;
    out_handle.pid = pi.dwProcessId;
    return true;
#else
    pid_t pid = fork();
    if (pid < 0) {
        err = "fork failed";
        return false;
    }
    if (pid == 0) {
        if (!workdir.empty()) {
            chdir(workdir.c_str());
        }
        std::vector<char *> argv;
        argv.push_back(const_cast<char *>(exe_path.c_str()));
        for (size_t i = 0; i < args.size(); ++i) {
            argv.push_back(const_cast<char *>(args[i].c_str()));
        }
        argv.push_back(NULL);
        execvp(exe_path.c_str(), &argv[0]);
        _exit(1);
    }
    out_handle.pid = pid;
    return true;
#endif
}

bool launcher_wait_process(const LauncherProcessHandle &handle, int &exit_code)
{
#ifdef _WIN32
    if (!handle.process) return false;
    WaitForSingleObject(handle.process, INFINITE);
    DWORD code = 1;
    GetExitCodeProcess(handle.process, &code);
    exit_code = (int)code;
    return true;
#else
    int status = 0;
    if (waitpid(handle.pid, &status, 0) < 0) {
        return false;
    }
    if (WIFEXITED(status)) {
        exit_code = WEXITSTATUS(status);
    } else {
        exit_code = -1;
    }
    return true;
#endif
}

bool launcher_terminate_process(const LauncherProcessHandle &handle)
{
#ifdef _WIN32
    if (!handle.process) return false;
    TerminateProcess(handle.process, 1);
    return true;
#else
    if (handle.pid <= 0) return false;
    kill(handle.pid, SIGTERM);
    return true;
#endif
}
