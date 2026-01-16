/*
No-modal-loading enforcement tests (IO ban + stall watchdog + derived jobs).
*/
#include "domino/sys.h"
#include "domino/system/dsys_guard.h"

#include <string.h>

static int dsys_test_starts_with(const char* text, const char* prefix)
{
    size_t i = 0u;
    if (!text || !prefix) {
        return 0;
    }
    while (prefix[i]) {
        if (text[i] != prefix[i]) {
            return 0;
        }
        ++i;
    }
    return 1;
}

static size_t dsys_test_append(char* dst, size_t cap, size_t pos, const char* src)
{
    size_t len;
    if (!dst || cap == 0u || pos >= cap) {
        return pos;
    }
    if (!src) {
        return pos;
    }
    len = strlen(src);
    if (len + pos >= cap) {
        len = cap - pos - 1u;
    }
    memcpy(dst + pos, src, len);
    dst[pos + len] = '\0';
    return pos + len;
}

static size_t dsys_test_append_char(char* dst, size_t cap, size_t pos, char ch)
{
    if (!dst || cap == 0u || pos + 1u >= cap) {
        return pos;
    }
    dst[pos++] = ch;
    dst[pos] = '\0';
    return pos;
}

static int dsys_test_build_report_dir(char* out, size_t cap, const char* run_root)
{
    size_t pos = 0u;
    if (!out || cap == 0u || !run_root || !run_root[0]) {
        return 0;
    }
    out[0] = '\0';
    pos = dsys_test_append(out, cap, pos, run_root);
    if (pos > 0u && out[pos - 1u] != '/' && out[pos - 1u] != '\\') {
        pos = dsys_test_append_char(out, cap, pos, '/');
    }
    pos = dsys_test_append(out, cap, pos, "perf");
    pos = dsys_test_append_char(out, cap, pos, '/');
    pos = dsys_test_append(out, cap, pos, "no_modal_loading");
    return (pos > 0u) ? 1 : 0;
}

static int dsys_test_dir_has_prefix(const char* dir, const char* prefix)
{
    dsys_dir_iter* it;
    dsys_dir_entry ent;
    int found = 0;

    if (!dir || !prefix) {
        return 0;
    }

    it = dsys_dir_open(dir);
    if (!it) {
        return 0;
    }
    while (dsys_dir_next(it, &ent)) {
        if (dsys_test_starts_with(ent.name, prefix)) {
            found = 1;
            break;
        }
    }
    dsys_dir_close(it);
    return found;
}

static int test_io_ban(void)
{
    const char* run_root = "run_root_perf_ioban";
    char report_dir[260];
    void* fh;

    dsys_guard_set_run_root(run_root);
    dsys_guard_set_io_enabled(1);
    dsys_guard_set_act_time_us(123u);
    dsys_guard_set_sim_tick(456u);

    dsys_thread_tag_current("ui_test", DSYS_THREAD_FLAG_NO_BLOCK);
    fh = dsys_file_open("io_ban_probe.txt", "rb");
    if (fh != NULL) {
        dsys_thread_clear_current();
        return 1;
    }
    if (dsys_guard_get_io_violation_count() == 0u) {
        dsys_thread_clear_current();
        return 1;
    }
    dsys_thread_clear_current();

    if (!dsys_test_build_report_dir(report_dir, sizeof(report_dir), run_root)) {
        return 1;
    }
    if (!dsys_test_dir_has_prefix(report_dir, "PERF-IOBAN-001_")) {
        return 1;
    }
    return 0;
}

static void test_job_fn(void* user)
{
    int* flag = (int*)user;
    if (flag) {
        *flag = 1;
    }
}

static int test_derived_jobs(void)
{
    int ran = 0;
    dsys_derived_job_desc desc;

    dsys_thread_tag_current("ui_test", DSYS_THREAD_FLAG_NO_BLOCK);
    desc.fn = test_job_fn;
    desc.user = &ran;
    desc.tag = "derived_test";
    if (dsys_derived_job_submit(&desc) != 0) {
        dsys_thread_clear_current();
        return 1;
    }
    if (ran != 0) {
        dsys_thread_clear_current();
        return 1;
    }
    if (dsys_derived_job_pending() == 0u) {
        dsys_thread_clear_current();
        return 1;
    }
    dsys_thread_clear_current();
    if (dsys_derived_job_run_next() != 1) {
        return 1;
    }
    if (ran != 1) {
        return 1;
    }
    return 0;
}

static int test_stall_watchdog(void)
{
    const char* run_root = "run_root_perf_stall";
    char report_dir[260];

    dsys_guard_set_run_root(run_root);
    dsys_stall_watchdog_reset();
    dsys_stall_watchdog_set_enabled(1);
    dsys_stall_watchdog_set_threshold_ms(1);

    dsys_thread_tag_current("ui_test", DSYS_THREAD_FLAG_NO_BLOCK);
    dsys_stall_watchdog_frame_begin("stall_test");
    dsys_sleep_ms(5u);
    dsys_stall_watchdog_frame_end();
    if (!dsys_stall_watchdog_was_triggered()) {
        dsys_thread_clear_current();
        return 1;
    }
    dsys_thread_clear_current();

    if (!dsys_test_build_report_dir(report_dir, sizeof(report_dir), run_root)) {
        return 1;
    }
    if (!dsys_test_dir_has_prefix(report_dir, "PERF-STALL-001_")) {
        return 1;
    }
    return 0;
}

int main(void)
{
    if (test_io_ban() != 0) {
        return 1;
    }
    if (test_stall_watchdog() != 0) {
        return 1;
    }
    if (test_derived_jobs() != 0) {
        return 1;
    }
    return 0;
}
