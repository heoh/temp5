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

# WASI Reactor 모드 라이브러리 (main 없음, 함수만 export)
# 클라이언트에서 개별 함수를 직접 호출할 수 있음
cc_binary(
    name = "hello_world_wasi_lib",
    srcs = ["hello_world_lib.cc"],
    linkopts = ["-mexec-model=reactor"],
    target_compatible_with = [
        "@platforms//os:wasi",
        "@platforms//cpu:wasm32",
    ],
)
