cmake_minimum_required(VERSION 3.15)

# Core engine and shared libs
add_subdirectory(core)

# Platform and renderer layers (currently skeletal; wired per-target later)
add_subdirectory(platform)
add_subdirectory(render)

# Internal tool libraries (separate from top-level /tools entrypoints)
add_subdirectory(tools)

# Product binaries (stubbed)
add_subdirectory(products)
