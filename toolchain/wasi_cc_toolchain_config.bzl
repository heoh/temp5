"""WASI SDK cc_toolchain_config rule."""

load("@bazel_tools//tools/cpp:cc_toolchain_config_lib.bzl",
     "feature",
     "flag_group",
     "flag_set",
     "tool_path",
)
load("@bazel_tools//tools/build_defs/cc:action_names.bzl", "ACTION_NAMES")
load("@wasi_sdk_paths//:paths.bzl", "WASI_CLANG_INCLUDE", "WASI_SDK_PATH", "WASI_SYSROOT", "WASI_SYSROOT_INCLUDE")

all_compile_actions = [
    ACTION_NAMES.c_compile,
    ACTION_NAMES.cpp_compile,
    ACTION_NAMES.linkstamp_compile,
    ACTION_NAMES.assemble,
    ACTION_NAMES.preprocess_assemble,
    ACTION_NAMES.cpp_header_parsing,
    ACTION_NAMES.cpp_module_compile,
    ACTION_NAMES.cpp_module_codegen,
]

all_link_actions = [
    ACTION_NAMES.cpp_link_executable,
    ACTION_NAMES.cpp_link_dynamic_library,
    ACTION_NAMES.cpp_link_nodeps_dynamic_library,
]

def _wasi_cc_toolchain_config_impl(ctx):
    sysroot = ctx.attr.sysroot_path
    
    # Use pre-computed paths from repository rule
    wasi_sdk_root = WASI_SDK_PATH
    clang_include_root = WASI_CLANG_INCLUDE

    tool_paths = [
        tool_path(
            name = "gcc",
            path = ctx.attr.clang_path,
        ),
        tool_path(
            name = "ld",
            path = ctx.attr.wasm_ld_path,
        ),
        tool_path(
            name = "ar",
            path = ctx.attr.ar_path,
        ),
        tool_path(
            name = "cpp",
            path = ctx.attr.clang_path,
        ),
        tool_path(
            name = "gcov",
            path = "/bin/false",
        ),
        tool_path(
            name = "nm",
            path = ctx.attr.nm_path,
        ),
        tool_path(
            name = "objdump",
            path = ctx.attr.objdump_path,
        ),
        tool_path(
            name = "strip",
            path = ctx.attr.strip_path,
        ),
    ]

    default_compile_flags_feature = feature(
        name = "default_compile_flags",
        enabled = True,
        flag_sets = [
            flag_set(
                actions = all_compile_actions,
                flag_groups = [
                    flag_group(
                        flags = [
                            "--target=wasm32-wasi",
                            "--sysroot=" + sysroot,
                            "-fno-exceptions",
                        ],
                    ),
                ],
            ),
        ],
    )

    # C++ specific compile flags
    cxx_flags_feature = feature(
        name = "cxx_flags",
        enabled = True,
        flag_sets = [
            flag_set(
                actions = [ACTION_NAMES.cpp_compile],
                flag_groups = [
                    flag_group(
                        flags = [
                            "-stdlib=libc++",
                        ],
                    ),
                ],
            ),
        ],
    )

    default_link_flags_feature = feature(
        name = "default_link_flags",
        enabled = True,
        flag_sets = [
            flag_set(
                actions = all_link_actions,
                flag_groups = [
                    flag_group(
                        flags = [
                            "--target=wasm32-wasi",
                            "--sysroot=" + sysroot,
                            "-stdlib=libc++",
                            "-lc++",
                            "-lc++abi",
                        ],
                    ),
                ],
            ),
        ],
    )

    features = [
        default_compile_flags_feature,
        cxx_flags_feature,
        default_link_flags_feature,
    ]

    return cc_common.create_cc_toolchain_config_info(
        ctx = ctx,
        toolchain_identifier = "wasi-toolchain",
        host_system_name = "x86_64-linux",
        target_system_name = "wasm32-wasi",
        target_cpu = "wasm32",
        target_libc = "wasi",
        compiler = "clang",
        abi_version = "wasi",
        abi_libc_version = "wasi",
        tool_paths = tool_paths,
        features = features,
        builtin_sysroot = WASI_SYSROOT,
        cxx_builtin_include_directories = [
            WASI_SYSROOT_INCLUDE,
            WASI_CLANG_INCLUDE,
        ],
    )

wasi_cc_toolchain_config = rule(
    implementation = _wasi_cc_toolchain_config_impl,
    attrs = {
        "clang_path": attr.string(mandatory = True),
        "wasm_ld_path": attr.string(mandatory = True),
        "ar_path": attr.string(mandatory = True),
        "nm_path": attr.string(mandatory = True),
        "objdump_path": attr.string(mandatory = True),
        "strip_path": attr.string(mandatory = True),
        "sysroot_path": attr.string(mandatory = True),
    },
    provides = [CcToolchainConfigInfo],
)
