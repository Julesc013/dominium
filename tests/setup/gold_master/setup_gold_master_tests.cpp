#include "dsk/dsk_audit.h"
#include "dsk/dsk_contracts.h"
#include "dsk/dsk_digest.h"
#include "dsk/dsk_error.h"
#include "dsk/dsk_jobs.h"
#include "dsk/dsk_plan.h"
#include "dss/dss_txn.h"

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <string>
#include <vector>

#if defined(_WIN32)
#include <direct.h>
#include <io.h>
#include <process.h>
#include <sys/stat.h>
#include <errno.h>
#else
#include <dirent.h>
#include <errno.h>
#include <sys/stat.h>
#include <unistd.h>
#endif

static int fail(const char *msg) {
    std::fprintf(stderr, "FAIL: %s\n", msg ? msg : "(null)");
    return 1;
}

static int make_dir_one(const std::string &path) {
#if defined(_WIN32)
    if (_mkdir(path.c_str()) == 0) {
        return 1;
    }
#else
    if (mkdir(path.c_str(), 0755) == 0) {
        return 1;
    }
#endif
    return errno == EEXIST;
}

static int is_drive_prefix(const std::string &path) {
#if defined(_WIN32)
    return path.size() == 2u && path[1] == ':';
#else
    (void)path;
    return 0;
#endif
}

static int is_drive_root(const std::string &path) {
#if defined(_WIN32)
    return path.size() == 3u && path[1] == ':' && (path[2] == '\\' || path[2] == '/');
#else
    (void)path;
    return 0;
#endif
}

static int make_dir_recursive(const std::string &path) {
    size_t i;
    std::string current;
    if (path.empty()) {
        return 0;
    }
    for (i = 0u; i <= path.size(); ++i) {
        char c = (i < path.size()) ? path[i] : '\0';
        if (c == '/' || c == '\\' || c == '\0') {
            if (!current.empty() && !is_drive_prefix(current) && !is_drive_root(current)) {
                if (!make_dir_one(current)) {
                    return 0;
                }
            }
        }
        if (c != '\0') {
            current.push_back(c);
        }
    }
    return 1;
}

static int remove_dir_recursive(const std::string &path) {
#if defined(_WIN32)
    std::string pattern = path + "\\*";
    struct _finddata_t data;
    intptr_t handle = _findfirst(pattern.c_str(), &data);
    if (handle == -1) {
        return (errno == ENOENT) ? 1 : 0;
    }
    do {
        const char *name = data.name;
        if (std::strcmp(name, ".") == 0 || std::strcmp(name, "..") == 0) {
            continue;
        }
        std::string child = path + "\\" + name;
        if (data.attrib & _A_SUBDIR) {
            if (!remove_dir_recursive(child)) {
                _findclose(handle);
                return 0;
            }
            _rmdir(child.c_str());
        } else {
            std::remove(child.c_str());
        }
    } while (_findnext(handle, &data) == 0);
    _findclose(handle);
    _rmdir(path.c_str());
    return 1;
#else
    DIR *dir = opendir(path.c_str());
    if (!dir) {
        return (errno == ENOENT) ? 1 : 0;
    }
    struct dirent *ent;
    while ((ent = readdir(dir)) != NULL) {
        const char *name = ent->d_name;
        if (std::strcmp(name, ".") == 0 || std::strcmp(name, "..") == 0) {
            continue;
        }
        std::string child = path + "/" + name;
        struct stat st;
        if (stat(child.c_str(), &st) != 0) {
            continue;
        }
        if (S_ISDIR(st.st_mode)) {
            if (!remove_dir_recursive(child)) {
                closedir(dir);
                return 0;
            }
            rmdir(child.c_str());
        } else {
            std::remove(child.c_str());
        }
    }
    closedir(dir);
    rmdir(path.c_str());
    return 1;
#endif
}

static std::string join_path(const std::string &a, const std::string &b) {
#if defined(_WIN32)
    const char sep = '\\';
#else
    const char sep = '/';
#endif
    if (a.empty()) {
        return b;
    }
    if (b.empty()) {
        return a;
    }
    if (a[a.size() - 1u] == '/' || a[a.size() - 1u] == '\\') {
        return a + b;
    }
    return a + sep + b;
}

static int read_file(const std::string &path, std::vector<unsigned char> &out) {
    std::FILE *in = std::fopen(path.c_str(), "rb");
    long size;
    if (!in) {
        return 0;
    }
    std::fseek(in, 0, SEEK_END);
    size = std::ftell(in);
    std::fseek(in, 0, SEEK_SET);
    if (size < 0) {
        std::fclose(in);
        return 0;
    }
    out.resize((size_t)size);
    if (size > 0 && std::fread(&out[0], 1u, (size_t)size, in) != (size_t)size) {
        std::fclose(in);
        return 0;
    }
    std::fclose(in);
    return 1;
}

static int write_file(const std::string &path, const std::vector<unsigned char> &data) {
    std::FILE *out = std::fopen(path.c_str(), "wb");
    if (!out) {
        return 0;
    }
    if (!data.empty()) {
        if (std::fwrite(&data[0], 1u, data.size(), out) != data.size()) {
            std::fclose(out);
            return 0;
        }
    }
    std::fclose(out);
    return 1;
}

static int copy_file(const std::string &src, const std::string &dst) {
    std::vector<unsigned char> data;
    if (!read_file(src, data)) {
        return 0;
    }
    return write_file(dst, data);
}

static int copy_fixture_set(const std::string &fixtures_root,
                            const std::string &sandbox_root) {
    static const char *k_files[] = {
        "manifest_v1.tlv",
        "request_quick.tlv",
        "request_custom.tlv",
        "payloads/v1/base.bin",
        "payloads/v1/extras.bin"
    };
    size_t i;
    for (i = 0u; i < sizeof(k_files) / sizeof(k_files[0]); ++i) {
        std::string src = join_path(fixtures_root, k_files[i]);
        std::string dst = join_path(sandbox_root, k_files[i]);
        std::string dir = dst;
        size_t pos = dir.find_last_of("/\\");
        if (pos != std::string::npos) {
            dir = dir.substr(0u, pos);
            if (!make_dir_recursive(dir)) {
                return 0;
            }
        }
        if (!copy_file(src, dst)) {
            return 0;
        }
    }
    return 1;
}

static std::string quote_arg(const std::string &arg) {
    if (arg.find(' ') == std::string::npos && arg.find('\t') == std::string::npos) {
        return arg;
    }
    std::string out = "\"";
    size_t i;
    for (i = 0u; i < arg.size(); ++i) {
        char c = arg[i];
        if (c == '"') {
            out += "\\\"";
        } else {
            out.push_back(c);
        }
    }
    out += "\"";
    return out;
}

static int run_cmd(const std::string &exe,
                   const std::vector<std::string> &args,
                   const std::string &stdout_path) {
#if defined(_WIN32)
    std::vector<const char *> argv;
    FILE *out = 0;
    int saved_fd = -1;
    int code;
    size_t i;
    argv.reserve(args.size() + 2u);
    argv.push_back(exe.c_str());
    for (i = 0u; i < args.size(); ++i) {
        argv.push_back(args[i].c_str());
    }
    argv.push_back(0);
    if (!stdout_path.empty()) {
        out = std::fopen(stdout_path.c_str(), "wb");
        if (!out) {
            return 0;
        }
        saved_fd = _dup(_fileno(stdout));
        if (saved_fd == -1) {
            std::fclose(out);
            return 0;
        }
        if (_dup2(_fileno(out), _fileno(stdout)) != 0) {
            _close(saved_fd);
            std::fclose(out);
            return 0;
        }
    }
    code = _spawnvp(_P_WAIT, exe.c_str(), &argv[0]);
    if (!stdout_path.empty()) {
        std::fflush(stdout);
        _dup2(saved_fd, _fileno(stdout));
        _close(saved_fd);
        std::fclose(out);
    }
    return code == 0;
#else
    std::string cmd = quote_arg(exe);
    size_t i;
    for (i = 0u; i < args.size(); ++i) {
        cmd += " ";
        cmd += quote_arg(args[i]);
    }
    if (!stdout_path.empty()) {
        cmd += " > ";
        cmd += quote_arg(stdout_path);
    }
    return std::system(cmd.c_str()) == 0;
#endif
}

static std::string json_escape(const std::string &value) {
    static const char *hex = "0123456789abcdef";
    std::string out;
    size_t i;
    out.reserve(value.size() + 8u);
    for (i = 0u; i < value.size(); ++i) {
        unsigned char c = (unsigned char)value[i];
        if (c == '\\') {
            out += "\\\\";
        } else if (c == '"') {
            out += "\\\"";
        } else if (c == '\n') {
            out += "\\n";
        } else if (c == '\r') {
            out += "\\r";
        } else if (c == '\t') {
            out += "\\t";
        } else if (c < 0x20u) {
            out += "\\u00";
            out += hex[(c >> 4) & 0x0Fu];
            out += hex[c & 0x0Fu];
        } else {
            out.push_back((char)c);
        }
    }
    return out;
}

static void append_u64(std::string &out, unsigned long long value) {
    char buf[32];
    std::sprintf(buf, "%llu", value);
    out += buf;
}

static void append_u32(std::string &out, unsigned long value) {
    char buf[32];
    std::sprintf(buf, "%lu", value);
    out += buf;
}

static unsigned long err_detail_u32(const dsk_error_t &err,
                                    unsigned long key,
                                    unsigned long default_value) {
    unsigned long i;
    for (i = 0u; i < (unsigned long)err.detail_count; ++i) {
        const err_detail_t *detail = &err.details[i];
        if (detail->key_id != key) {
            continue;
        }
        if (detail->type == ERR_DETAIL_TYPE_U32) {
            return (unsigned long)detail->v.u32_value;
        }
        if (detail->type == ERR_DETAIL_TYPE_MSG_ID) {
            return (unsigned long)detail->v.msg_id;
        }
        if (detail->type == ERR_DETAIL_TYPE_U64) {
            return (unsigned long)detail->v.u64_value;
        }
        break;
    }
    return default_value;
}

static int write_job_journal_json(const std::string &path, const dsk_job_journal_t &journal) {
    std::string json;
    size_t i;
    unsigned long subcode = err_detail_u32(journal.last_error, (unsigned long)ERR_DETAIL_KEY_SUBCODE, 0u);
    json += "{";
    json += "\"run_id\":";
    append_u64(json, (unsigned long long)journal.run_id);
    json += ",";
    json += "\"plan_digest64\":";
    append_u64(json, (unsigned long long)journal.plan_digest64);
    json += ",";
    json += "\"selected_splat_id\":\"" + json_escape(journal.selected_splat_id) + "\",";
    json += "\"stage_root\":\"" + json_escape(journal.stage_root) + "\",";
    json += "\"rollback_ref\":\"" + json_escape(journal.rollback_ref) + "\",";
    json += "\"last_error\":{";
    json += "\"domain\":";
    append_u32(json, (unsigned long)journal.last_error.domain);
    json += ",";
    json += "\"code\":";
    append_u32(json, (unsigned long)journal.last_error.code);
    json += ",";
    json += "\"subcode\":";
    append_u32(json, subcode);
    json += ",";
    json += "\"flags\":";
    append_u32(json, (unsigned long)journal.last_error.flags);
    json += ",";
    json += "\"msg_id\":";
    append_u32(json, (unsigned long)journal.last_error.msg_id);
    json += "},";
    json += "\"checkpoints\":[";
    for (i = 0u; i < journal.checkpoints.size(); ++i) {
        const dsk_job_checkpoint_t &cp = journal.checkpoints[i];
        if (i != 0u) json += ",";
        json += "{";
        json += "\"job_id\":";
        append_u32(json, (unsigned long)cp.job_id);
        json += ",";
        json += "\"status\":";
        append_u32(json, (unsigned long)cp.status);
        json += ",";
        json += "\"last_completed_step\":";
        append_u32(json, (unsigned long)cp.last_completed_step);
        json += "}";
    }
    json += "]";
    json += "}\n";
    {
        std::vector<unsigned char> bytes(json.begin(), json.end());
        return write_file(path, bytes);
    }
}

static int write_txn_journal_json(const std::string &path, const dss_txn_journal_t &journal) {
    std::string json;
    size_t i;
    json += "{";
    json += "\"plan_digest64\":";
    append_u64(json, (unsigned long long)journal.plan_digest64);
    json += ",";
    json += "\"stage_root\":\"" + json_escape(journal.stage_root) + "\",";
    json += "\"steps\":[";
    for (i = 0u; i < journal.steps.size(); ++i) {
        const dss_txn_step_t &step = journal.steps[i];
        if (i != 0u) json += ",";
        json += "{";
        json += "\"step_id\":";
        append_u32(json, (unsigned long)step.step_id);
        json += ",";
        json += "\"op_kind\":";
        append_u32(json, (unsigned long)step.op_kind);
        json += ",";
        json += "\"src\":\"" + json_escape(step.src_path) + "\",";
        json += "\"dst\":\"" + json_escape(step.dst_path) + "\",";
        json += "\"rollback_kind\":";
        append_u32(json, (unsigned long)step.rollback_kind);
        json += ",";
        json += "\"rollback_src\":\"" + json_escape(step.rollback_src) + "\",";
        json += "\"rollback_dst\":\"" + json_escape(step.rollback_dst) + "\"";
        json += "}";
    }
    json += "]";
    json += "}\n";
    {
        std::vector<unsigned char> bytes(json.begin(), json.end());
        return write_file(path, bytes);
    }
}

static dsk_u64 digest64_file(const std::string &path) {
    std::vector<unsigned char> bytes;
    if (!read_file(path, bytes)) {
        return 0u;
    }
    return dsk_digest64_bytes(bytes.empty() ? 0 : &bytes[0], (dsk_u32)bytes.size());
}

static int read_digest_file(const std::string &path,
                            std::vector<std::string> &files,
                            std::vector<dsk_u64> &digests) {
    std::ifstream in(path.c_str(), std::ios::in | std::ios::binary);
    std::string line;
    files.clear();
    digests.clear();
    if (!in) {
        return 0;
    }
    while (std::getline(in, line)) {
        size_t pos = line.find(' ');
        if (pos == std::string::npos) {
            continue;
        }
        std::string name = line.substr(0u, pos);
        std::string value = line.substr(pos + 1u);
        if (name.empty() || value.empty()) {
            continue;
        }
        dsk_u64 digest = 0u;
        std::sscanf(value.c_str(), "%llx", (unsigned long long *)&digest);
        files.push_back(name);
        digests.push_back(digest);
    }
    return 1;
}

static int write_digest_file(const std::string &path,
                             const std::vector<std::string> &files,
                             const std::vector<dsk_u64> &digests) {
    std::string out;
    size_t i;
    if (files.size() != digests.size()) {
        return 0;
    }
    for (i = 0u; i < files.size(); ++i) {
        char buf[64];
        std::snprintf(buf, sizeof(buf), "%llx", (unsigned long long)digests[i]);
        out += files[i] + " " + buf + "\n";
    }
    {
        std::vector<unsigned char> bytes(out.begin(), out.end());
        return write_file(path, bytes);
    }
}

static void gold_master_files(std::vector<std::string> &out) {
    static const char *k_files[] = {
        "manifest.tlv",
        "request_quick.tlv",
        "request_custom.tlv",
        "plan.tlv",
        "installed_state.tlv",
        "setup_audit.tlv",
        "job_journal.tlv",
        "txn_journal.tlv",
        "manifest.json",
        "request_quick.json",
        "request_custom.json",
        "plan.json",
        "installed_state.json",
        "setup_audit.json",
        "job_journal.json",
        "txn_journal.json"
    };
    size_t i;
    out.clear();
    for (i = 0u; i < sizeof(k_files) / sizeof(k_files[0]); ++i) {
        out.push_back(k_files[i]);
    }
}

static int generate_gold_master(const std::string &cli,
                                const std::string &fixtures_root,
                                const std::string &gold_root,
                                const std::string &sandbox_root,
                                int update) {
    std::string out_dir = join_path(sandbox_root, "out");
    std::string cli_local = join_path(sandbox_root,
#if defined(_WIN32)
                                      "dominium-setup.exe"
#else
                                      "dominium-setup"
#endif
    );
    std::string manifest_path = join_path(sandbox_root, "manifest_v1.tlv");
    std::string request_quick = join_path(sandbox_root, "request_quick.tlv");
    std::string request_custom = join_path(sandbox_root, "request_custom.tlv");
    std::string plan_path = join_path(out_dir, "plan.tlv");
    std::string state_path = join_path(out_dir, "installed_state.tlv");
    std::string audit_path = join_path(out_dir, "setup_audit.tlv");
    std::string journal_path = join_path(out_dir, "job_journal.tlv");
    std::string txn_path = journal_path + ".txn.tlv";

    remove_dir_recursive(sandbox_root);
    if (!make_dir_recursive(out_dir)) {
        return fail("failed to create gold master sandbox");
    }
    if (!copy_fixture_set(fixtures_root, sandbox_root)) {
        return fail("failed to copy fixtures");
    }
    if (!copy_file(cli, cli_local)) {
        return fail("failed to stage dominium-setup");
    }
    {
        std::vector<std::string> args;
        args.push_back("manifest");
        args.push_back("dump");
        args.push_back("--in");
        args.push_back(manifest_path);
        args.push_back("--out");
        args.push_back(join_path(out_dir, "manifest.json"));
        args.push_back("--format");
        args.push_back("json");
        args.push_back("--use-fake-services");
        args.push_back(sandbox_root);
        if (!run_cmd(cli_local, args, std::string())) {
            return fail("manifest dump failed");
        }
    }
    {
        std::vector<std::string> args;
        args.push_back("request");
        args.push_back("dump");
        args.push_back("--in");
        args.push_back(request_quick);
        args.push_back("--out");
        args.push_back(join_path(out_dir, "request_quick.json"));
        args.push_back("--format");
        args.push_back("json");
        args.push_back("--use-fake-services");
        args.push_back(sandbox_root);
        if (!run_cmd(cli_local, args, std::string())) {
            return fail("request quick dump failed");
        }
    }
    {
        std::vector<std::string> args;
        args.push_back("request");
        args.push_back("dump");
        args.push_back("--in");
        args.push_back(request_custom);
        args.push_back("--out");
        args.push_back(join_path(out_dir, "request_custom.json"));
        args.push_back("--format");
        args.push_back("json");
        args.push_back("--use-fake-services");
        args.push_back(sandbox_root);
        if (!run_cmd(cli_local, args, std::string())) {
            return fail("request custom dump failed");
        }
    }
    {
        std::vector<std::string> args;
        args.push_back("plan");
        args.push_back("--manifest");
        args.push_back(manifest_path);
        args.push_back("--request");
        args.push_back(request_quick);
        args.push_back("--out-plan");
        args.push_back(plan_path);
        args.push_back("--json");
        args.push_back("--use-fake-services");
        args.push_back(sandbox_root);
        args.push_back("--platform");
        args.push_back("win32_nt5");
        if (!run_cmd(cli_local, args, join_path(out_dir, "plan.json"))) {
            return fail("plan failed");
        }
    }
    {
        std::vector<std::string> args;
        args.push_back("apply");
        args.push_back("--plan");
        args.push_back(plan_path);
        args.push_back("--out-state");
        args.push_back(state_path);
        args.push_back("--out-audit");
        args.push_back(audit_path);
        args.push_back("--out-journal");
        args.push_back(journal_path);
        args.push_back("--use-fake-services");
        args.push_back(sandbox_root);
        args.push_back("--platform");
        args.push_back("win32_nt5");
        if (!run_cmd(cli_local, args, std::string())) {
            return fail("apply failed");
        }
    }
    {
        std::vector<std::string> args;
        args.push_back("audit");
        args.push_back("dump");
        args.push_back("--in");
        args.push_back(audit_path);
        args.push_back("--out");
        args.push_back(join_path(out_dir, "setup_audit.json"));
        args.push_back("--format");
        args.push_back("json");
        args.push_back("--use-fake-services");
        args.push_back(sandbox_root);
        if (!run_cmd(cli_local, args, std::string())) {
            return fail("audit dump failed");
        }
    }
    {
        std::vector<std::string> args;
        args.push_back("state");
        args.push_back("dump");
        args.push_back("--in");
        args.push_back(state_path);
        args.push_back("--out");
        args.push_back(join_path(out_dir, "installed_state.json"));
        args.push_back("--format");
        args.push_back("json");
        args.push_back("--use-fake-services");
        args.push_back(sandbox_root);
        if (!run_cmd(cli_local, args, std::string())) {
            return fail("state dump failed");
        }
    }

    {
        std::vector<unsigned char> bytes;
        dsk_job_journal_t journal;
        dss_txn_journal_t txn;
        dsk_status_t stj;
        dss_error_t stt;
        if (!read_file(journal_path, bytes)) {
            return fail("missing job journal");
        }
        dsk_job_journal_clear(&journal);
        stj = dsk_job_journal_parse(bytes.empty() ? 0 : &bytes[0], (dsk_u32)bytes.size(), &journal);
        if (!dsk_error_is_ok(stj)) {
            return fail("job journal parse failed");
        }
        if (!write_job_journal_json(join_path(out_dir, "job_journal.json"), journal)) {
            return fail("job journal json write failed");
        }

        bytes.clear();
        if (!read_file(txn_path, bytes)) {
            return fail("missing txn journal");
        }
        dss_txn_journal_clear(&txn);
        stt = dss_txn_journal_parse(bytes.empty() ? 0 : &bytes[0], (dss_u32)bytes.size(), &txn);
        if (!dss_error_is_ok(stt)) {
            return fail("txn journal parse failed");
        }
        if (!write_txn_journal_json(join_path(out_dir, "txn_journal.json"), txn)) {
            return fail("txn journal json write failed");
        }
    }

    if (update) {
        std::vector<std::string> files;
        std::vector<dsk_u64> digests;
        size_t i;
        gold_master_files(files);
        if (!make_dir_recursive(gold_root)) {
            return fail("failed to create gold master dir");
        }
        for (i = 0u; i < files.size(); ++i) {
            std::string src;
            if (files[i] == "manifest.tlv") src = manifest_path;
            else if (files[i] == "request_quick.tlv") src = request_quick;
            else if (files[i] == "request_custom.tlv") src = request_custom;
            else if (files[i] == "plan.tlv") src = plan_path;
            else if (files[i] == "installed_state.tlv") src = state_path;
            else if (files[i] == "setup_audit.tlv") src = audit_path;
            else if (files[i] == "job_journal.tlv") src = journal_path;
            else if (files[i] == "txn_journal.tlv") src = txn_path;
            else if (files[i] == "manifest.json") src = join_path(out_dir, "manifest.json");
            else if (files[i] == "request_quick.json") src = join_path(out_dir, "request_quick.json");
            else if (files[i] == "request_custom.json") src = join_path(out_dir, "request_custom.json");
            else if (files[i] == "plan.json") src = join_path(out_dir, "plan.json");
            else if (files[i] == "installed_state.json") src = join_path(out_dir, "installed_state.json");
            else if (files[i] == "setup_audit.json") src = join_path(out_dir, "setup_audit.json");
            else if (files[i] == "job_journal.json") src = join_path(out_dir, "job_journal.json");
            else if (files[i] == "txn_journal.json") src = join_path(out_dir, "txn_journal.json");
            else continue;
            if (!copy_file(src, join_path(gold_root, files[i]))) {
                return fail("failed to update gold master file");
            }
        }
        digests.resize(files.size());
        for (i = 0u; i < files.size(); ++i) {
            digests[i] = digest64_file(join_path(gold_root, files[i]));
        }
        if (!write_digest_file(join_path(gold_root, "digests.txt"), files, digests)) {
            return fail("failed to write digests.txt");
        }
        return 0;
    }

    {
        std::vector<std::string> files;
        size_t i;
        gold_master_files(files);
        for (i = 0u; i < files.size(); ++i) {
            std::vector<unsigned char> tmp;
            std::string gold_path = join_path(gold_root, files[i]);
            if (!read_file(gold_path, tmp)) {
                return fail("missing gold master file");
            }
        }
    }

    return 0;
}

static int check_gold_master_roundtrip(const std::string &gold_root) {
    std::vector<unsigned char> bytes;
    dsk_manifest_t manifest;
    dsk_request_t request;
    dsk_plan_t plan;
    dsk_installed_state_t state;
    dsk_audit_t audit;
    dsk_job_journal_t journal;
    dss_txn_journal_t txn;
    dsk_tlv_buffer_t buf;
    dsk_status_t st;
    dss_error_t stt;

    if (!read_file(join_path(gold_root, "manifest.tlv"), bytes)) return fail("read manifest.tlv");
    dsk_manifest_clear(&manifest);
    st = dsk_manifest_parse(bytes.empty() ? 0 : &bytes[0], (dsk_u32)bytes.size(), &manifest);
    if (!dsk_error_is_ok(st)) return fail("manifest parse");
    st = dsk_manifest_write(&manifest, &buf);
    if (!dsk_error_is_ok(st)) return fail("manifest write");
    dsk_tlv_buffer_free(&buf);

    if (!read_file(join_path(gold_root, "request_quick.tlv"), bytes)) return fail("read request_quick.tlv");
    dsk_request_clear(&request);
    st = dsk_request_parse(bytes.empty() ? 0 : &bytes[0], (dsk_u32)bytes.size(), &request);
    if (!dsk_error_is_ok(st)) return fail("request parse");
    st = dsk_request_write(&request, &buf);
    if (!dsk_error_is_ok(st)) return fail("request write");
    dsk_tlv_buffer_free(&buf);

    if (!read_file(join_path(gold_root, "plan.tlv"), bytes)) return fail("read plan.tlv");
    dsk_plan_clear(&plan);
    st = dsk_plan_parse(bytes.empty() ? 0 : &bytes[0], (dsk_u32)bytes.size(), &plan);
    if (!dsk_error_is_ok(st)) return fail("plan parse");
    st = dsk_plan_write(&plan, &buf);
    if (!dsk_error_is_ok(st)) return fail("plan write");
    dsk_tlv_buffer_free(&buf);

    if (!read_file(join_path(gold_root, "installed_state.tlv"), bytes)) return fail("read installed_state.tlv");
    dsk_installed_state_clear(&state);
    st = dsk_installed_state_parse(bytes.empty() ? 0 : &bytes[0], (dsk_u32)bytes.size(), &state);
    if (!dsk_error_is_ok(st)) return fail("state parse");
    st = dsk_installed_state_write(&state, &buf);
    if (!dsk_error_is_ok(st)) return fail("state write");
    dsk_tlv_buffer_free(&buf);

    if (!read_file(join_path(gold_root, "setup_audit.tlv"), bytes)) return fail("read setup_audit.tlv");
    dsk_audit_clear(&audit);
    st = dsk_audit_parse(bytes.empty() ? 0 : &bytes[0], (dsk_u32)bytes.size(), &audit);
    if (!dsk_error_is_ok(st)) return fail("audit parse");
    st = dsk_audit_write(&audit, &buf);
    if (!dsk_error_is_ok(st)) return fail("audit write");
    dsk_tlv_buffer_free(&buf);

    if (!read_file(join_path(gold_root, "job_journal.tlv"), bytes)) return fail("read job_journal.tlv");
    dsk_job_journal_clear(&journal);
    st = dsk_job_journal_parse(bytes.empty() ? 0 : &bytes[0], (dsk_u32)bytes.size(), &journal);
    if (!dsk_error_is_ok(st)) return fail("job journal parse");
    st = dsk_job_journal_write(&journal, &buf);
    if (!dsk_error_is_ok(st)) return fail("job journal write");
    dsk_tlv_buffer_free(&buf);

    if (!read_file(join_path(gold_root, "txn_journal.tlv"), bytes)) return fail("read txn_journal.tlv");
    dss_txn_journal_clear(&txn);
    stt = dss_txn_journal_parse(bytes.empty() ? 0 : &bytes[0], (dss_u32)bytes.size(), &txn);
    if (!dss_error_is_ok(stt)) return fail("txn journal parse");
    stt = dss_txn_journal_write(&txn, &buf);
    if (!dss_error_is_ok(stt)) return fail("txn journal write");
    dsk_tlv_buffer_free(&buf);

    return 0;
}

static int check_gold_master_digests(const std::string &gold_root) {
    std::vector<std::string> expected;
    std::vector<std::string> files;
    std::vector<dsk_u64> digests;
    size_t i;
    std::string digest_path = join_path(gold_root, "digests.txt");
    gold_master_files(expected);
    if (!read_digest_file(digest_path, files, digests)) {
        return fail("failed to read digests.txt");
    }
    if (files.size() != digests.size()) {
        return fail("digest list mismatch");
    }
    if (files.size() != expected.size()) {
        return fail("digest file count mismatch");
    }
    for (i = 0u; i < expected.size(); ++i) {
        if (files[i] != expected[i]) {
            return fail("digest file list mismatch");
        }
    }
    for (i = 0u; i < files.size(); ++i) {
        dsk_u64 actual = digest64_file(join_path(gold_root, files[i]));
        if (actual != digests[i]) {
            std::fprintf(stderr, "FAIL: digest mismatch for %s\n", files[i].c_str());
            return 1;
        }
    }
    return 0;
}

int main(int argc, char **argv) {
    if (argc < 5) {
        std::fprintf(stderr,
                     "usage: setup_gold_master_tests <mode> <dominium-setup> <fixtures_root> <gold_root> <sandbox_root> [--update]\n");
        return 1;
    }
    std::string mode = argv[1];
    std::string cli = argv[2];
    std::string fixtures_root = argv[3];
    std::string gold_root = argv[4];
    std::string sandbox_root = (argc > 5) ? argv[5] : "";
    int update = (argc > 6 && std::strcmp(argv[6], "--update") == 0) ? 1 : 0;

    if (mode == "generate") {
        return generate_gold_master(cli, fixtures_root, gold_root, sandbox_root, update);
    }
    if (mode == "roundtrip") {
        return check_gold_master_roundtrip(gold_root);
    }
    if (mode == "digests") {
        return check_gold_master_digests(gold_root);
    }
    std::fprintf(stderr, "unknown mode: %s\n", mode.c_str());
    return 1;
}
