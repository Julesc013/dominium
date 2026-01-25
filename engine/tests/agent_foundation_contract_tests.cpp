/*
Agent foundation contract tests (AGENT0/TestX).
*/
#include "domino/agent.h"

#include <stdio.h>
#include <fstream>
#include <sstream>
#include <string>

#ifndef DOMINIUM_REPO_ROOT
#define DOMINIUM_REPO_ROOT "."
#endif

#define EXPECT(cond, msg) do { \
    if (!(cond)) { \
        fprintf(stderr, "FAIL: %s\n", msg); \
        return 1; \
    } \
} while (0)

#define STATIC_ASSERT(cond, name) \
    typedef char static_assert_##name[(cond) ? 1 : -1]

STATIC_ASSERT(DOM_AGENT_SNAPSHOT_SUBJECTIVE == 0, agent_snapshot_default_subjective);
STATIC_ASSERT(DOM_AGENT_ID_INVALID == 0, agent_invalid_id_zero);

static std::string join_path(const char* root, const char* rel)
{
    std::string out = root ? root : ".";
    if (!out.empty()) {
        char last = out[out.size() - 1];
        if (last != '/' && last != '\\') {
            out += '/';
        }
    }
    out += rel;
    return out;
}

static int read_file(const char* path, std::string* out)
{
    std::ifstream file(path, std::ios::in | std::ios::binary);
    if (!file.is_open()) {
        return 0;
    }
    std::ostringstream buffer;
    buffer << file.rdbuf();
    *out = buffer.str();
    return 1;
}

static std::string to_lower(const std::string& input)
{
    std::string out = input;
    for (std::string::size_type i = 0; i < out.size(); ++i) {
        char c = out[i];
        if (c >= 'A' && c <= 'Z') {
            out[i] = static_cast<char>(c - 'A' + 'a');
        }
    }
    return out;
}

static int contains_ci(const std::string& haystack, const char* needle)
{
    std::string hay = to_lower(haystack);
    std::string need = to_lower(std::string(needle));
    return hay.find(need) != std::string::npos;
}

static int require_contains(const char* path, const char* needle)
{
    std::string data;
    if (!read_file(path, &data)) {
        fprintf(stderr, "FAIL: unable to read %s\n", path);
        return 0;
    }
    if (!contains_ci(data, needle)) {
        fprintf(stderr, "FAIL: missing \"%s\" in %s\n", needle, path);
        return 0;
    }
    return 1;
}

static int require_doc_links(const char* path)
{
    if (!require_contains(path, "arch/INVARIANTS.md")) {
        return 0;
    }
    if (!require_contains(path, "arch/REALITY_LAYER.md")) {
        return 0;
    }
    return 1;
}

static int test_contract_docs(void)
{
    std::string model = join_path(DOMINIUM_REPO_ROOT, "docs/agents/AGENT_MODEL.md");
    std::string identity = join_path(DOMINIUM_REPO_ROOT, "docs/agents/AGENT_IDENTITY.md");
    std::string lifecycle = join_path(DOMINIUM_REPO_ROOT, "docs/agents/AGENT_LIFECYCLE.md");
    std::string non_goals = join_path(DOMINIUM_REPO_ROOT, "docs/agents/AGENT_NON_GOALS.md");

    EXPECT(require_doc_links(model.c_str()), "AGENT_MODEL links");
    EXPECT(require_doc_links(identity.c_str()), "AGENT_IDENTITY links");
    EXPECT(require_doc_links(lifecycle.c_str()), "AGENT_LIFECYCLE links");
    EXPECT(require_doc_links(non_goals.c_str()), "AGENT_NON_GOALS links");

    EXPECT(require_contains(model.c_str(), "must not see objective truth by default"),
           "AGENT_MODEL objective truth default");
    EXPECT(require_contains(model.c_str(), "must not mutate state without authority"),
           "AGENT_MODEL authority mutation");

    EXPECT(require_contains(identity.c_str(), "must persist across save/load"),
           "AGENT_IDENTITY persistence");

    EXPECT(require_contains(lifecycle.c_str(), "must be created only via processes"),
           "AGENT_LIFECYCLE creation");
    EXPECT(require_contains(lifecycle.c_str(), "must be terminated only via processes"),
           "AGENT_LIFECYCLE termination");
    EXPECT(require_contains(lifecycle.c_str(), "termination must leave history"),
           "AGENT_LIFECYCLE history");
    EXPECT(require_contains(lifecycle.c_str(), "history must remain queryable"),
           "AGENT_LIFECYCLE history query");

    return 0;
}

static int test_contract_header(void)
{
    std::string header = join_path(DOMINIUM_REPO_ROOT, "engine/include/domino/agent.h");

    EXPECT(require_contains(header.c_str(), "dom_process_exec_context"),
           "agent header process context");
    EXPECT(require_contains(header.c_str(), "dom_agent_create"),
           "agent header create function");
    EXPECT(require_contains(header.c_str(), "dom_agent_terminate"),
           "agent header terminate function");
    EXPECT(require_contains(header.c_str(), "dom_agent_snapshot_kind"),
           "agent header snapshot kind");
    EXPECT(require_contains(header.c_str(), "dom_agent_history"),
           "agent header history function");

    return 0;
}

int main(void)
{
    if (test_contract_docs() != 0) {
        return 1;
    }
    if (test_contract_header() != 0) {
        return 1;
    }
    return 0;
}
