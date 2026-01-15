/*
FILE: source/dominium/tools/coredata_validate/coredata_validate_report.h
MODULE: Dominium
PURPOSE: Coredata validation report structures and formatting.
*/
#ifndef DOMINIUM_TOOLS_COREDATA_VALIDATE_REPORT_H
#define DOMINIUM_TOOLS_COREDATA_VALIDATE_REPORT_H

#include <string>
#include <vector>

extern "C" {
#include "domino/core/types.h"
}

namespace dom {
namespace tools {

enum CoredataValidationClass {
    CORE_DATA_SCHEMA_ERROR = 1,
    CORE_DATA_REFERENCE_ERROR = 2,
    CORE_DATA_DETERMINISM_ERROR = 3,
    CORE_DATA_POLICY_ERROR = 4,
    CORE_DATA_RANGE_ERROR = 5,
    CORE_DATA_MIGRATION_ERROR = 6
};

enum CoredataValidationSeverity {
    CORE_DATA_SEVERITY_ERROR = 1,
    CORE_DATA_SEVERITY_WARNING = 2
};

struct CoredataValidationIssue {
    CoredataValidationClass cls;
    CoredataValidationSeverity severity;
    std::string code;
    std::string message;
    std::string path;
    int line;
};

struct CoredataValidationReport {
    std::string tool_version;
    std::string mode;
    std::string input_path;
    std::vector<CoredataValidationIssue> issues;
    u32 error_count;
    u32 warning_count;

    CoredataValidationReport();
};

void coredata_report_init(CoredataValidationReport &report,
                          const std::string &mode,
                          const std::string &input_path);

void coredata_report_add_issue(CoredataValidationReport &report,
                               CoredataValidationClass cls,
                               CoredataValidationSeverity severity,
                               const std::string &code,
                               const std::string &message,
                               const std::string &path,
                               int line);

void coredata_report_sort(CoredataValidationReport &report);

int coredata_report_exit_code(const CoredataValidationReport &report);

std::string coredata_report_text(const CoredataValidationReport &report);
std::string coredata_report_json(const CoredataValidationReport &report);
std::vector<unsigned char> coredata_report_tlv(const CoredataValidationReport &report);

bool coredata_report_has_error_class(const CoredataValidationReport &report,
                                     CoredataValidationClass cls);

bool coredata_report_has_io_error(const CoredataValidationReport &report);

} // namespace tools
} // namespace dom

#endif /* DOMINIUM_TOOLS_COREDATA_VALIDATE_REPORT_H */
