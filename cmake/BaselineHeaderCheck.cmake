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

        set(is_c89_header 0)
        if(rel MATCHES "^include/domino/")
            set(is_c89_header 1)
        endif()

        file(STRINGS "${header_path}" lines)
        set(line_no 0)
        foreach(line IN LISTS lines)
            math(EXPR line_no "${line_no} + 1")

            # Escape list separators in diagnostic output.
            set(line_disp "${line}")
            string(REPLACE ";" "\\;" line_disp "${line_disp}")

            # ------------------------------------------------------------
            # Forbidden includes (baseline-visible public headers)
            # ------------------------------------------------------------
            if(line MATCHES "<stdint\\.h>")
                list(APPEND violations "${rel}:${line_no}: forbidden include: <stdint.h>: ${line_disp}")
            endif()
            if(line MATCHES "<stdbool\\.h>")
                list(APPEND violations "${rel}:${line_no}: forbidden include: <stdbool.h>: ${line_disp}")
            endif()

            # ------------------------------------------------------------
            # Forbidden keywords / constructs
            # ------------------------------------------------------------
            foreach(kw IN ITEMS constexpr nullptr noexcept override final thread_local auto inline)
                if(line MATCHES "(^|[^A-Za-z0-9_])${kw}([^A-Za-z0-9_]|$)")
                    list(APPEND violations "${rel}:${line_no}: forbidden token: ${kw}: ${line_disp}")
                endif()
            endforeach()

            if(line MATCHES "long[ \t]+long")
                list(APPEND violations "${rel}:${line_no}: forbidden token: long long: ${line_disp}")
            endif()

            if(line MATCHES "\\.[A-Za-z_][A-Za-z0-9_]*[ \t]*=")
                list(APPEND violations "${rel}:${line_no}: forbidden C99 designated initializer: ${line_disp}")
            endif()

            # C89 headers must not use // comments.
            if(is_c89_header AND line MATCHES "//")
                list(APPEND violations "${rel}:${line_no}: forbidden C++-style comment in C89 header: ${line_disp}")
            endif()
        endforeach()
    endforeach()

    if(violations)
        list(JOIN violations "\n" violations_text)
        message(FATAL_ERROR
            "Baseline header check failed.\n"
            "Baseline-visible headers must remain C89/C++98 compatible.\n\n"
            "${violations_text}\n"
        )
    endif()
endfunction()

