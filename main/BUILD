cc_binary(
    name = "hello_world",
    srcs = ["hello_world.cc"],
)

# WASI C++ target
cc_binary(
    name = "hello_world_wasi",
    srcs = ["hello_world.cc"],
    target_compatible_with = [
        "@platforms//os:wasi",
        "@platforms//cpu:wasm32",
    ],
)

# WASI C target
cc_binary(
    name = "hello_world_wasi_c",
    srcs = ["hello_world_c.c"],
    target_compatible_with = [
        "@platforms//os:wasi",
        "@platforms//cpu:wasm32",
    ],
)
