#include "dom_shared/process.h"
#include "dom_shared/logging.h"

#ifdef _WIN32
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <process.h>
#else
#include <unistd.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <signal.h>
#endif

#include <vector>
#include <string>

namespace dom_shared {

#ifdef _WIN32
struct ProcessInternal {
    HANDLE process_handle;
};

static std::string quote_arg(const std::string& a)
{
    for (size_t i = 0; i < a.size(); ++i) {
        if (a[i] == ' ' || a[i] == '\t') {
            return "\"" + a + "\"";
        }
    }
    return a;
}
#endif

bool spawn_process(const std::string& executable,
                   const std::vector<std::string>& args,
                   const ProcessOptions& options,
                   ProcessHandle& out_handle)
{
#ifdef _WIN32
    std::string cmd_line = quote_arg(executable);
    for (size_t i = 0; i < args.size(); ++i) {
        cmd_line.append(" ");
        cmd_line.append(quote_arg(args[i]));
    }

    STARTUPINFOA si;
    ZeroMemory(&si, sizeof(si));
    si.cb = sizeof(si);
    PROCESS_INFORMATION pi;
    ZeroMemory(&pi, sizeof(pi));

    LPSTR cmd_ptr = cmd_line.empty() ? NULL : const_cast<char*>(cmd_line.c_str());
    LPVOID env_ptr = options.inherit_environment ? (LPVOID)NULL : (LPVOID)NULL; // placeholder for future custom env
    BOOL ok = CreateProcessA(
        NULL,
        cmd_ptr,
        NULL,
        NULL,
        FALSE,
        0,
        env_ptr,
        options.working_directory.empty() ? NULL : options.working_directory.c_str(),
        &si,
        &pi);
    if (!ok) {
        log_error("CreateProcess failed for %s", executable.c_str());
        return false;
    }

    CloseHandle(pi.hThread);
    ProcessInternal* internal = new ProcessInternal();
    internal->process_handle = pi.hProcess;
    out_handle.pid = (int)pi.dwProcessId;
    out_handle.internal = internal;
    return true;
#else
    std::vector<std::string> argv_storage;
    argv_storage.push_back(executable);
    for (size_t i = 0; i < args.size(); ++i) argv_storage.push_back(args[i]);

    std::vector<char*> argv(argv_storage.size() + 1, (char*)0);
    for (size_t i = 0; i < argv_storage.size(); ++i) {
        argv[i] = const_cast<char*>(argv_storage[i].c_str());
    }
    pid_t pid = fork();
    if (pid == 0) {
        if (!options.working_directory.empty()) {
            chdir(options.working_directory.c_str());
        }
        // TODO: support non-inherited environment if needed.
        execv(executable.c_str(), &argv[0]);
        _exit(127);
    } else if (pid > 0) {
        out_handle.pid = (int)pid;
        out_handle.internal = 0;
        return true;
    }
    log_error("Failed to fork for %s", executable.c_str());
    return false;
#endif
}

bool process_is_running(const ProcessHandle& handle)
{
    if (handle.pid <= 0) return false;
#ifdef _WIN32
    const ProcessInternal* internal = (const ProcessInternal*)handle.internal;
    if (!internal || !internal->process_handle) return false;
    DWORD wait_rc = WaitForSingleObject(internal->process_handle, 0);
    return wait_rc == WAIT_TIMEOUT;
#else
    int rc = kill((pid_t)handle.pid, 0);
    return rc == 0;
#endif
}

int process_wait(const ProcessHandle& handle)
{
    if (handle.pid <= 0) return -1;
#ifdef _WIN32
    ProcessInternal* internal = (ProcessInternal*)handle.internal;
    if (!internal || !internal->process_handle) return -1;
    WaitForSingleObject(internal->process_handle, INFINITE);
    DWORD code = 0;
    GetExitCodeProcess(internal->process_handle, &code);
    CloseHandle(internal->process_handle);
    delete internal;
    return (int)code;
#else
    int status = 0;
    pid_t rc = waitpid((pid_t)handle.pid, &status, 0);
    if (rc < 0) return -1;
    if (WIFEXITED(status)) return WEXITSTATUS(status);
    return status;
#endif
}

std::string process_read_stdout(const ProcessHandle& handle)
{
    (void)handle;
    return std::string(); // TODO: implement buffered stdout capture
}

std::string process_read_stderr(const ProcessHandle& handle)
{
    (void)handle;
    return std::string(); // TODO: implement buffered stderr capture
}

} // namespace dom_shared
