# WASI Preopen (사전 디렉토리 열기) 가이드

이 문서는 WASI에서 파일시스템 접근을 위해 필수적인 **preopen** 개념과 클라이언트에서의 사용 방법을 설명합니다.

## 목차

1. [Preopen이란?](#preopen이란)
2. [왜 Preopen이 필요한가?](#왜-preopen이-필요한가)
3. [클라이언트별 Preopen 설정](#클라이언트별-preopen-설정)
4. [경로 매핑 이해하기](#경로-매핑-이해하기)
5. [보안 고려사항](#보안-고려사항)

---

## Preopen이란?

**Preopen**은 WASI(WebAssembly System Interface)에서 WebAssembly 모듈이 접근할 수 있는 디렉토리를 **사전에 열어두는** 메커니즘입니다.

일반적인 네이티브 프로그램과 달리, WASI 모듈은 **기본적으로 어떤 파일이나 디렉토리에도 접근할 수 없습니다**. 호스트(런타임)가 명시적으로 허용한 디렉토리만 접근할 수 있습니다.

```
┌─────────────────────────────────────────────────────────┐
│                    호스트 시스템                          │
│  ┌─────────────────────────────────────────────────┐   │
│  │              WASI 런타임 (wasmtime, Node.js 등)    │   │
│  │  ┌─────────────────────────────────────────┐   │   │
│  │  │           WebAssembly 모듈               │   │   │
│  │  │                                         │   │   │
│  │  │  opendir("/")  ──────────────────────►  │   │   │
│  │  │                                         │   │   │
│  │  └─────────────────────────────────────────┘   │   │
│  │                     │                          │   │
│  │                     ▼                          │   │
│  │            Preopen 테이블 조회                   │   │
│  │            "/" → "/home/user/sandbox"          │   │
│  │                     │                          │   │
│  │                     ▼                          │   │
│  │            호스트 디렉토리 접근                   │   │
│  └─────────────────────────────────────────────────┘   │
│                        │                               │
│                        ▼                               │
│              /home/user/sandbox/ 실제 접근              │
└─────────────────────────────────────────────────────────┘
```

---

## 왜 Preopen이 필요한가?

### 1. 샌드박스 보안 모델

WASI는 **Capability-based Security** 모델을 사용합니다. 이는 "기본 거부(deny by default)" 원칙을 따릅니다:

- ❌ WASI 모듈은 기본적으로 파일시스템에 접근할 수 없음
- ✅ 호스트가 명시적으로 허용한 디렉토리만 접근 가능

### 2. 최소 권한 원칙

Preopen을 통해 WASI 모듈에게 **필요한 최소한의 권한**만 부여할 수 있습니다:

```python
# 나쁜 예: 전체 시스템에 접근 허용
wasi_config.preopen_dir("/", "/")

# 좋은 예: 필요한 디렉토리만 허용
wasi_config.preopen_dir("/app/data", "/data")
wasi_config.preopen_dir("/app/config", "/config")
```

### 3. 경로 가상화

호스트의 실제 경로를 WASI 모듈 내에서 다른 경로로 매핑할 수 있습니다:

| 호스트 경로 | WASI 내부 경로 |
|------------|---------------|
| `/home/user/project/sandbox` | `/` |
| `/tmp/wasi_tmp` | `/tmp` |
| `/var/data/app` | `/data` |

---

## 클라이언트별 Preopen 설정

### wasmtime CLI

```bash
# 단일 디렉토리 매핑
wasmtime --dir=/path/to/host/dir::/ program.wasm

# 여러 디렉토리 매핑
wasmtime --dir=/host/data::/data --dir=/host/config::/config program.wasm

# 형식: --dir=<호스트경로>::<WASI경로>
```

### Node.js

```javascript
import { WASI } from 'node:wasi';

const wasi = new WASI({
  version: 'preview1',
  preopens: {
    // 키: WASI 내부 경로, 값: 호스트 실제 경로
    '/': '/path/to/sandbox',           // 루트를 샌드박스로 매핑
    '/data': '/home/user/app/data',    // /data를 실제 데이터 폴더로 매핑
    '/tmp': '/tmp/wasi_sandbox',       // /tmp를 임시 폴더로 매핑
  },
});
```

**주의**: Node.js의 `preopens` 객체에서:
- **키(key)**: WASI 모듈이 사용할 가상 경로
- **값(value)**: 호스트 시스템의 실제 경로

### Python (wasmtime 패키지)

```python
from wasmtime import WasiConfig

wasi_config = WasiConfig()

# preopen_dir(호스트_경로, WASI_경로)
wasi_config.preopen_dir("/path/to/sandbox", "/")
wasi_config.preopen_dir("/home/user/data", "/data")
wasi_config.preopen_dir("/tmp/wasi", "/tmp")

store.set_wasi(wasi_config)
```

**주의**: Python wasmtime의 `preopen_dir` 메서드에서:
- **첫 번째 인자**: 호스트 시스템의 실제 경로
- **두 번째 인자**: WASI 모듈이 사용할 가상 경로

---

## 경로 매핑 이해하기

### 예시: 더미 루트 사용

이 프로젝트의 예제에서는 실제 시스템 루트(`/`) 대신 더미 루트 디렉토리를 사용합니다:

```
examples/dummy_root/
├── bin/
├── etc/
│   └── config.txt
├── home/
│   └── user/
│       └── hello.txt
├── tmp/
└── var/
    └── log/
        └── app.log
```

**Node.js 설정:**
```javascript
const dummyRootPath = '/path/to/examples/dummy_root';

const wasi = new WASI({
  preopens: { '/': dummyRootPath },  // 더미 루트를 "/" 로 매핑
});
```

**Python 설정:**
```python
dummy_root = "/path/to/examples/dummy_root"
wasi_config.preopen_dir(dummy_root, "/")  # 더미 루트를 "/" 로 매핑
```

**WASI 모듈 내부에서의 동작:**
```c
// WASI 모듈 코드
opendir("/");           // → 실제로는 examples/dummy_root/ 를 열음
opendir("/etc");        // → 실제로는 examples/dummy_root/etc/ 를 열음
fopen("/etc/config.txt", "r");  // → examples/dummy_root/etc/config.txt
```

### 매핑 테이블 예시

| WASI 모듈 요청 경로 | Preopen 매핑 | 실제 호스트 경로 |
|-------------------|-------------|-----------------|
| `/` | `/` → `examples/dummy_root` | `examples/dummy_root/` |
| `/etc/config.txt` | `/` → `examples/dummy_root` | `examples/dummy_root/etc/config.txt` |
| `/home/user` | `/` → `examples/dummy_root` | `examples/dummy_root/home/user/` |

---

## 보안 고려사항

### ⚠️ 절대 하지 말아야 할 것

```python
# 위험: 전체 시스템 루트 노출
wasi_config.preopen_dir("/", "/")

# 위험: 민감한 디렉토리 노출
wasi_config.preopen_dir("/etc", "/etc")
wasi_config.preopen_dir(os.path.expanduser("~"), "/home")
```

### ✅ 권장 사항

1. **최소 권한 원칙**: 필요한 디렉토리만 노출

   ```python
   # 애플리케이션에 필요한 디렉토리만 노출
   wasi_config.preopen_dir("/app/data", "/data")
   ```

2. **샌드박스 디렉토리 사용**: 격리된 디렉토리 생성 후 매핑

   ```python
   import tempfile
   sandbox = tempfile.mkdtemp(prefix="wasi_sandbox_")
   wasi_config.preopen_dir(sandbox, "/")
   ```

3. **읽기 전용 필요시**: 별도의 읽기 전용 마운트 고려

4. **경로 검증**: 사용자 입력 경로를 preopen에 사용할 때는 반드시 검증

   ```python
   import os
   user_path = get_user_input()
   # 경로 정규화 및 검증
   safe_path = os.path.realpath(user_path)
   if not safe_path.startswith("/allowed/base/"):
       raise SecurityError("허용되지 않은 경로")
   ```

---

## Reactor 모드와 Preopen

Reactor 모드 WASM 라이브러리에서 preopen을 사용할 때 주의사항:

### 1. `_initialize` 호출 필수

파일시스템 관련 함수를 호출하기 전에 `_initialize`를 먼저 호출해야 합니다:

```python
instance = linker.instantiate(store, module)

# _initialize 먼저 호출
initialize = instance.exports(store).get("_initialize")
if initialize:
    initialize(store)

# 그 다음 파일시스템 접근 함수 호출
list_root = instance.exports(store).get("list_root_directory")
list_root(store)
```

### 2. Preopen 없이 파일 접근 시 오류

Preopen 설정 없이 파일시스템 접근 시:

```
ENOENT: no such file or directory
```

또는

```
wasm trap: out of bounds memory access
```

---

## 참고 자료

- [WASI 공식 문서](https://wasi.dev/)
- [wasmtime Preopen 문서](https://docs.wasmtime.dev/)
- [Node.js WASI API](https://nodejs.org/api/wasi.html)
- [Capability-based Security](https://en.wikipedia.org/wiki/Capability-based_security)
