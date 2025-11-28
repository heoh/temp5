# WASI SDK BUILD file
package(default_visibility = ["//visibility:public"])

filegroup(
    name = "all_files",
    srcs = glob(["**"]),
)

filegroup(
    name = "compiler_files",
    srcs = glob([
        "bin/**",
        "lib/**",
        "share/**",
    ]),
)

filegroup(
    name = "linker_files",
    srcs = glob([
        "bin/**",
        "lib/**",
        "share/**",
    ]),
)

filegroup(
    name = "ar_files",
    srcs = glob(["bin/llvm-ar*"]),
)

filegroup(
    name = "sysroot",
    srcs = glob(["share/wasi-sysroot/**"]),
)

filegroup(
    name = "clang_builtin_include",
    srcs = glob(["lib/clang/*/include/**"]),
)
