/*
FILE: source/tests/ui_cli_determinism_test.cpp
MODULE: Dominium Tests
PURPOSE: Headless determinism checks for UI CLI (apply/codegen/registry/scan).
NOTES: Uses dominium-ui-editor CLI; no GUI initialization.
*/
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include <map>
#include <cctype>
#include <cerrno>

#if defined(_WIN32)
#include <direct.h>
#include <windows.h>
#else
#include <sys/stat.h>
#include <unistd.h>
#include <sys/wait.h>
#endif

struct Args {
    std::string mode;
    std::string ui_editor;
    std::string script;
    std::string work_dir;
    std::string doc;
    std::string docname;
    std::string doc_basename;
};

static int is_sep(char c) { return c == '/' || c == '\\'; }

static std::string join_path(const std::string& a, const std::string& b)
{
    if (a.empty()) return b;
    if (b.empty()) return a;
    if (is_sep(a[a.size() - 1u])) return a + b;
    return a + "/" + b;
}

static std::string replace_ext(const std::string& path, const std::string& new_ext)
{
    size_t dot = path.find_last_of('.');
    size_t sep = path.find_last_of("/\\");
    if (dot != std::string::npos && (sep == std::string::npos || dot > sep)) {
        return path.substr(0u, dot) + new_ext;
    }
    return path + new_ext;
}

static int make_dir(const std::string& path)
{
    if (path.empty()) return 0;
#if defined(_WIN32)
    if (_mkdir(path.c_str()) == 0) return 1;
#else
    if (mkdir(path.c_str(), 0755) == 0) return 1;
#endif
    if (errno == EEXIST) return 1;
    return 0;
}

static int ensure_dir_recursive(const std::string& path)
{
    size_t i = 0u;
    std::string cur;
    if (path.empty()) return 0;
    if (path.size() >= 2u && path[1] == ':') {
        cur = path.substr(0u, 2u);
        i = 2u;
        if (i < path.size() && is_sep(path[i])) {
            cur.push_back(path[i]);
            ++i;
        }
    }
    for (; i < path.size(); ++i) {
        char c = path[i];
        if (is_sep(c)) {
            if (!cur.empty() && !make_dir(cur)) return 0;
        }
        cur.push_back(c);
    }
    if (!cur.empty() && !make_dir(cur)) return 0;
    return 1;
}

static int read_file_bytes(const std::string& path, std::vector<unsigned char>& out)
{
    FILE* f = std::fopen(path.c_str(), "rb");
    long sz;
    size_t got;
    out.clear();
    if (!f) return 0;
    if (std::fseek(f, 0, SEEK_END) != 0) {
        std::fclose(f);
        return 0;
    }
    sz = std::ftell(f);
    if (sz < 0) {
        std::fclose(f);
        return 0;
    }
    if (std::fseek(f, 0, SEEK_SET) != 0) {
        std::fclose(f);
        return 0;
    }
    out.resize((size_t)sz);
    got = 0u;
    if (sz > 0) {
        got = std::fread(&out[0], 1u, (size_t)sz, f);
    }
    std::fclose(f);
    return got == (size_t)sz;
}

static int compare_files(const std::string& a, const std::string& b, std::string& out_error)
{
    std::vector<unsigned char> ba;
    std::vector<unsigned char> bb;
    if (!read_file_bytes(a, ba)) {
        out_error = "read_failed:" + a;
        return 0;
    }
    if (!read_file_bytes(b, bb)) {
        out_error = "read_failed:" + b;
        return 0;
    }
    if (ba.size() != bb.size()) {
        out_error = "size_mismatch";
        return 0;
    }
    if (ba.empty()) return 1;
    if (std::memcmp(&ba[0], &bb[0], ba.size()) != 0) {
        out_error = "content_mismatch";
        return 0;
    }
    return 1;
}

static void print_args(const std::vector<std::string>& args)
{
    size_t i;
    for (i = 0u; i < args.size(); ++i) {
        if (i != 0u) {
            std::fprintf(stderr, " ");
        }
        std::fprintf(stderr, "%s", args[i].c_str());
    }
    std::fprintf(stderr, "\n");
}

static int run_process(const std::vector<std::string>& args)
{
    if (args.empty()) {
        return 0;
    }
#if defined(_WIN32)
    {
        std::string cmdline;
        size_t i;
        for (i = 0u; i < args.size(); ++i) {
            const std::string& arg = args[i];
            if (i != 0u) {
                cmdline.push_back(' ');
            }
            if (arg.find(' ') == std::string::npos && arg.find('\t') == std::string::npos) {
                cmdline += arg;
            } else {
                cmdline.push_back('"');
                cmdline += arg;
                cmdline.push_back('"');
            }
        }
        STARTUPINFOA si;
        PROCESS_INFORMATION pi;
        DWORD exit_code = 1;
        std::memset(&si, 0, sizeof(si));
        std::memset(&pi, 0, sizeof(pi));
        si.cb = sizeof(si);
        if (!CreateProcessA(NULL, &cmdline[0], NULL, NULL, FALSE, 0, NULL, NULL, &si, &pi)) {
            std::fprintf(stderr, "command failed: ");
            print_args(args);
            return 0;
        }
        WaitForSingleObject(pi.hProcess, INFINITE);
        GetExitCodeProcess(pi.hProcess, &exit_code);
        CloseHandle(pi.hProcess);
        CloseHandle(pi.hThread);
        if (exit_code != 0) {
            std::fprintf(stderr, "command failed: ");
            print_args(args);
            return 0;
        }
        return 1;
    }
#else
    pid_t pid = fork();
    if (pid < 0) {
        return 0;
    }
    if (pid == 0) {
        std::vector<char*> argv;
        size_t i;
        argv.reserve(args.size() + 1u);
        for (i = 0u; i < args.size(); ++i) {
            argv.push_back((char*)args[i].c_str());
        }
        argv.push_back((char*)0);
        execv(args[0].c_str(), &argv[0]);
        _exit(127);
    }
    {
        int status = 0;
        if (waitpid(pid, &status, 0) < 0) {
            return 0;
        }
        if (WIFEXITED(status) && WEXITSTATUS(status) == 0) {
            return 1;
        }
    }
    std::fprintf(stderr, "command failed: ");
    print_args(args);
    return 0;
#endif
}

static int write_text_file(const std::string& path, const std::string& text)
{
    FILE* f = std::fopen(path.c_str(), "wb");
    if (!f) return 0;
    if (!text.empty()) {
        if (std::fwrite(text.c_str(), 1u, text.size(), f) != text.size()) {
            std::fclose(f);
            return 0;
        }
    }
    std::fclose(f);
    return 1;
}

static std::string sanitize_doc_name(const std::string& in)
{
    std::string out;
    size_t i;
    for (i = 0u; i < in.size(); ++i) {
        unsigned char c = (unsigned char)in[i];
        if (std::isalnum(c)) {
            out.push_back((char)std::tolower(c));
        } else {
            out.push_back('_');
        }
    }
    if (out.empty()) {
        out = "doc";
    }
    if (out[0] >= '0' && out[0] <= '9') {
        out.insert(0u, "ui_");
    }
    return out;
}

static void skip_ws(const std::string& s, size_t& i)
{
    while (i < s.size() && std::isspace((unsigned char)s[i])) {
        ++i;
    }
}

static int parse_registry_actions(const std::string& path, std::map<std::string, unsigned>& out)
{
    std::vector<unsigned char> bytes;
    size_t i;
    size_t len;
    std::string s;
    out.clear();
    if (!read_file_bytes(path, bytes)) {
        return 0;
    }
    s.assign((const char*)&bytes[0], bytes.size());
    i = s.find("\"actions\"");
    if (i == std::string::npos) {
        return 0;
    }
    i = s.find('{', i);
    if (i == std::string::npos) {
        return 0;
    }
    ++i;
    len = s.size();
    while (i < len) {
        skip_ws(s, i);
        if (i >= len) break;
        if (s[i] == '}') {
            ++i;
            break;
        }
        if (s[i] != '"') {
            return 0;
        }
        ++i;
        {
            size_t start = i;
            while (i < len && s[i] != '"') {
                if (s[i] == '\\' && i + 1u < len) {
                    i += 2u;
                    continue;
                }
                ++i;
            }
            if (i >= len) return 0;
            std::string key = s.substr(start, i - start);
            ++i;
            skip_ws(s, i);
            if (i >= len || s[i] != ':') return 0;
            ++i;
            skip_ws(s, i);
            if (i >= len || !std::isdigit((unsigned char)s[i])) return 0;
            unsigned val = 0u;
            while (i < len && std::isdigit((unsigned char)s[i])) {
                val = val * 10u + (unsigned)(s[i] - '0');
                ++i;
            }
            out[key] = val;
            skip_ws(s, i);
            if (i < len && s[i] == ',') {
                ++i;
                continue;
            }
            if (i < len && s[i] == '}') {
                ++i;
                break;
            }
        }
    }
    return !out.empty();
}

static int run_apply_determinism(const Args& args)
{
    std::string run1 = join_path(args.work_dir, "run1");
    std::string run2 = join_path(args.work_dir, "run2");
    std::string base = args.doc_basename.empty() ? "ui_doc" : args.doc_basename;
    std::string doc1 = join_path(run1, base + ".tlv");
    std::string doc2 = join_path(run2, base + ".tlv");
    std::string err;
    std::vector<std::string> cmd;

    if (!ensure_dir_recursive(run1) || !ensure_dir_recursive(run2)) {
        std::fprintf(stderr, "apply: failed to create work dirs\n");
        return 1;
    }

    cmd.clear();
    cmd.push_back(args.ui_editor);
    cmd.push_back("--headless-apply");
    cmd.push_back(doc1);
    cmd.push_back("--script");
    cmd.push_back(args.script);
    cmd.push_back("--out");
    cmd.push_back(doc1);
    cmd.push_back("--in-new");
    if (!run_process(cmd)) {
        std::fprintf(stderr, "apply: command failed (run1)\n");
        return 1;
    }

    cmd.clear();
    cmd.push_back(args.ui_editor);
    cmd.push_back("--headless-apply");
    cmd.push_back(doc2);
    cmd.push_back("--script");
    cmd.push_back(args.script);
    cmd.push_back("--out");
    cmd.push_back(doc2);
    cmd.push_back("--in-new");
    if (!run_process(cmd)) {
        std::fprintf(stderr, "apply: command failed (run2)\n");
        return 1;
    }

    if (!compare_files(doc1, doc2, err)) {
        std::fprintf(stderr, "apply: tlv mismatch (%s)\n", err.c_str());
        return 1;
    }
    if (!compare_files(replace_ext(doc1, ".json"), replace_ext(doc2, ".json"), err)) {
        std::fprintf(stderr, "apply: json mismatch (%s)\n", err.c_str());
        return 1;
    }
    return 0;
}

static int run_codegen_determinism(const Args& args)
{
    std::string run1 = join_path(args.work_dir, "run1");
    std::string run2 = join_path(args.work_dir, "run2");
    std::string gen1 = join_path(run1, "gen");
    std::string gen2 = join_path(run2, "gen");
    std::string reg1 = join_path(run1, "registry.json");
    std::string reg2 = join_path(run2, "registry.json");
    std::string doc_sym = "ui_" + sanitize_doc_name(args.docname);
    std::string gen_cpp_1 = join_path(gen1, doc_sym + "_actions_gen.cpp");
    std::string gen_cpp_2 = join_path(gen2, doc_sym + "_actions_gen.cpp");
    std::string gen_h_1 = join_path(gen1, doc_sym + "_actions_gen.h");
    std::string gen_h_2 = join_path(gen2, doc_sym + "_actions_gen.h");
    std::string err;
    std::vector<std::string> cmd;

    if (!ensure_dir_recursive(gen1) || !ensure_dir_recursive(gen2)) {
        std::fprintf(stderr, "codegen: failed to create gen dirs\n");
        return 1;
    }

    cmd.clear();
    cmd.push_back(args.ui_editor);
    cmd.push_back("--headless-codegen");
    cmd.push_back("--in");
    cmd.push_back(args.doc);
    cmd.push_back("--out");
    cmd.push_back(gen1);
    cmd.push_back("--registry");
    cmd.push_back(reg1);
    cmd.push_back("--docname");
    cmd.push_back(args.docname);
    if (!run_process(cmd)) {
        std::fprintf(stderr, "codegen: command failed (run1)\n");
        return 1;
    }

    cmd.clear();
    cmd.push_back(args.ui_editor);
    cmd.push_back("--headless-codegen");
    cmd.push_back("--in");
    cmd.push_back(args.doc);
    cmd.push_back("--out");
    cmd.push_back(gen2);
    cmd.push_back("--registry");
    cmd.push_back(reg2);
    cmd.push_back("--docname");
    cmd.push_back(args.docname);
    if (!run_process(cmd)) {
        std::fprintf(stderr, "codegen: command failed (run2)\n");
        return 1;
    }

    if (!compare_files(gen_cpp_1, gen_cpp_2, err)) {
        std::fprintf(stderr, "codegen: cpp mismatch (%s)\n", err.c_str());
        return 1;
    }
    if (!compare_files(gen_h_1, gen_h_2, err)) {
        std::fprintf(stderr, "codegen: header mismatch (%s)\n", err.c_str());
        return 1;
    }
    return 0;
}

static int run_registry_stability(const Args& args)
{
    std::string work = args.work_dir;
    std::string doc = join_path(work, "reg_test_doc.tlv");
    std::string reg = join_path(work, "reg_test_registry.json");
    std::string script_full = join_path(work, "ops_full.json");
    std::string script_removed = join_path(work, "ops_removed.json");
    std::map<std::string, unsigned> actions;
    unsigned id_first = 0u;
    unsigned id_third = 0u;
    std::vector<std::string> cmd;

    if (!ensure_dir_recursive(work)) {
        std::fprintf(stderr, "registry: failed to create work dir\n");
        return 1;
    }

    {
        std::string full =
            "{\n"
            "  \"version\": 1,\n"
            "  \"docname\": \"test_ui\",\n"
            "  \"defaults\": { \"root_name\": \"root\" },\n"
            "  \"ops\": [\n"
            "    { \"op\": \"ensure_root\", \"name\": \"root\", \"type\": \"CONTAINER\" },\n"
            "    { \"op\": \"create_widget\", \"parent\": { \"path\": \"root\" }, \"type\": \"BUTTON\", \"name\": \"btn_a\", \"if_exists\": \"reuse\", \"out\": \"$a_id\" },\n"
            "    { \"op\": \"bind_event\", \"target\": { \"id\": \"$a_id\" }, \"event\": \"on_click\", \"action\": \"test.action.a\" },\n"
            "    { \"op\": \"create_widget\", \"parent\": { \"path\": \"root\" }, \"type\": \"BUTTON\", \"name\": \"btn_b\", \"if_exists\": \"reuse\", \"out\": \"$b_id\" },\n"
            "    { \"op\": \"bind_event\", \"target\": { \"id\": \"$b_id\" }, \"event\": \"on_click\", \"action\": \"test.action.b\" }\n"
            "  ]\n"
            "}\n";
        if (!write_text_file(script_full, full)) {
            std::fprintf(stderr, "registry: failed to write full ops\n");
            return 1;
        }
    }
    {
        std::string removed =
            "{\n"
            "  \"version\": 1,\n"
            "  \"docname\": \"test_ui\",\n"
            "  \"defaults\": { \"root_name\": \"root\" },\n"
            "  \"ops\": [\n"
            "    { \"op\": \"ensure_root\", \"name\": \"root\", \"type\": \"CONTAINER\" },\n"
            "    { \"op\": \"create_widget\", \"parent\": { \"path\": \"root\" }, \"type\": \"BUTTON\", \"name\": \"btn_b\", \"if_exists\": \"reuse\", \"out\": \"$b_id\" },\n"
            "    { \"op\": \"bind_event\", \"target\": { \"id\": \"$b_id\" }, \"event\": \"on_click\", \"action\": \"test.action.b\" }\n"
            "  ]\n"
            "}\n";
        if (!write_text_file(script_removed, removed)) {
            std::fprintf(stderr, "registry: failed to write removed ops\n");
            return 1;
        }
    }

    cmd.clear();
    cmd.push_back(args.ui_editor);
    cmd.push_back("--headless-apply");
    cmd.push_back(doc);
    cmd.push_back("--script");
    cmd.push_back(script_full);
    cmd.push_back("--out");
    cmd.push_back(doc);
    cmd.push_back("--in-new");
    if (!run_process(cmd)) {
        std::fprintf(stderr, "registry: apply full failed\n");
        return 1;
    }

    cmd.clear();
    cmd.push_back(args.ui_editor);
    cmd.push_back("--headless-codegen");
    cmd.push_back("--in");
    cmd.push_back(doc);
    cmd.push_back("--out");
    cmd.push_back(join_path(work, "gen"));
    cmd.push_back("--registry");
    cmd.push_back(reg);
    cmd.push_back("--docname");
    cmd.push_back("test_ui");
    if (!run_process(cmd)) {
        std::fprintf(stderr, "registry: codegen full failed\n");
        return 1;
    }
    if (!parse_registry_actions(reg, actions)) {
        std::fprintf(stderr, "registry: parse failed (full)\n");
        return 1;
    }
    if (actions.find("test.action.a") == actions.end()) {
        std::fprintf(stderr, "registry: missing action a\n");
        return 1;
    }
    id_first = actions["test.action.a"];

    cmd.clear();
    cmd.push_back(args.ui_editor);
    cmd.push_back("--headless-apply");
    cmd.push_back(doc);
    cmd.push_back("--script");
    cmd.push_back(script_removed);
    cmd.push_back("--out");
    cmd.push_back(doc);
    cmd.push_back("--in-new");
    if (!run_process(cmd)) {
        std::fprintf(stderr, "registry: apply removed failed\n");
        return 1;
    }

    cmd.clear();
    cmd.push_back(args.ui_editor);
    cmd.push_back("--headless-codegen");
    cmd.push_back("--in");
    cmd.push_back(doc);
    cmd.push_back("--out");
    cmd.push_back(join_path(work, "gen"));
    cmd.push_back("--registry");
    cmd.push_back(reg);
    cmd.push_back("--docname");
    cmd.push_back("test_ui");
    if (!run_process(cmd)) {
        std::fprintf(stderr, "registry: codegen removed failed\n");
        return 1;
    }

    cmd.clear();
    cmd.push_back(args.ui_editor);
    cmd.push_back("--headless-apply");
    cmd.push_back(doc);
    cmd.push_back("--script");
    cmd.push_back(script_full);
    cmd.push_back("--out");
    cmd.push_back(doc);
    cmd.push_back("--in-new");
    if (!run_process(cmd)) {
        std::fprintf(stderr, "registry: apply readd failed\n");
        return 1;
    }

    cmd.clear();
    cmd.push_back(args.ui_editor);
    cmd.push_back("--headless-codegen");
    cmd.push_back("--in");
    cmd.push_back(doc);
    cmd.push_back("--out");
    cmd.push_back(join_path(work, "gen"));
    cmd.push_back("--registry");
    cmd.push_back(reg);
    cmd.push_back("--docname");
    cmd.push_back("test_ui");
    if (!run_process(cmd)) {
        std::fprintf(stderr, "registry: codegen readd failed\n");
        return 1;
    }

    actions.clear();
    if (!parse_registry_actions(reg, actions)) {
        std::fprintf(stderr, "registry: parse failed (readd)\n");
        return 1;
    }
    if (actions.find("test.action.a") == actions.end()) {
        std::fprintf(stderr, "registry: missing action a after readd\n");
        return 1;
    }
    id_third = actions["test.action.a"];
    if (id_first != id_third) {
        std::fprintf(stderr, "registry: action id changed (%u -> %u)\n", id_first, id_third);
        return 1;
    }
    return 0;
}

static int run_scan_determinism(const Args& args)
{
    std::string out1 = join_path(args.work_dir, "ui_index_1.json");
    std::string out2 = join_path(args.work_dir, "ui_index_2.json");
    std::string err;
    std::vector<std::string> cmd;

    if (!ensure_dir_recursive(args.work_dir)) {
        std::fprintf(stderr, "scan: failed to create work dir\n");
        return 1;
    }

    cmd.clear();
    cmd.push_back(args.ui_editor);
    cmd.push_back("--scan-ui");
    cmd.push_back("--out");
    cmd.push_back(out1);
    if (!run_process(cmd)) {
        std::fprintf(stderr, "scan: command failed (run1)\n");
        return 1;
    }

    cmd.clear();
    cmd.push_back(args.ui_editor);
    cmd.push_back("--scan-ui");
    cmd.push_back("--out");
    cmd.push_back(out2);
    if (!run_process(cmd)) {
        std::fprintf(stderr, "scan: command failed (run2)\n");
        return 1;
    }

    if (!compare_files(out1, out2, err)) {
        std::fprintf(stderr, "scan: ui_index mismatch (%s)\n", err.c_str());
        return 1;
    }
    return 0;
}

static void print_usage()
{
    std::fprintf(stderr,
                 "usage: ui_cli_determinism_test --mode <apply_determinism|codegen_determinism|registry_stability|scan_determinism>\n"
                 "       --ui-editor <path> --work-dir <dir> [--script <ops.json>] [--doc <ui_doc.tlv>]\n"
                 "       [--docname <name>] [--doc-basename <base>]\n");
}

static int parse_args(int argc, char** argv, Args& out)
{
    int i;
    for (i = 1; i < argc; ++i) {
        const char* arg = argv[i];
        if (!arg) continue;
        if (std::strcmp(arg, "--mode") == 0 && i + 1 < argc) {
            out.mode = argv[++i];
        } else if (std::strcmp(arg, "--ui-editor") == 0 && i + 1 < argc) {
            out.ui_editor = argv[++i];
        } else if (std::strcmp(arg, "--script") == 0 && i + 1 < argc) {
            out.script = argv[++i];
        } else if (std::strcmp(arg, "--work-dir") == 0 && i + 1 < argc) {
            out.work_dir = argv[++i];
        } else if (std::strcmp(arg, "--doc") == 0 && i + 1 < argc) {
            out.doc = argv[++i];
        } else if (std::strcmp(arg, "--docname") == 0 && i + 1 < argc) {
            out.docname = argv[++i];
        } else if (std::strcmp(arg, "--doc-basename") == 0 && i + 1 < argc) {
            out.doc_basename = argv[++i];
        } else {
            std::fprintf(stderr, "unknown arg: %s\n", arg);
            return 0;
        }
    }
    if (!out.ui_editor.empty() && out.ui_editor[0] == '"' &&
        out.ui_editor[out.ui_editor.size() - 1u] == '"' && out.ui_editor.size() >= 2u) {
        out.ui_editor = out.ui_editor.substr(1u, out.ui_editor.size() - 2u);
    }
    if (!out.script.empty() && out.script[0] == '"' &&
        out.script[out.script.size() - 1u] == '"' && out.script.size() >= 2u) {
        out.script = out.script.substr(1u, out.script.size() - 2u);
    }
    if (!out.work_dir.empty() && out.work_dir[0] == '"' &&
        out.work_dir[out.work_dir.size() - 1u] == '"' && out.work_dir.size() >= 2u) {
        out.work_dir = out.work_dir.substr(1u, out.work_dir.size() - 2u);
    }
    if (!out.doc.empty() && out.doc[0] == '"' &&
        out.doc[out.doc.size() - 1u] == '"' && out.doc.size() >= 2u) {
        out.doc = out.doc.substr(1u, out.doc.size() - 2u);
    }
    if (out.mode.empty() || out.ui_editor.empty() || out.work_dir.empty()) {
        return 0;
    }
    return 1;
}

int main(int argc, char** argv)
{
    Args args;
    if (!parse_args(argc, argv, args)) {
        print_usage();
        return 2;
    }
    if (args.mode == "apply_determinism") {
        if (args.script.empty()) {
            print_usage();
            return 2;
        }
        return run_apply_determinism(args);
    }
    if (args.mode == "codegen_determinism") {
        if (args.doc.empty() || args.docname.empty()) {
            print_usage();
            return 2;
        }
        return run_codegen_determinism(args);
    }
    if (args.mode == "registry_stability") {
        return run_registry_stability(args);
    }
    if (args.mode == "scan_determinism") {
        return run_scan_determinism(args);
    }
    std::fprintf(stderr, "unknown mode: %s\n", args.mode.c_str());
    return 2;
}
