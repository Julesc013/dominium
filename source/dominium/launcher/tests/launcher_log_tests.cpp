/*
FILE: source/dominium/launcher/tests/launcher_log_tests.cpp
MODULE: Dominium
RESPONSIBILITY: Validates core_log round-trip encoding and launcher log routing/bounds.
*/
#include <cassert>
#include <cstdio>
#include <cstring>
#include <string>
#include <vector>

extern "C" {
#include "dominium/core_log.h"
#include "core/include/launcher_core_api.h"
}

#include "core/include/launcher_log.h"

namespace {

static bool is_sep(char c) {
    return c == '/' || c == '\\';
}

static std::string path_join(const std::string& a, const std::string& b) {
    if (a.empty()) return b;
    if (b.empty()) return a;
    if (is_sep(a[a.size() - 1u])) return a + b;
    return a + "/" + b;
}

static std::string u64_hex16(u64 v) {
    static const char* hex = "0123456789abcdef";
    char buf[17];
    int i;
    for (i = 0; i < 16; ++i) {
        unsigned shift = (unsigned)((15 - i) * 4);
        unsigned nib = (unsigned)((v >> shift) & 0xFu);
        buf[i] = hex[nib & 0xFu];
    }
    buf[16] = '\0';
    return std::string(buf);
}

static bool file_exists(const std::string& path) {
    FILE* f = std::fopen(path.c_str(), "rb");
    if (!f) return false;
    std::fclose(f);
    return true;
}

static long file_size(const std::string& path) {
    FILE* f = std::fopen(path.c_str(), "rb");
    long sz = -1;
    if (!f) return -1;
    if (std::fseek(f, 0, SEEK_END) == 0) {
        sz = std::ftell(f);
    }
    std::fclose(f);
    return sz;
}

struct MemSink {
    unsigned char* buf;
    u32 cap;
    u32 off;
};

static dom_abi_result mem_write(void* user, const void* data, u32 len) {
    MemSink* s = (MemSink*)user;
    if (!s || !data || len == 0u) {
        return 0;
    }
    if ((u64)s->off + (u64)len > (u64)s->cap) {
        return (dom_abi_result)-1;
    }
    std::memcpy(s->buf + s->off, data, len);
    s->off += len;
    return 0;
}

static void test_core_log_roundtrip(void) {
    core_log_event ev;
    core_log_event out;
    unsigned char buf[512];
    MemSink sink;
    core_log_write_sink ws;
    u32 used = 0u;
    char rel[CORE_LOG_MAX_PATH];

    core_log_event_clear(&ev);
    ev.domain = CORE_LOG_DOMAIN_LAUNCHER;
    ev.code = CORE_LOG_EVT_OP_OK;
    ev.severity = CORE_LOG_SEV_INFO;
    ev.flags = CORE_LOG_EVT_FLAG_NONE;
    ev.msg_id = 42u;
    ev.t_mono = 1234ull;
    (void)core_log_event_add_u32(&ev, CORE_LOG_KEY_OPERATION_ID, CORE_LOG_OP_LAUNCHER_LAUNCH_EXECUTE);
    (void)core_log_event_add_u64(&ev, CORE_LOG_KEY_RUN_ID, 0x1234ull);
    (void)core_log_event_add_msg_id(&ev, CORE_LOG_KEY_ERR_MSG_ID, 77u);

    std::memset(rel, 0, sizeof(rel));
    assert(core_log_path_make_relative("state", "state/logs/events.tlv", rel, sizeof(rel), 1) == 1);
    assert(std::strcmp(rel, "logs/events.tlv") == 0);

    sink.buf = buf;
    sink.cap = (u32)sizeof(buf);
    sink.off = 0u;
    ws.user = &sink;
    ws.write = mem_write;
    assert(core_log_event_write_tlv(&ev, &ws) == 0);

    assert(core_log_event_read_tlv(buf, sink.off, &out, &used) == 0);
    assert(used == sink.off);
    assert(out.domain == ev.domain);
    assert(out.code == ev.code);
    assert(out.severity == ev.severity);
    assert(out.msg_id == ev.msg_id);
    assert(out.field_count == ev.field_count);
}

static void test_log_routing_and_bounds(void) {
    const launcher_services_api_v1* services = launcher_services_null_v1();
    core_log_event ev;
    core_log_scope scope;
    const std::string state_root = "log_test_state";
    const std::string instance_id = "inst_log";
    const u64 run_id = 0x1ull;
    const std::string run_hex = u64_hex16(run_id);
    std::string run_path;
    std::string rolling_path;
    int i;

    core_log_event_clear(&ev);
    ev.domain = CORE_LOG_DOMAIN_LAUNCHER;
    ev.code = CORE_LOG_EVT_STATE;
    ev.severity = CORE_LOG_SEV_INFO;
    (void)core_log_event_add_u32(&ev, CORE_LOG_KEY_STATUS_CODE, 1u);

    std::memset(&scope, 0, sizeof(scope));
    scope.kind = CORE_LOG_SCOPE_RUN;
    scope.instance_id = instance_id.c_str();
    scope.run_id = run_id;
    scope.state_root = state_root.c_str();
    assert(launcher_services_emit_event(services, &scope, &ev) == 0);

    run_path = path_join(path_join(path_join(path_join(state_root, "instances"), instance_id), "logs/runs"), run_hex);
    run_path = path_join(run_path, "events.tlv");
    assert(file_exists(run_path));

    std::memset(&scope, 0, sizeof(scope));
    scope.kind = CORE_LOG_SCOPE_INSTANCE;
    scope.instance_id = instance_id.c_str();
    scope.state_root = state_root.c_str();
    for (i = 0; i < 2000; ++i) {
        assert(launcher_services_emit_event(services, &scope, &ev) == 0);
    }
    rolling_path = path_join(path_join(path_join(path_join(state_root, "instances"), instance_id), "logs/rolling"),
                             "events_rolling.tlv");
    {
        long sz = file_size(rolling_path);
        assert(sz >= 0);
        assert(sz <= (128 * 1024));
    }
}

} /* namespace */

int main(void) {
    test_core_log_roundtrip();
    test_log_routing_and_bounds();
    return 0;
}
