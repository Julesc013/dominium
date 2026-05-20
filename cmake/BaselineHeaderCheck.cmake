function(dominium_baseline_header_check root_dir)
    if(NOT IS_DIRECTORY "${root_dir}")
        message(FATAL_ERROR "BaselineHeaderCheck: not a directory: ${root_dir}")
    endif()

    file(GLOB_RECURSE header_files
        LIST_DIRECTORIES false
        "${root_dir}/*.h"
        "${root_dir}/*.hpp"
        "${root_dir}/*.hh"
        "${root_dir}/*.inl"
    )
    list(SORT header_files)

    set(violations "")

    foreach(header_path IN LISTS header_files)
        file(RELATIVE_PATH rel "${CMAKE_SOURCE_DIR}" "${header_path}")
        string(REPLACE "\\" "/" rel "${rel}")

        file(STRINGS "${header_path}" lines)
        set(line_no 0)
        set(in_block_comment 0)
        foreach(line IN LISTS lines)
            math(EXPR line_no "${line_no} + 1")

            # Escape list separators in diagnostic output.
            set(line_disp "${line}")
            string(REPLACE ";" "\\;" line_disp "${line_disp}")

            # ------------------------------------------------------------
            # Comment stripping (avoid false positives from doc blocks)
            # ------------------------------------------------------------
            set(line_scan "${line}")

            # If we're currently inside a /* ... */ block, ignore until the closing */.
            if(in_block_comment)
                if(line_scan MATCHES "\\*/")
                    # Drop up to and including the first */ and keep scanning the remainder.
                    string(REGEX REPLACE "^.*\\*/" "" line_scan "${line_scan}")
                    set(in_block_comment 0)
                else()
                    continue()
                endif()
            endif()

            # Strip any /* ... */ segments on this line; enter block mode if unterminated.
            if(line_scan MATCHES "/\\*")
                if(line_scan MATCHES "/\\*.*\\*/")
                    string(REGEX REPLACE "/\\*.*\\*/" "" line_scan "${line_scan}")
                else()
                    string(REGEX REPLACE "/\\*.*$" "" line_scan "${line_scan}")
                    set(in_block_comment 1)
                endif()
            endif()

            # Strip // comments for token scanning.
            if(line_scan MATCHES "//")
                string(REGEX REPLACE "//.*$" "" line_scan "${line_scan}")
            endif()

            # ------------------------------------------------------------
            # Forbidden includes (baseline-visible public headers)
            # ------------------------------------------------------------
            foreach(inc IN ITEMS vector string map set unordered_map unordered_set list deque array memory functional future thread mutex optional variant any stdexcept filesystem memory_resource charconv)
                if(line_scan MATCHES "^[ \t]*#[ \t]*include[ \t]*<${inc}>")
                    list(APPEND violations "${rel}:${line_no}: forbidden C++ library include in public C ABI header: <${inc}>: ${line_disp}")
                endif()
            endforeach()
            foreach(inc IN ITEMS windows.h winsock.h winsock2.h unistd.h pthread.h vulkan/vulkan.h SDL.h SDL2/SDL.h)
                if(line_scan MATCHES "^[ \t]*#[ \t]*include[ \t]*<${inc}>")
                    list(APPEND violations "${rel}:${line_no}: forbidden platform include in public engine header: <${inc}>: ${line_disp}")
                endif()
            endforeach()

        endforeach()
    endforeach()

    if(violations)
        list(JOIN violations "\n" violations_text)
        message(FATAL_ERROR
            "Baseline header check failed.\n"
            "Baseline-visible headers must avoid forbidden C++ library and platform header leakage.\n"
            "C ABI shape is enforced by tools/validators/abi/check_public_headers.py.\n\n"
            "${violations_text}\n"
        )
    endif()
endfunction()
