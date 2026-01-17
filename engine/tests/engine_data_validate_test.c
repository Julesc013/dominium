/*
Shared data validation tests (DATA1).
*/
#include <stdio.h>
#include <string.h>

#include "domino/io/data_validate.h"

#define EXPECT(cond, msg) do { \
    if (!(cond)) { \
        fprintf(stderr, "FAIL: %s\n", msg); \
        return 1; \
    } \
} while (0)

static void write_u32_le(unsigned char* p, u32 v) {
    p[0] = (unsigned char)(v & 0xFFu);
    p[1] = (unsigned char)((v >> 8) & 0xFFu);
    p[2] = (unsigned char)((v >> 16) & 0xFFu);
    p[3] = (unsigned char)((v >> 24) & 0xFFu);
}

static void write_u64_le(unsigned char* p, u64 v) {
    write_u32_le(p, (u32)(v & 0xFFFFFFFFu));
    write_u32_le(p + 4u, (u32)(v >> 32));
}

static int append_tlv(unsigned char* buf, u32 cap, u32* offset, u32 tag,
                      const void* payload, u32 payload_len) {
    if (!buf || !offset) {
        return -1;
    }
    if (*offset + 8u + payload_len > cap) {
        return -2;
    }
    write_u32_le(buf + *offset, tag);
    write_u32_le(buf + *offset + 4u, payload_len);
    *offset += 8u;
    if (payload_len > 0u && payload) {
        memcpy(buf + *offset, payload, payload_len);
        *offset += payload_len;
    }
    return 0;
}

static int build_valid_tlv(unsigned char* buf, u32 cap, u32* out_len) {
    u32 off = 0u;
    unsigned char tmp64[8];
    unsigned char tmp32[4];
    write_u64_le(tmp64, 42u);
    write_u32_le(tmp32, 10u);
    if (append_tlv(buf, cap, &off, 1u, tmp64, 8u) != 0) return -1;
    if (append_tlv(buf, cap, &off, 2u, tmp32, 4u) != 0) return -1;
    write_u32_le(tmp32, 2u);
    if (append_tlv(buf, cap, &off, 3u, tmp32, 4u) != 0) return -1;
    write_u64_le(tmp64, 7u);
    if (append_tlv(buf, cap, &off, 4u, tmp64, 8u) != 0) return -1;
    write_u32_le(tmp32, 99u);
    if (append_tlv(buf, cap, &off, 5u, tmp32, 4u) != 0) return -1;
    *out_len = off;
    return 0;
}

static int report_has_class(const dom_validation_report* report, dom_validation_class cls) {
    u32 i;
    if (!report) {
        return 0;
    }
    for (i = 0u; i < report->issue_count; ++i) {
        if (report->issues[i].cls == cls) {
            return 1;
        }
    }
    return 0;
}

static int test_accept(void) {
    unsigned char buf[256];
    u32 len = 0u;
    dom_validation_issue issues[16];
    dom_validation_report report;
    dom_schema_version version = {1u, 0u, 0u};
    dom_validation_result result;

    dom_data_schema_registry_reset();
    dom_data_schema_register_builtin();
    dom_validation_report_init(&report, issues, 16u);
    EXPECT(build_valid_tlv(buf, sizeof(buf), &len) == 0, "valid tlv build failed");

    result = dom_data_validate_tlv(buf, len, DOM_DATA_TEST_SCHEMA_ID, version,
                                   "valid", &report, 0);
    EXPECT(result == DOM_VALIDATION_ACCEPT, "expected ACCEPT");
    return 0;
}

static int test_structural_missing_field(void) {
    unsigned char buf[128];
    u32 off = 0u;
    unsigned char tmp32[4];
    dom_validation_issue issues[16];
    dom_validation_report report;
    dom_schema_version version = {1u, 0u, 0u};
    dom_validation_result result;

    dom_data_schema_registry_reset();
    dom_data_schema_register_builtin();
    dom_validation_report_init(&report, issues, 16u);

    write_u32_le(tmp32, 10u);
    append_tlv(buf, sizeof(buf), &off, 2u, tmp32, 4u);
    result = dom_data_validate_tlv(buf, off, DOM_DATA_TEST_SCHEMA_ID, version,
                                   "missing", &report, 0);
    EXPECT(result == DOM_VALIDATION_REFUSE, "missing required should refuse");
    EXPECT(report_has_class(&report, DOM_VALIDATION_SCHEMA), "expected schema error");
    return 0;
}

static int test_semantic_range(void) {
    unsigned char buf[128];
    u32 off = 0u;
    unsigned char tmp64[8];
    unsigned char tmp32[4];
    dom_validation_issue issues[16];
    dom_validation_report report;
    dom_schema_version version = {1u, 0u, 0u};
    dom_validation_result result;

    dom_data_schema_registry_reset();
    dom_data_schema_register_builtin();
    dom_validation_report_init(&report, issues, 16u);

    write_u64_le(tmp64, 1u);
    append_tlv(buf, sizeof(buf), &off, 1u, tmp64, 8u);
    write_u32_le(tmp32, 0u);
    append_tlv(buf, sizeof(buf), &off, 2u, tmp32, 4u);
    write_u32_le(tmp32, 1u);
    append_tlv(buf, sizeof(buf), &off, 3u, tmp32, 4u);
    write_u64_le(tmp64, 1u);
    append_tlv(buf, sizeof(buf), &off, 4u, tmp64, 8u);

    result = dom_data_validate_tlv(buf, off, DOM_DATA_TEST_SCHEMA_ID, version,
                                   "range", &report, 0);
    EXPECT(result == DOM_VALIDATION_REFUSE, "range violation should refuse");
    EXPECT(report_has_class(&report, DOM_VALIDATION_SEMANTIC), "expected semantic error");
    return 0;
}

static int test_determinism_order(void) {
    unsigned char buf[128];
    u32 off = 0u;
    unsigned char tmp64[8];
    unsigned char tmp32[4];
    dom_validation_issue issues[16];
    dom_validation_report report;
    dom_schema_version version = {1u, 0u, 0u};
    dom_validation_result result;

    dom_data_schema_registry_reset();
    dom_data_schema_register_builtin();
    dom_validation_report_init(&report, issues, 16u);

    write_u32_le(tmp32, 10u);
    append_tlv(buf, sizeof(buf), &off, 2u, tmp32, 4u);
    write_u64_le(tmp64, 1u);
    append_tlv(buf, sizeof(buf), &off, 1u, tmp64, 8u);
    write_u32_le(tmp32, 1u);
    append_tlv(buf, sizeof(buf), &off, 3u, tmp32, 4u);
    write_u64_le(tmp64, 1u);
    append_tlv(buf, sizeof(buf), &off, 4u, tmp64, 8u);

    result = dom_data_validate_tlv(buf, off, DOM_DATA_TEST_SCHEMA_ID, version,
                                   "order", &report, 0);
    EXPECT(result == DOM_VALIDATION_REFUSE, "order violation should refuse");
    EXPECT(report_has_class(&report, DOM_VALIDATION_DETERMINISM), "expected determinism error");
    return 0;
}

static int test_performance_repeat(void) {
    unsigned char buf[256];
    u32 off = 0u;
    unsigned char tmp64[8];
    unsigned char tmp32[4];
    dom_validation_issue issues[32];
    dom_validation_report report;
    dom_schema_version version = {1u, 0u, 0u};
    dom_validation_result result;
    u32 i;

    dom_data_schema_registry_reset();
    dom_data_schema_register_builtin();
    dom_validation_report_init(&report, issues, 32u);

    write_u64_le(tmp64, 1u);
    append_tlv(buf, sizeof(buf), &off, 1u, tmp64, 8u);
    write_u32_le(tmp32, 10u);
    append_tlv(buf, sizeof(buf), &off, 2u, tmp32, 4u);
    write_u32_le(tmp32, 1u);
    append_tlv(buf, sizeof(buf), &off, 3u, tmp32, 4u);
    write_u64_le(tmp64, 1u);
    append_tlv(buf, sizeof(buf), &off, 4u, tmp64, 8u);
    for (i = 0u; i < 9u; ++i) {
        write_u32_le(tmp32, 100u + i);
        append_tlv(buf, sizeof(buf), &off, 5u, tmp32, 4u);
    }

    result = dom_data_validate_tlv(buf, off, DOM_DATA_TEST_SCHEMA_ID, version,
                                   "repeat", &report, 0);
    EXPECT(result == DOM_VALIDATION_REFUSE, "repeat overflow should refuse");
    EXPECT(report_has_class(&report, DOM_VALIDATION_PERFORMANCE), "expected performance error");
    return 0;
}

static int test_migration_refusal(void) {
    unsigned char buf[256];
    u32 len = 0u;
    dom_validation_issue issues[16];
    dom_validation_report report;
    dom_schema_version version = {2u, 0u, 0u};
    dom_validation_result result;

    dom_data_schema_registry_reset();
    dom_data_schema_register_builtin();
    dom_validation_report_init(&report, issues, 16u);
    EXPECT(build_valid_tlv(buf, sizeof(buf), &len) == 0, "valid tlv build failed");

    result = dom_data_validate_tlv(buf, len, DOM_DATA_TEST_SCHEMA_ID, version,
                                   "migrate", &report, 0);
    EXPECT(result == DOM_VALIDATION_REFUSE, "major mismatch should refuse");
    EXPECT(report_has_class(&report, DOM_VALIDATION_MIGRATION), "expected migration error");
    return 0;
}

static int test_version_warning(void) {
    unsigned char buf[256];
    u32 len = 0u;
    dom_validation_issue issues[16];
    dom_validation_report report;
    dom_schema_version version = {1u, 1u, 0u};
    dom_validation_result result;

    dom_data_schema_registry_reset();
    dom_data_schema_register_builtin();
    dom_validation_report_init(&report, issues, 16u);
    EXPECT(build_valid_tlv(buf, sizeof(buf), &len) == 0, "valid tlv build failed");

    result = dom_data_validate_tlv(buf, len, DOM_DATA_TEST_SCHEMA_ID, version,
                                   "warn", &report, 0);
    EXPECT(result == DOM_VALIDATION_ACCEPT_WITH_WARNINGS, "minor mismatch should warn");
    return 0;
}

int main(void) {
    if (test_accept() != 0) {
        return 1;
    }
    if (test_structural_missing_field() != 0) {
        return 1;
    }
    if (test_semantic_range() != 0) {
        return 1;
    }
    if (test_determinism_order() != 0) {
        return 1;
    }
    if (test_performance_repeat() != 0) {
        return 1;
    }
    if (test_migration_refusal() != 0) {
        return 1;
    }
    if (test_version_warning() != 0) {
        return 1;
    }
    return 0;
}
