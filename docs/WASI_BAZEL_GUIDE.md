# Bazel에서 WASI (WebAssembly System Interface) 빌드 가이드

이 문서는 Bazel 프로젝트에 wasm32-wasi 타겟 빌드를 추가하면서 얻은 지식과 노하우를 정리한 것입니다.

## 목차

1. [WASI란?](#wasi란)
2. [빌드 방법 비교](#빌드-방법-비교)
3. [WASI SDK 직접 사용 방법 (채택)](#wasi-sdk-직접-사용-방법-채택)
4. [시행착오 및 해결 방법](#시행착오-및-해결-방법)
5. [핵심 구현 포인트](#핵심-구현-포인트)

---

## WASI란?

**WASI (WebAssembly System Interface)**는 WebAssembly가 파일 시스템, 네트워크 등 시스템 리소스에 접근할 수 있게 해주는 표준 인터페이스입니다.

- **wasm32**: WebAssembly 32비트 아키텍처
- **wasi**: WASI 시스템 인터페이스를 사용하는 OS 레이어

WASI를 사용하면 브라우저 외부에서도 WebAssembly를 실행할 수 있으며, wasmtime, wasmer 등의 런타임으로 실행합니다.

---

## 빌드 방법 비교

Bazel에서 wasm32-wasi 타겟을 빌드하는 방법은 크게 3가지가 있습니다:

### 방법 1: WASI SDK 직접 사용 ✅ (채택)

```
WASI SDK = Clang + wasi-libc + libc++ + compiler-rt (모두 포함)
```

**장점:**
- 완전한 툴체인 제공 (컴파일러, 링커, sysroot, 런타임 라이브러리 모두 포함)
- C++도 문제없이 빌드 가능 (libc++ 포함)
- WebAssembly 공식 프로젝트로 안정적
- 버전 관리가 명확함

**단점:**
- 약 200MB 다운로드 필요
- 커스텀 cc_toolchain 설정 필요

### 방법 2: rules_wasm 사용

Aspect Build의 rules_wasm 사용.

**장점:**
- 비교적 간단한 설정

**단점:**
- Bazel 7+ 호환성 문제 있음
- bzlmod 지원 미흡
- 유지보수 불확실

### 방법 3: toolchains_llvm + WASI sysroot

toolchains_llvm에서 제공하는 LLVM과 별도 WASI sysroot 조합.

**장점:**
- 네이티브/WASI 툴체인을 하나로 관리

**단점:**
- ❌ **`<iostream>` 등 C++ 헤더 사용 불가** (wasi-sysroot에 libc++ 미포함)
- ❌ **compiler-rt builtins 누락** (`libclang_rt.builtins-wasm32.a` 없음)
- 결국 C 코드만 빌드 가능

### 결론

**방법 1 (WASI SDK 직접 사용)**이 가장 안정적이고 완전한 솔루션입니다.

---

## WASI SDK 직접 사용 방법 (채택)

### 전체 구조

```
project/
├── MODULE.bazel              # WASI SDK 다운로드 설정
├── .bazelrc                  # --config=wasi 설정
├── platforms/BUILD           # wasm32-wasi 플랫폼 정의
└── toolchain/
    ├── BUILD                 # cc_toolchain 등록
    ├── wasi_sdk.BUILD        # WASI SDK 외부 저장소 BUILD
    ├── wasi_sdk_paths.bzl    # 절대 경로 생성 repository_rule
    ├── wasi_cc_toolchain_config.bzl  # 툴체인 설정
    └── wrappers/             # 컴파일러 래퍼 스크립트
```

### 1. MODULE.bazel 설정

```python
# Dependencies
bazel_dep(name = "platforms", version = "0.0.10")
bazel_dep(name = "rules_cc", version = "0.1.0")

# WASI SDK 다운로드
http_archive = use_repo_rule("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

http_archive(
    name = "wasi_sdk",
    build_file = "//toolchain:wasi_sdk.BUILD",
    sha256 = "c6c38aab56e5de88adf6c1ebc9c3ae8da72f88ec2b656fb024eda8d4167a0bc5",
    strip_prefix = "wasi-sdk-24.0-x86_64-linux",
    url = "https://github.com/WebAssembly/wasi-sdk/releases/download/wasi-sdk-24/wasi-sdk-24.0-x86_64-linux.tar.gz",
)

# 절대 경로 생성을 위한 repository_rule
wasi_sdk_toolchain = use_repo_rule("//toolchain:wasi_sdk_paths.bzl", "wasi_sdk_toolchain")
wasi_sdk_toolchain(name = "wasi_sdk_paths")

# 툴체인 등록
register_toolchains("//toolchain:wasi_cc_toolchain")
```

### 2. 플랫폼 정의

```python
# platforms/BUILD
platform(
    name = "wasm32-wasi",
    constraint_values = [
        "@platforms//cpu:wasm32",
        "@platforms//os:wasi",
    ],
)
```

### 3. .bazelrc 설정

```
build:wasi --platforms=//platforms:wasm32-wasi
build:wasi --features=-layering_check
build:wasi --features=no_legacy_features
build:wasi --noincompatible_validate_top_level_header_inclusions
```

---

## 시행착오 및 해결 방법

### 문제 1: toolchains_llvm의 WASI 키 이름

**증상:**
```
'wasm32-wasi' is not a valid key
```

**원인:** toolchains_llvm 1.5.0에서 WASI 키 이름이 변경됨

**해결:** `wasm32-wasi` → `wasip1-wasm32` 사용

### 문제 2: wasi-sysroot에 libc++ 미포함

**증상:**
```
fatal error: 'iostream' file not found
```

**원인:** GitHub releases의 wasi-sysroot는 C 라이브러리만 포함하고, libc++는 미포함

**해결:** WASI SDK 전체를 사용 (libc++ 포함됨)

### 문제 3: compiler-rt builtins 누락

**증상:**
```
unable to find library -lclang_rt.builtins-wasm32
```

**원인:** 일반 LLVM 배포판에는 wasm32용 compiler-rt가 없음

**해결:** WASI SDK에 포함된 compiler-rt 사용

### 문제 4: 절대 경로 include 검사 실패

**증상:**
```
absolute path inclusion(s) found in rule
```

**원인:** Bazel이 `cxx_builtin_include_directories`에 지정된 경로와 실제 include 경로가 불일치

**해결:** repository_rule을 사용하여 WASI SDK의 절대 경로를 동적으로 생성

```python
# toolchain/wasi_sdk_paths.bzl
def _wasi_sdk_toolchain_impl(repository_ctx):
    wasi_sdk = repository_ctx.path(Label("@wasi_sdk//:BUILD")).dirname
    wasi_sdk_path = str(wasi_sdk)
    
    repository_ctx.file("paths.bzl", """
WASI_SDK_PATH = "{path}"
WASI_SYSROOT = "{path}/share/wasi-sysroot"
WASI_SYSROOT_INCLUDE = "{path}/share/wasi-sysroot/include"
WASI_CLANG_INCLUDE = "{path}/lib/clang/18/include"
""".format(path = wasi_sdk_path))
```

### 문제 5: Sandbox에서 컴파일러 경로 문제

**증상:**
```
No such file or directory: external/wasi_sdk/bin/clang
```

**원인:** Bazel sandbox에서 external repository 경로가 다르게 마운트됨

**해결:** Wrapper 스크립트로 동적 경로 탐색

```bash
#!/bin/bash
WASI_SDK_DIR="external/+_repo_rules+wasi_sdk"
if [ ! -d "$WASI_SDK_DIR" ]; then
    WASI_SDK_DIR="external/wasi_sdk"
fi
exec "$WASI_SDK_DIR/bin/clang" "$@"
```

### 문제 6: bzlmod에서 external repository 이름

**증상:** `@wasi_sdk` 대신 `@+_repo_rules+wasi_sdk` 같은 이름 사용

**원인:** bzlmod에서 `use_repo_rule`로 생성된 repository는 canonical 이름이 다름

**해결:** Wrapper 스크립트에서 두 경로 모두 시도

---

## 핵심 구현 포인트

### 1. cc_toolchain_config 필수 설정

```python
return cc_common.create_cc_toolchain_config_info(
    ctx = ctx,
    toolchain_identifier = "wasi-toolchain",
    host_system_name = "x86_64-linux",
    target_system_name = "wasm32-wasi",
    target_cpu = "wasm32",
    target_libc = "wasi",
    compiler = "clang",
    # 핵심: builtin_sysroot와 cxx_builtin_include_directories
    builtin_sysroot = WASI_SYSROOT,
    cxx_builtin_include_directories = [
        WASI_SYSROOT_INCLUDE,
        WASI_CLANG_INCLUDE,  # clang 내장 헤더 (stddef.h 등)
    ],
    ...
)
```

### 2. C++ 빌드를 위한 플래그

```python
# 컴파일 플래그
flags = [
    "--target=wasm32-wasi",
    "--sysroot=" + sysroot,
    "-fno-exceptions",  # WASI는 예외 지원 제한적
    "-stdlib=libc++",   # C++용
]

# 링크 플래그
flags = [
    "--target=wasm32-wasi",
    "--sysroot=" + sysroot,
    "-stdlib=libc++",
    "-lc++",
    "-lc++abi",
]
```

### 3. 타겟 호환성 선언

```python
cc_binary(
    name = "hello_world_wasi",
    srcs = ["hello_world.cc"],
    target_compatible_with = [
        "@platforms//os:wasi",
        "@platforms//cpu:wasm32",
    ],
)
```

---

## 참고 자료

- [WASI SDK GitHub](https://github.com/WebAssembly/wasi-sdk)
- [Bazel CC Toolchain 문서](https://bazel.build/docs/cc-toolchain-config-reference)
- [toolchains_llvm](https://github.com/bazel-contrib/toolchains_llvm)
- [wasmtime](https://wasmtime.dev/)
