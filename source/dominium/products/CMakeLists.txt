cmake_minimum_required(VERSION 3.16)

# Legacy placeholder: active Dominium products now live under source/dominium/.
# This tree is kept only for historical reference and is not part of the
# primary build graph.

if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/_legacy")
    add_subdirectory(_legacy)
endif()
