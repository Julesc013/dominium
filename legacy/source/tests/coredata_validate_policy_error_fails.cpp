/*
FILE: source/tests/coredata_validate_policy_error_fails.cpp
MODULE: Dominium Tests
PURPOSE: Ensure coredata_validate rejects policy-violating authoring data.
*/
#include <cstdio>
#include <string>
#include <vector>

#include "coredata_validate_checks.h"
#include "coredata_validate_load.h"
#include "coredata_validate_report.h"
#include "coredata_compile/coredata_validate.h"

#ifndef COREDATA_FIXTURE_POLICY_INVALID_ROOT
#define COREDATA_FIXTURE_POLICY_INVALID_ROOT "tests/fixtures/coredata_invalid_candidate_progression"
#endif

int main() {
    const std::string root = COREDATA_FIXTURE_POLICY_INVALID_ROOT;
    dom::tools::CoredataValidationReport report;
    dom::tools::CoredataData data;
    std::vector<dom::tools::CoredataError> errors;

    dom::tools::coredata_report_init(report, "authoring", root);

    if (!dom::tools::coredata_validate_load_authoring(root, data, errors)) {
        dom::tools::coredata_validate_report_errors(errors, report);
    } else {
        dom::tools::coredata_validate_report_errors(errors, report);
        errors.clear();
        if (!dom::tools::coredata_validate(data, errors)) {
            dom::tools::coredata_validate_report_errors(errors, report);
        } else {
            dom::tools::coredata_validate_authoring_policy(data, report);
        }
    }

    if (report.error_count == 0u) {
        std::fprintf(stderr, "policy validation unexpectedly succeeded\n");
        return 1;
    }
    if (dom::tools::coredata_report_exit_code(report) != 13) {
        std::fprintf(stderr, "expected policy error exit code\n");
        return 1;
    }
    return 0;
}
