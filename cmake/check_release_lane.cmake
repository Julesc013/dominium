if(NOT DEFINED DOM_BUILD_KIND OR DOM_BUILD_KIND STREQUAL "")
    message(FATAL_ERROR "DIST_RELEASE_ONLY|build_kind_missing")
endif()

if(NOT DOM_BUILD_KIND MATCHES "^(release|beta|rc|hotfix)$")
    message(FATAL_ERROR "DIST_RELEASE_ONLY|invalid_build_kind|${DOM_BUILD_KIND}")
endif()

if(NOT DEFINED DOM_BUILD_GBN OR DOM_BUILD_GBN STREQUAL "" OR DOM_BUILD_GBN STREQUAL "none")
    message(FATAL_ERROR "DIST_RELEASE_ONLY|missing_gbn")
endif()
