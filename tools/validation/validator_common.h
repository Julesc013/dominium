/*
FILE: tools/validation/validator_common.h
MODULE: Dominium
LAYER / SUBSYSTEM: Tools / validation
RESPONSIBILITY: Shared helpers for validator scanning and reporting.
ALLOWED DEPENDENCIES: C/C++98 standard headers only.
FORBIDDEN DEPENDENCIES: Engine/game internal headers; OS headers in authoritative code.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Validator output is deterministic for a given repo state.
*/
#ifndef DOMINIUM_TOOLS_VALIDATION_COMMON_H
#define DOMINIUM_TOOLS_VALIDATION_COMMON_H

#include <string>
#include <vector>

namespace dom {
namespace validation {

enum ValidationSeverity {
    VAL_SEV_WARN = 1,
    VAL_SEV_ERROR = 2
};

struct ValidationIssue {
    std::string rule_id;
    std::string message;
    std::string remediation;
    std::string path;
    unsigned int line;
    ValidationSeverity severity;
};

struct ValidationReport {
    std::vector<ValidationIssue> issues;
    unsigned int warning_count;
    unsigned int error_count;
    ValidationReport();
    void add(const std::string& rule_id,
             ValidationSeverity severity,
             const std::string& path,
             unsigned int line,
             const std::string& message,
             const std::string& remediation);
    bool has_errors() const;
};

struct ValidationContext {
    std::string repo_root;
    bool strict;
};

struct DirEntry {
    std::string name;
    bool is_dir;
};

bool read_file_text(const std::string& path, std::string& out_text);
std::string to_lower(const std::string& value);
bool path_join(const std::string& base, const std::string& child, std::string& out);
bool is_dir(const std::string& path);
void list_dir(const std::string& path, std::vector<DirEntry>& out_entries);
void list_files_recursive(const std::string& root,
                          const std::vector<std::string>& exts,
                          const std::vector<std::string>& skip_dirs,
                          std::vector<std::string>& out_files);
bool starts_with(const std::string& value, const std::string& prefix);
bool contains_token(const std::string& haystack, const std::string& needle);

} /* namespace validation */
} /* namespace dom */

#endif /* DOMINIUM_TOOLS_VALIDATION_COMMON_H */
