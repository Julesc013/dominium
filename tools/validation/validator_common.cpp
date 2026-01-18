/*
FILE: tools/validation/validator_common.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Tools / validation
RESPONSIBILITY: Implements shared helpers for validator scanning and reporting.
ALLOWED DEPENDENCIES: C/C++98 standard headers only.
FORBIDDEN DEPENDENCIES: Engine/game internal headers; OS headers in authoritative code.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Validator output is deterministic for a given repo state.
*/
#include "validator_common.h"

#include <cstdio>
#include <cstring>

#if defined(_WIN32)
#include <windows.h>
#else
#include <dirent.h>
#include <sys/stat.h>
#endif

namespace dom {
namespace validation {

ValidationReport::ValidationReport()
    : warning_count(0u)
    , error_count(0u) {}

void ValidationReport::add(const std::string& rule_id,
                           ValidationSeverity severity,
                           const std::string& path,
                           unsigned int line,
                           const std::string& message,
                           const std::string& remediation) {
    ValidationIssue issue;
    issue.rule_id = rule_id;
    issue.message = message;
    issue.remediation = remediation;
    issue.path = path;
    issue.line = line;
    issue.severity = severity;
    issues.push_back(issue);
    if (severity == VAL_SEV_ERROR) {
        error_count += 1u;
    } else {
        warning_count += 1u;
    }
}

bool ValidationReport::has_errors() const {
    return error_count > 0u;
}

bool read_file_text(const std::string& path, std::string& out_text) {
    FILE* f = std::fopen(path.c_str(), "rb");
    if (!f) {
        return false;
    }
    if (std::fseek(f, 0, SEEK_END) != 0) {
        std::fclose(f);
        return false;
    }
    long size = std::ftell(f);
    if (size < 0) {
        std::fclose(f);
        return false;
    }
    if (std::fseek(f, 0, SEEK_SET) != 0) {
        std::fclose(f);
        return false;
    }
    out_text.clear();
    if (size > 0) {
        out_text.resize(static_cast<size_t>(size));
        size_t read = std::fread(&out_text[0], 1u, static_cast<size_t>(size), f);
        if (read != static_cast<size_t>(size)) {
            std::fclose(f);
            return false;
        }
    }
    std::fclose(f);
    return true;
}

std::string to_lower(const std::string& value) {
    std::string out;
    out.reserve(value.size());
    for (size_t i = 0u; i < value.size(); ++i) {
        char c = value[i];
        if (c >= 'A' && c <= 'Z') {
            c = static_cast<char>(c - 'A' + 'a');
        }
        out.push_back(c);
    }
    return out;
}

bool path_join(const std::string& base, const std::string& child, std::string& out) {
    if (base.empty()) {
        out = child;
        return true;
    }
    if (child.empty()) {
        out = base;
        return true;
    }
    char sep =
#if defined(_WIN32)
        '\\';
#else
        '/';
#endif
    out = base;
    if (out[out.size() - 1u] != sep) {
        out.push_back(sep);
    }
    out += child;
    return true;
}

bool is_dir(const std::string& path) {
#if defined(_WIN32)
    DWORD attrs = GetFileAttributesA(path.c_str());
    if (attrs == INVALID_FILE_ATTRIBUTES) {
        return false;
    }
    return (attrs & FILE_ATTRIBUTE_DIRECTORY) != 0;
#else
    struct stat st;
    if (stat(path.c_str(), &st) != 0) {
        return false;
    }
    return S_ISDIR(st.st_mode);
#endif
}

void list_dir(const std::string& path, std::vector<DirEntry>& out_entries) {
    out_entries.clear();
#if defined(_WIN32)
    std::string pattern = path;
    if (!pattern.empty() && pattern[pattern.size() - 1u] != '\\') {
        pattern += "\\";
    }
    pattern += "*";
    WIN32_FIND_DATAA data;
    HANDLE h = FindFirstFileA(pattern.c_str(), &data);
    if (h == INVALID_HANDLE_VALUE) {
        return;
    }
    do {
        const char* name = data.cFileName;
        if (!name || std::strcmp(name, ".") == 0 || std::strcmp(name, "..") == 0) {
            continue;
        }
        DirEntry entry;
        entry.name = name;
        entry.is_dir = (data.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY) != 0;
        out_entries.push_back(entry);
    } while (FindNextFileA(h, &data));
    FindClose(h);
#else
    DIR* dir = opendir(path.c_str());
    if (!dir) {
        return;
    }
    struct dirent* ent = 0;
    while ((ent = readdir(dir)) != 0) {
        const char* name = ent->d_name;
        if (!name || std::strcmp(name, ".") == 0 || std::strcmp(name, "..") == 0) {
            continue;
        }
        DirEntry entry;
        entry.name = name;
        std::string full;
        path_join(path, name, full);
        entry.is_dir = is_dir(full);
        out_entries.push_back(entry);
    }
    closedir(dir);
#endif
}

static bool has_ext(const std::string& path, const std::vector<std::string>& exts) {
    if (exts.empty()) {
        return true;
    }
    std::string lower = to_lower(path);
    for (size_t i = 0u; i < exts.size(); ++i) {
        const std::string& ext = exts[i];
        if (lower.size() >= ext.size() &&
            lower.compare(lower.size() - ext.size(), ext.size(), ext) == 0) {
            return true;
        }
    }
    return false;
}

static bool is_skipped_dir(const std::string& name, const std::vector<std::string>& skip_dirs) {
    for (size_t i = 0u; i < skip_dirs.size(); ++i) {
        if (name == skip_dirs[i]) {
            return true;
        }
    }
    return false;
}

void list_files_recursive(const std::string& root,
                          const std::vector<std::string>& exts,
                          const std::vector<std::string>& skip_dirs,
                          std::vector<std::string>& out_files) {
    std::vector<DirEntry> entries;
    list_dir(root, entries);
    for (size_t i = 0u; i < entries.size(); ++i) {
        const DirEntry& entry = entries[i];
        if (entry.is_dir) {
            if (is_skipped_dir(entry.name, skip_dirs)) {
                continue;
            }
            std::string child;
            path_join(root, entry.name, child);
            list_files_recursive(child, exts, skip_dirs, out_files);
        } else {
            std::string path;
            path_join(root, entry.name, path);
            if (has_ext(path, exts)) {
                out_files.push_back(path);
            }
        }
    }
}

bool starts_with(const std::string& value, const std::string& prefix) {
    if (prefix.size() > value.size()) {
        return false;
    }
    return value.compare(0u, prefix.size(), prefix) == 0;
}

bool contains_token(const std::string& haystack, const std::string& needle) {
    if (needle.empty()) {
        return true;
    }
    return haystack.find(needle) != std::string::npos;
}

} /* namespace validation */
} /* namespace dom */
