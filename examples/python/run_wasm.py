#!/usr/bin/env python3
"""
Python에서 WASI WebAssembly 모듈 실행 예제

사용법:
    python run_wasm.py                              # say_hello() 실행
    python run_wasm.py <wasm_file_path>             # 지정 파일로 say_hello() 실행
    python run_wasm.py --list-root                  # list_root_directory() 함수 호출
    python run_wasm.py <wasm_file_path> --list-root # 지정 파일로 list_root_directory() 호출

참고: 이 예제는 reactor 모드로 빌드된 WASM 라이브러리를 사용합니다.
      (hello_world_wasi_lib - main() 없이 함수만 export)

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


def run_wasm(wasm_path: str, call_function: str = None) -> int:
    """WASI WASM 모듈을 실행합니다.
    
    Args:
        wasm_path: WASM 파일 경로
        call_function: 호출할 export 함수 이름 (None이면 _start 실행)
    """
    
    # 엔진 및 스토어 생성
    engine = Engine()
    store = Store(engine)
    
    # WASI 설정
    wasi_config = WasiConfig()
    wasi_config.inherit_stdout()
    wasi_config.inherit_stderr()
    wasi_config.inherit_stdin()
    # 파일시스템 접근 권한 부여 (루트 디렉토리)
    if call_function == "list_root_directory":
        wasi_config.preopen_dir("/", "/")
    store.set_wasi(wasi_config)
    
    # 링커에 WASI 함수들 추가
    linker = Linker(engine)
    linker.define_wasi()
    
    # WASM 모듈 로드
    wasm_bytes = Path(wasm_path).read_bytes()
    module = Module(engine, wasm_bytes)
    
    # 인스턴스 생성 및 실행
    instance = linker.instantiate(store, module)
    
    # reactor 모드: _initialize 함수가 있으면 먼저 호출
    initialize = instance.exports(store).get("_initialize")
    if initialize:
        initialize(store)
    
    if call_function:
        # 특정 함수 직접 호출
        func = instance.exports(store).get(call_function)
        if func is None:
            print(f"오류: {call_function} 함수를 찾을 수 없습니다.")
            return 1
        try:
            print(f"=== {call_function}() 호출 ===")
            func(store)
            return 0
        except Exception as e:
            if "exit" in str(e).lower():
                return 0
            raise
    
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
    # 커맨드 라인 인자 파싱
    args = sys.argv[1:]
    list_root_flag = "--list-root" in args
    args = [a for a in args if not a.startswith("--")]
    
    # WASM 파일 경로 결정
    if args:
        wasm_path = args[0]
    else:
        # 기본 경로 (reactor 모드 라이브러리)
        script_dir = Path(__file__).parent
        wasm_path = script_dir / "../../bazel-bin/main/hello_world_wasi_lib"
    
    wasm_path = Path(wasm_path).resolve()
    
    if not wasm_path.exists():
        print(f"오류: WASM 파일을 찾을 수 없습니다: {wasm_path}")
        print("\n먼저 빌드하세요:")
        print("  ./bazel build //main:hello_world_wasi_lib --config=wasi")
        sys.exit(1)
    
    print(f"WASM 파일 로드: {wasm_path}")
    print("-" * 40)
    
    # list_root_directory 또는 say_hello 호출
    call_function = "list_root_directory" if list_root_flag else "say_hello"
    exit_code = run_wasm(str(wasm_path), call_function)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
