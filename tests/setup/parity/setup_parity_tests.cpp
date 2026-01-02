#include <cstdio>
#include <cstring>
#include <fstream>
#include <string>
#include <vector>

#ifndef SETUP_SOURCE_DIR
#define SETUP_SOURCE_DIR "."
#endif

static int fail(const char *msg, const std::string &path) {
    std::fprintf(stderr, "FAIL: %s (%s)\n", msg, path.c_str());
    return 1;
}

static int read_file(const std::string &path, std::string &out) {
    std::ifstream in(path.c_str(), std::ios::in | std::ios::binary);
    if (!in) {
        return 0;
    }
    std::string contents;
    in.seekg(0, std::ios::end);
    std::streamoff size = in.tellg();
    if (size < 0) {
        return 0;
    }
    in.seekg(0, std::ios::beg);
    contents.resize((size_t)size);
    if (size > 0) {
        in.read(&contents[0], size);
    }
    out.swap(contents);
    return in.good() || in.eof();
}

static int require_markers(const std::string &path,
                           const char *const *markers,
                           size_t count) {
    std::string data;
    size_t i;
    if (!read_file(path, data)) {
        return fail("unable to read file", path);
    }
    for (i = 0u; i < count; ++i) {
        if (!markers[i]) {
            continue;
        }
        if (data.find(markers[i]) == std::string::npos) {
            std::fprintf(stderr, "FAIL: missing marker '%s' in %s\n", markers[i], path.c_str());
            return 1;
        }
    }
    return 0;
}

static std::string root_path(const char *suffix) {
    std::string root = SETUP_SOURCE_DIR ? SETUP_SOURCE_DIR : ".";
    if (!root.empty() && root[root.size() - 1u] != '/') {
        root += "/";
    }
    return root + (suffix ? suffix : "");
}

static int test_kernel_invariants_match_launcher(void) {
    static const char *k_setup_markers[] = {
        "Kernel may not include OS headers",
        "All contracts are TLV",
        "All planning is deterministic",
        "All installs are resumable"
    };
    static const char *k_launcher_markers[] = {
        "deterministic instance manager",
        "zero UI assumptions",
        "Persistence is **TLV**",
        "Every run emits an audit record"
    };
    if (require_markers(root_path("docs/setup/INVARIANTS.md"),
                        k_setup_markers,
                        sizeof(k_setup_markers) / sizeof(k_setup_markers[0])) != 0) {
        return 1;
    }
    return require_markers(root_path("source/dominium/launcher/core/README_launcher_core.md"),
                           k_launcher_markers,
                           sizeof(k_launcher_markers) / sizeof(k_launcher_markers[0]));
}

static int test_capability_registry_semantics_match(void) {
    static const char *k_setup_markers[] = {
        "first compatible in canonical order",
        "lexicographic"
    };
    static const char *k_launcher_markers[] = {
        "deterministic capability snapshot build"
    };
    if (require_markers(root_path("docs/setup/SPLAT_SELECTION_RULES.md"),
                        k_setup_markers,
                        sizeof(k_setup_markers) / sizeof(k_setup_markers[0])) != 0) {
        return 1;
    }
    return require_markers(root_path("source/dominium/launcher/launcher_caps_snapshot.h"),
                           k_launcher_markers,
                           sizeof(k_launcher_markers) / sizeof(k_launcher_markers[0]));
}

static int test_job_journal_semantics_match(void) {
    static const char *k_setup_markers[] = {
        "job_journal.tlv",
        "deterministic"
    };
    static const char *k_launcher_markers[] = {
        "Job graph + journal TLVs are deterministic"
    };
    if (require_markers(root_path("docs/setup/JOB_ENGINE.md"),
                        k_setup_markers,
                        sizeof(k_setup_markers) / sizeof(k_setup_markers[0])) != 0) {
        return 1;
    }
    return require_markers(root_path("source/dominium/launcher/core/include/launcher_job.h"),
                           k_launcher_markers,
                           sizeof(k_launcher_markers) / sizeof(k_launcher_markers[0]));
}

int main(int argc, char **argv) {
    if (argc < 2) {
        std::fprintf(stderr, "usage: setup_parity_tests <test>\n");
        return 1;
    }
    if (std::strcmp(argv[1], "kernel_invariants_match_launcher") == 0) {
        return test_kernel_invariants_match_launcher();
    }
    if (std::strcmp(argv[1], "capability_registry_semantics_match") == 0) {
        return test_capability_registry_semantics_match();
    }
    if (std::strcmp(argv[1], "job_journal_semantics_match") == 0) {
        return test_job_journal_semantics_match();
    }
    std::fprintf(stderr, "unknown test: %s\n", argv[1]);
    return 1;
}
