/*
FILE: source/tests/coredata_compile_schema_failure_test.cpp
MODULE: Dominium Tests
PURPOSE: Ensure coredata compiler refuses invalid references.
*/
#include <cstdio>
#include <string>
#include <vector>

#include "coredata_load.h"
#include "coredata_validate.h"

#ifndef COREDATA_FIXTURE_INVALID_ROOT
#define COREDATA_FIXTURE_INVALID_ROOT "tests/fixtures/coredata_invalid_missing_profile"
#endif

int main() {
    const std::string root = COREDATA_FIXTURE_INVALID_ROOT;
    dom::tools::CoredataData data;
    std::vector<dom::tools::CoredataError> errors;

    if (!dom::tools::coredata_load_all(root, data, errors)) {
        dom::tools::coredata_errors_print(errors);
        return 1;
    }
    if (dom::tools::coredata_validate(data, errors)) {
        std::fprintf(stderr, "validation unexpectedly succeeded\n");
        return 1;
    }
    return 0;
}
