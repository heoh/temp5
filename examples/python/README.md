# Python WASI 실행 예제

## 요구사항

```bash
pip install wasmtime
```

## 실행 방법

```bash
# 프로젝트 루트에서 WASM 빌드
./bazel build //main:hello_world_wasi_c --config=wasi

# 예제 디렉토리로 이동
cd examples/python

# 실행 (기본 경로 사용)
python run_wasm.py

# 또는 WASM 파일 경로 직접 지정
python run_wasm.py ../../bazel-bin/main/hello_world_wasi

# C++ 버전 실행
python run_wasm.py ../../bazel-bin/main/hello_world_wasi
```

## 출력 예시

```
WASM 파일 로드: /path/to/bazel-bin/main/hello_world_wasi_c
----------------------------------------
Hello World from WASI!
```

## wasmtime-py 주요 API

```python
from wasmtime import Engine, Store, Module, Linker, WasiConfig

# 기본 설정
engine = Engine()
store = Store(engine)

# WASI 설정
wasi_config = WasiConfig()
wasi_config.inherit_stdout()  # stdout 상속
wasi_config.inherit_env()     # 환경변수 상속
wasi_config.argv = ["prog", "arg1"]  # 명령줄 인자
store.set_wasi(wasi_config)

# 모듈 로드 및 실행
linker = Linker(engine)
linker.define_wasi()
module = Module.from_file(engine, "file.wasm")
instance = linker.instantiate(store, module)
instance.exports(store)["_start"](store)
```

## 참고

- [wasmtime-py GitHub](https://github.com/bytecodealliance/wasmtime-py)
- [wasmtime-py 문서](https://bytecodealliance.github.io/wasmtime-py/)
