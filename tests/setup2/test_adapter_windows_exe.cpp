#include "dsk/dsk_contracts.h"
#include "dsk/dsk_error.h"
#include "dsk/dsk_tlv.h"

#include <cstdio>
#include <cstring>
#include <string>
#include <vector>

#if defined(_WIN32)
#include <direct.h>
#include <process.h>
#endif

static int fail(const char *msg) {
    std::fprintf(stderr, "FAIL: %s\n", msg);
    return 1;
}

static int make_dir_if_needed(const std::string &path) {
#if defined(_WIN32)
    if (_mkdir(path.c_str()) == 0) {
        return 1;
    }
#endif
    return 1;
}

static std::string join_path(const std::string &dir, const char *name) {
    if (dir.empty()) {
        return name ? name : "";
    }
    if (!name || !name[0]) {
        return dir;
    }
    return dir + "\\" + name;
}

static int write_file(const std::string &path, const std::vector<dsk_u8> &data) {
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

static int read_file(const std::string &path, std::vector<dsk_u8> &out) {
    std::FILE *in = std::fopen(path.c_str(), "rb");
    size_t size;
    if (!in) {
        return 0;
    }
    std::fseek(in, 0, SEEK_END);
    size = (size_t)std::ftell(in);
    std::fseek(in, 0, SEEK_SET);
    out.resize(size);
    if (size > 0u && std::fread(&out[0], 1u, size, in) != size) {
        std::fclose(in);
        return 0;
    }
    std::fclose(in);
    return 1;
}

static int write_manifest(const std::string &path) {
    dsk_manifest_t manifest;
    dsk_tlv_buffer_t buf;
    dsk_status_t st;

    dsk_manifest_clear(&manifest);
    manifest.product_id = "dominium";
    manifest.version = "1.0.0";
    manifest.build_id = "test";
    manifest.supported_targets.push_back("win32_nt5");
    {
        dsk_layout_template_t layout;
        layout.template_id = "root_base";
        layout.target_root = "primary";
        layout.path_prefix = "app";
        manifest.layout_templates.push_back(layout);
    }
    {
        dsk_manifest_component_t comp;
        comp.component_id = "base";
        comp.kind = "runtime";
        comp.default_selected = DSK_TRUE;
        {
            dsk_artifact_t art;
            art.artifact_id = "base_art";
            art.hash = "hash";
            art.digest64 = 0x1111111111111111ULL;
            art.size = 1u;
            art.source_path = "base.dat";
            art.layout_template_id = "root_base";
            comp.artifacts.push_back(art);
        }
        manifest.components.push_back(comp);
    }

    st = dsk_manifest_write(&manifest, &buf);
    if (!dsk_error_is_ok(st)) {
        return 0;
    }
    {
        std::vector<dsk_u8> bytes(buf.data, buf.data + buf.size);
        dsk_tlv_buffer_free(&buf);
        return write_file(path, bytes);
    }
}

static int write_payload(const std::string &work_dir) {
    std::string payload_dir = join_path(work_dir, "payloads");
    std::string payload_path = join_path(payload_dir, "base.dat");
    std::vector<dsk_u8> data;
    data.push_back(0x61);
    data.push_back(0x62);
    data.push_back(0x63);
    if (!make_dir_if_needed(payload_dir)) {
        return 0;
    }
    return write_file(payload_path, data);
}

static int spawn_process(const std::string &exe, const std::vector<std::string> &args) {
#if defined(_WIN32)
    std::vector<const char *> argv;
    size_t i;
    argv.reserve(args.size() + 2u);
    argv.push_back(exe.c_str());
    for (i = 0u; i < args.size(); ++i) {
        argv.push_back(args[i].c_str());
    }
    argv.push_back(0);
    return _spawnvp(_P_WAIT, exe.c_str(), &argv[0]);
#else
    (void)exe;
    (void)args;
    return -1;
#endif
}

int main(int argc, char **argv) {
    if (argc < 4) {
        std::fprintf(stderr, "usage: test_adapter_windows_exe <setup2_cli> <adapter> <work_dir>\n");
        return 1;
    }
    {
        std::string cli = argv[1];
        std::string adapter = argv[2];
        std::string work_dir = argv[3];
        std::string manifest_path = join_path(work_dir, "manifest.tlv");
        std::string cli_request = join_path(work_dir, "cli_request.tlv");
        std::string adapter_request = join_path(work_dir, "adapter_request.tlv");
        std::vector<dsk_u8> a;
        std::vector<dsk_u8> b;
        std::vector<std::string> args;
        int code;

        if (!make_dir_if_needed(work_dir)) {
            return fail("failed to create work dir");
        }
        if (!write_manifest(manifest_path)) {
            return fail("failed to write manifest");
        }
        if (!write_payload(work_dir)) {
            return fail("failed to write payload");
        }

        args.clear();
        args.push_back("request");
        args.push_back("make");
        args.push_back("--manifest");
        args.push_back(manifest_path);
        args.push_back("--op");
        args.push_back("install");
        args.push_back("--scope");
        args.push_back("system");
        args.push_back("--ui-mode");
        args.push_back("cli");
        args.push_back("--root");
        args.push_back("install");
        args.push_back("--payload-root");
        args.push_back("payloads");
        args.push_back("--frontend-id");
        args.push_back("test-front");
        args.push_back("--platform");
        args.push_back("win32_nt5");
        args.push_back("--out-request");
        args.push_back(cli_request);
        args.push_back("--deterministic");
        args.push_back("1");
        args.push_back("--use-fake-services");
        args.push_back(work_dir);
        code = spawn_process(cli, args);
        if (code != 0) {
            return fail("dominium-setup2 request make failed");
        }

        args.clear();
        args.push_back("--cli");
        args.push_back("request-make");
        args.push_back("--manifest");
        args.push_back(manifest_path);
        args.push_back("--op");
        args.push_back("install");
        args.push_back("--scope");
        args.push_back("system");
        args.push_back("--frontend-id");
        args.push_back("test-front");
        args.push_back("--platform");
        args.push_back("win32_nt5");
        args.push_back("--payload-root");
        args.push_back("payloads");
        args.push_back("--root");
        args.push_back("install");
        args.push_back("--out-request");
        args.push_back(adapter_request);
        args.push_back("--deterministic");
        args.push_back("1");
        args.push_back("--use-fake-services");
        args.push_back(work_dir);
        args.push_back("--setup2-cli");
        args.push_back(cli);
        code = spawn_process(adapter, args);
        if (code != 0) {
            return fail("adapter request make failed");
        }

        if (!read_file(cli_request, a) || !read_file(adapter_request, b)) {
            return fail("failed to read request outputs");
        }
        if (a.size() != b.size() || std::memcmp(&a[0], &b[0], a.size()) != 0) {
            return fail("request bytes mismatch");
        }

        {
            std::string plan_path = join_path(work_dir, "install_plan.tlv");
            std::string state_path = join_path(work_dir, "installed_state.tlv");
            std::string audit_path = join_path(work_dir, "setup_audit.tlv");
            std::string journal_path = join_path(work_dir, "job_journal.tlv");

            args.clear();
            args.push_back("plan");
            args.push_back("--manifest");
            args.push_back(manifest_path);
            args.push_back("--request");
            args.push_back(adapter_request);
            args.push_back("--out-plan");
            args.push_back(plan_path);
            args.push_back("--use-fake-services");
            args.push_back(work_dir);
            code = spawn_process(cli, args);
            if (code != 0) {
                return fail("plan failed for adapter request");
            }

            args.clear();
            args.push_back("apply");
            args.push_back("--plan");
            args.push_back(plan_path);
            args.push_back("--out-state");
            args.push_back(state_path);
            args.push_back("--out-audit");
            args.push_back(audit_path);
            args.push_back("--out-journal");
            args.push_back(journal_path);
            args.push_back("--dry-run");
            args.push_back("--use-fake-services");
            args.push_back(work_dir);
            code = spawn_process(cli, args);
            if (code != 0) {
                return fail("apply failed for adapter request");
            }
        }
    }
    return 0;
}
