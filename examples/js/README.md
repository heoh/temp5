# JavaScript/Node.js WASI 실행 예제

## 요구사항

- Node.js 20 이상 (WASI 네이티브 지원)

## 실행 방법

```bash
# 프로젝트 루트에서 WASM 빌드
./bazel build //main:hello_world_wasi_c --config=wasi

# 예제 디렉토리로 이동
cd examples/js

# 실행 (기본 경로 사용)
node run_wasm.mjs

# 또는 WASM 파일 경로 직접 지정
node run_wasm.mjs ../../bazel-bin/main/hello_world_wasi
```

## 출력 예시

```
Hello World from WASI!
```

## 참고

- Node.js의 WASI 모듈은 `--experimental-wasi-unstable-preview1` 플래그 없이도 Node.js 20+에서 사용 가능
- 브라우저에서는 WASI를 직접 지원하지 않으므로 [wasmer-js](https://github.com/aspect-build/aspect-wasmtime-js) 같은 폴리필 필요
