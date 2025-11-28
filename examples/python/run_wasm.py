#!/usr/bin/env python3
"""
Python에서 WASI WebAssembly 모듈 실행 예제

사용법:
    python run_wasm.py
    python run_wasm.py <wasm_file_path>

요구사항:
    pip install wasmtime
"""

import sys
from pathlib import Path

try:
    from wasmtime import Engine, Store, Module, Linker, WasiConfig
except ImportError:
    print("wasmtime 패키지가 필요합니다.")
    print("설치: pip install wasmtime")
    sys.exit(1)


def run_wasm(wasm_path: str) -> int:
    """WASI WASM 모듈을 실행합니다."""
    
    # 엔진 및 스토어 생성
    engine = Engine()
    store = Store(engine)
    
    # WASI 설정
    wasi_config = WasiConfig()
    wasi_config.inherit_stdout()
    wasi_config.inherit_stderr()
    wasi_config.inherit_stdin()
    store.set_wasi(wasi_config)
    
    # 링커에 WASI 함수들 추가
    linker = Linker(engine)
    linker.define_wasi()
    
    # WASM 모듈 로드
    wasm_bytes = Path(wasm_path).read_bytes()
    module = Module(engine, wasm_bytes)
    
    # 인스턴스 생성 및 실행
    instance = linker.instantiate(store, module)
    
    # _start 함수 실행 (WASI 진입점)
    start = instance.exports(store).get("_start")
    if start is None:
        print("오류: _start 함수를 찾을 수 없습니다.")
        return 1
    
    try:
        start(store)
        return 0
    except Exception as e:
        # WASI exit(0)은 예외로 처리됨
        if "exit" in str(e).lower():
            return 0
        raise


def main():
    # WASM 파일 경로 결정
    if len(sys.argv) > 1:
        wasm_path = sys.argv[1]
    else:
        # 기본 경로
        script_dir = Path(__file__).parent
        wasm_path = script_dir / "../../bazel-bin/main/hello_world_wasi_c"
    
    wasm_path = Path(wasm_path).resolve()
    
    if not wasm_path.exists():
        print(f"오류: WASM 파일을 찾을 수 없습니다: {wasm_path}")
        print("\n먼저 빌드하세요:")
        print("  ./bazel build //main:hello_world_wasi_c --config=wasi")
        sys.exit(1)
    
    print(f"WASM 파일 로드: {wasm_path}")
    print("-" * 40)
    
    exit_code = run_wasm(str(wasm_path))
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
