# temp5

Hello World 예제 프로젝트 (네이티브 + WASI 빌드 지원)

## 사전 요구사항

### Bazelisk 설치

```bash
wget -O bazel https://github.com/bazelbuild/bazelisk/releases/latest/download/bazelisk-linux-amd64
chmod +x bazel
```

### wasmtime 설치 (WASI 실행용)

```bash
curl https://wasmtime.dev/install.sh -sSf | bash
```

## 빌드 방법

### 네이티브 빌드

```bash
./bazel build //main:hello_world
```

### WASI (WebAssembly) 빌드

```bash
# C++ 버전
./bazel build //main:hello_world_wasi --config=wasi

# C 버전
./bazel build //main:hello_world_wasi_c --config=wasi
```

## 실행 방법

### 네이티브 실행

```bash
./bazel-bin/main/hello_world
# 출력: Hello World
```

### WASI 실행

```bash
# C++ 버전
wasmtime ./bazel-bin/main/hello_world_wasi
# 출력: Hello World

# C 버전
wasmtime ./bazel-bin/main/hello_world_wasi_c
# 출력: Hello World from WASI!
```

## 빌드 타겟 목록

| 타겟 | 언어 | 플랫폼 | 설명 |
|------|------|--------|------|
| `//main:hello_world` | C++ | 네이티브 | 기본 Hello World |
| `//main:hello_world_wasi` | C++ | WASI | WebAssembly C++ 버전 |
| `//main:hello_world_wasi_c` | C | WASI | WebAssembly C 버전 |

## 프로젝트 구조

```
.
├── MODULE.bazel          # Bazel 모듈 설정 (WASI SDK 의존성)
├── .bazelrc              # Bazel 빌드 설정 (wasi config)
├── main/
│   ├── BUILD             # 빌드 타겟 정의
│   ├── hello_world.cc    # C++ 소스
│   └── hello_world_c.c   # C 소스
├── platforms/
│   └── BUILD             # wasm32-wasi 플랫폼 정의
└── toolchain/
    ├── BUILD                       # WASI CC 툴체인 등록
    ├── wasi_sdk.BUILD              # WASI SDK 외부 저장소 BUILD
    ├── wasi_sdk_paths.bzl          # WASI SDK 경로 생성 규칙
    ├── wasi_cc_toolchain_config.bzl # CC 툴체인 설정
    └── wrappers/                   # 컴파일러 래퍼 스크립트
        ├── clang
        ├── wasm-ld
        ├── llvm-ar
        ├── llvm-nm
        ├── llvm-objdump
        └── llvm-strip
```
