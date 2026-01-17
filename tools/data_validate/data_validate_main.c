/*
FILE: tools/data_validate/data_validate_main.c
MODULE: Dominium
PURPOSE: Data validation CLI (shared validator entry point).
*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "domino/io/data_validate.h"

static void usage(void) {
    printf("Usage: data_validate --input=<path> --schema-id=<u64> --schema-version=M.m.p\n");
    printf("                      [--strict=1] [--max-records=N]\n");
}

static int read_file_bytes(const char* path, unsigned char** out_bytes, u32* out_len) {
    FILE* f;
    long size;
    size_t read;
    unsigned char* buf;
    if (!path || !out_bytes || !out_len) {
        return -1;
    }
    *out_bytes = (unsigned char*)0;
    *out_len = 0u;
    f = fopen(path, "rb");
    if (!f) {
        return -2;
    }
    if (fseek(f, 0, SEEK_END) != 0) {
        fclose(f);
        return -3;
    }
    size = ftell(f);
    if (size < 0) {
        fclose(f);
        return -4;
    }
    if (fseek(f, 0, SEEK_SET) != 0) {
        fclose(f);
        return -5;
    }
    buf = (unsigned char*)malloc((size_t)size);
    if (!buf && size != 0) {
        fclose(f);
        return -6;
    }
    read = 0u;
    if (size > 0) {
        read = fread(buf, 1u, (size_t)size, f);
        if (read != (size_t)size) {
            free(buf);
            fclose(f);
            return -7;
        }
    }
    fclose(f);
    *out_bytes = buf;
    *out_len = (u32)size;
    return 0;
}

static int parse_version(const char* s, dom_schema_version* out) {
    char* end;
    unsigned long v;
    if (!s || !out) {
        return -1;
    }
    v = strtoul(s, &end, 10);
    if (!end || *end != '.') {
        return -2;
    }
    out->major = (u16)v;
    s = end + 1;
    v = strtoul(s, &end, 10);
    if (!end || *end != '.') {
        return -3;
    }
    out->minor = (u16)v;
    s = end + 1;
    v = strtoul(s, &end, 10);
    if (!end || *end != '\0') {
        return -4;
    }
    out->patch = (u16)v;
    return 0;
}

static int parse_u64(const char* s, u64* out) {
    char* end;
    unsigned long long v;
    if (!s || !out) {
        return -1;
    }
    v = strtoull(s, &end, 0);
    if (!end || *end != '\0') {
        return -2;
    }
    *out = (u64)v;
    return 0;
}

static const char* issue_check_id(const dom_validation_issue* issue) {
    if (!issue) {
        return "DATA-VALID-001";
    }
    if (strncmp(issue->code, "schema_meta_", 12) == 0) {
        return "DATA-SCHEMA-001";
    }
    if (strncmp(issue->code, "schema_version_", 15) == 0) {
        return "DATA-SCHEMA-002";
    }
    if (issue->cls == DOM_VALIDATION_MIGRATION) {
        return "DATA-MIGRATE-001";
    }
    if (issue->cls == DOM_VALIDATION_DETERMINISM || issue->cls == DOM_VALIDATION_PERFORMANCE) {
        return "DATA-VALID-002";
    }
    return "DATA-VALID-001";
}

static void print_group(const char* id,
                        const char* description,
                        const char* fix,
                        const dom_validation_report* report) {
    u32 i;
    int printed = 0;
    for (i = 0u; report && i < report->issue_count; ++i) {
        const dom_validation_issue* issue = &report->issues[i];
        if (strcmp(issue_check_id(issue), id) != 0) {
            continue;
        }
        if (!printed) {
            printf("%s: %s\n", id, description);
            printed = 1;
        }
        printf("  %s:%u: %s: %s\n",
               issue->path[0] ? issue->path : "<input>",
               (unsigned)issue->line,
               issue->code,
               issue->message);
    }
    if (printed && fix && fix[0]) {
        printf("Fix: %s\n", fix);
    }
}

int main(int argc, char** argv) {
    const char* input_path = 0;
    const char* version_str = 0;
    const char* schema_str = 0;
    int strict = 1;
    u32 max_records = 0u;
    int i;
    u64 schema_id = 0u;
    dom_schema_version version;
    unsigned char* bytes = 0;
    u32 len = 0u;
    dom_validation_issue issues[128];
    dom_validation_report report;
    dom_data_validate_options options;
    dom_validation_result result;

    for (i = 1; i < argc; ++i) {
        const char* arg = argv[i] ? argv[i] : "";
        if (strncmp(arg, "--input=", 8) == 0) {
            input_path = arg + 8;
        } else if (strncmp(arg, "--schema-id=", 12) == 0) {
            schema_str = arg + 12;
        } else if (strncmp(arg, "--schema-version=", 17) == 0) {
            version_str = arg + 17;
        } else if (strncmp(arg, "--strict=", 9) == 0) {
            strict = (arg[9] != '0');
        } else if (strncmp(arg, "--max-records=", 14) == 0) {
            max_records = (u32)strtoul(arg + 14, 0, 10);
        } else if (strcmp(arg, "--help") == 0 || strcmp(arg, "-h") == 0) {
            usage();
            return 0;
        } else {
            fprintf(stderr, "Unknown arg: %s\n", arg);
            usage();
            return 2;
        }
    }

    if (!input_path) {
        fprintf(stderr, "Missing --input\n");
        usage();
        return 2;
    }
    if (!schema_str || !version_str) {
        fprintf(stderr, "Missing --schema-id or --schema-version\n");
        usage();
        return 2;
    }
    if (parse_u64(schema_str, &schema_id) != 0) {
        fprintf(stderr, "Invalid --schema-id\n");
        return 2;
    }
    if (parse_version(version_str, &version) != 0) {
        fprintf(stderr, "Invalid --schema-version (use M.m.p)\n");
        return 2;
    }

    dom_data_schema_register_builtin();
    dom_validation_report_init(&report, issues, 128u);
    if (read_file_bytes(input_path, &bytes, &len) != 0) {
        dom_validation_report_add(&report, DOM_VALIDATION_IO, DOM_VALIDATION_SEV_ERROR,
                                  "file_read_failed", "failed to read input",
                                  input_path, 0u);
        result = dom_validation_report_result(&report);
    } else {
        options.max_records = max_records;
        options.require_canon_order = 1;
        options.warn_unknown_tags = 1;
        result = dom_data_validate_tlv(bytes, len, schema_id, version,
                                       input_path, &report, &options);
    }

    print_group("DATA-VALID-001",
                "structural/semantic validation failure",
                "Fix schema field presence, types, or ranges.",
                &report);
    print_group("DATA-VALID-002",
                "determinism/performance validation failure",
                "Remove nondeterministic constructs or unbounded lists.",
                &report);
    print_group("DATA-SCHEMA-001",
                "missing schema metadata",
                "Provide schema_id and schema_version metadata.",
                &report);
    print_group("DATA-SCHEMA-002",
                "invalid schema version progression",
                "Fix version progression or add migration guidance.",
                &report);
    print_group("DATA-MIGRATE-001",
                "missing or required migration",
                "Add a deterministic migration or update versioning policy.",
                &report);

    if (bytes) {
        free(bytes);
    }

    if (result == DOM_VALIDATION_REFUSE) {
        return 1;
    }
    if (result == DOM_VALIDATION_ACCEPT_WITH_WARNINGS && strict) {
        return 3;
    }
    return 0;
}
