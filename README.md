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
# C++ 버전 (command 모드 - main 있음)
./bazel build //main:hello_world_wasi --config=wasi

# C 버전 (command 모드 - main 있음)
./bazel build //main:hello_world_wasi_c --config=wasi

# Reactor 모드 라이브러리 (main 없음, 함수만 export)
./bazel build //main:hello_world_wasi_lib --config=wasi
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

### 디렉토리 목록 출력 (CLI 인자 사용)

WASI 바이너리는 CLI 인자로 경로를 전달하면 해당 디렉토리 목록을 출력합니다:

```bash
# 루트 디렉토리 목록
wasmtime --dir=/ ./bazel-bin/main/hello_world_wasi_c /
wasmtime --dir=/ ./bazel-bin/main/hello_world_wasi /

# 특정 디렉토리 목록
wasmtime --dir=/home ./bazel-bin/main/hello_world_wasi /home
```

> **참고**: `--dir=<path>` 옵션은 wasmtime에 해당 경로에 대한 파일시스템 접근 권한을 부여합니다.

### 클라이언트 예제 (Node.js / Python)

Reactor 모드 라이브러리(`hello_world_wasi_lib`)를 사용하면 export된 함수를 직접 호출할 수 있습니다:

```bash
# Node.js
node examples/js/run_wasm.mjs              # say_hello() 호출
node examples/js/run_wasm.mjs --list-root  # list_root_directory() 호출

# Python (pip install wasmtime 필요)
python3 examples/python/run_wasm.py              # say_hello() 호출
python3 examples/python/run_wasm.py --list-root  # list_root_directory() 호출
```

## 빌드 타겟 목록

| 타겟 | 언어 | 플랫폼 | 모드 | 설명 |
|------|------|--------|------|------|
| `//main:hello_world` | C++ | 네이티브 | - | 기본 Hello World |
| `//main:hello_world_wasi` | C++ | WASI | Command | WebAssembly C++ 버전 |
| `//main:hello_world_wasi_c` | C | WASI | Command | WebAssembly C 버전 |
| `//main:hello_world_wasi_lib` | C++ | WASI | **Reactor** | 함수 직접 호출용 라이브러리 |

> **Command vs Reactor 모드**:
> - **Command**: `main()` 함수가 있고 `_start`로 실행 (wasmtime CLI용)
> - **Reactor**: `main()` 없이 함수만 export, `_initialize` 후 개별 함수 호출 가능 (클라이언트용)

## 프로젝트 구조

```
.
├── MODULE.bazel          # Bazel 모듈 설정 (WASI SDK 의존성)
├── .bazelrc              # Bazel 빌드 설정 (wasi config)
├── main/
│   ├── BUILD             # 빌드 타겟 정의
│   ├── hello_world.cc    # C++ 소스 (command 모드)
│   ├── hello_world_c.c   # C 소스 (command 모드)
│   └── hello_world_lib.cc # C++ 소스 (reactor 모드 라이브러리)
├── examples/
│   ├── js/
│   │   └── run_wasm.mjs      # Node.js WASI 클라이언트
│   └── python/
│       └── run_wasm.py       # Python WASI 클라이언트
├── platforms/
│   └── BUILD             # wasm32-wasi 플랫폼 정의
├── toolchain/
│   ├── BUILD                       # WASI CC 툴체인 등록
│   ├── wasi_sdk.BUILD              # WASI SDK 외부 저장소 BUILD
│   ├── wasi_sdk_paths.bzl          # WASI SDK 경로 생성 규칙
│   ├── wasi_cc_toolchain_config.bzl # CC 툴체인 설정
│   └── wrappers/                   # 컴파일러 래퍼 스크립트
└── docs/
    └── WASI_BAZEL_GUIDE.md   # WASI 빌드 가이드 문서
```
