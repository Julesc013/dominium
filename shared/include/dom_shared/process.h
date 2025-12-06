#ifndef DOM_SHARED_PROCESS_H
#define DOM_SHARED_PROCESS_H

#include <string>
#include <vector>

namespace dom_shared {

struct ProcessOptions {
    std::string working_directory;
    bool        inherit_environment;

    ProcessOptions() : working_directory(), inherit_environment(true) {}
};

struct ProcessHandle {
    int  pid;           // platform-specific ID
    void* internal;     // opaque pointer to internal state

    ProcessHandle() : pid(-1), internal(0) {}
};

bool spawn_process(const std::string& executable,
                   const std::vector<std::string>& args,
                   const ProcessOptions& options,
                   ProcessHandle& out_handle);

// Non-blocking check if process is still alive
bool process_is_running(const ProcessHandle& handle);

// Blocking wait
int  process_wait(const ProcessHandle& handle);

// Simple helpers to read buffered stdout/stderr later if implemented
// (You can stub them for now; they will be expanded later)
std::string process_read_stdout(const ProcessHandle& handle);
std::string process_read_stderr(const ProcessHandle& handle);

} // namespace dom_shared

#endif
