/**
 * Node.js에서 WASI WebAssembly 모듈 실행 예제
 * 
 * 사용법:
 *   node run_wasm.mjs
 * 
 * 요구사항:
 *   Node.js 20+ (WASI 지원)
 */

import { readFile } from 'node:fs/promises';
import { WASI } from 'node:wasi';
import { argv, env } from 'node:process';

// WASI 인스턴스 생성
const wasi = new WASI({
  version: 'preview1',
  args: ['wasm'],  // 기본 인자 (프로그램 이름만)
  env: env,
});

// WASM 파일 경로 (빌드 후 생성되는 경로)
const wasmPath = process.argv[2] || './bazel-bin/main/hello_world_wasi_c';

try {
  // WASM 바이너리 로드
  const wasmBuffer = await readFile(wasmPath);
  
  // WebAssembly 모듈 컴파일 및 인스턴스화
  const wasmModule = await WebAssembly.compile(wasmBuffer);
  const instance = await WebAssembly.instantiate(wasmModule, wasi.getImportObject());
  
  // WASI 시작 (main 함수 실행)
  wasi.start(instance);
  
} catch (error) {
  console.error('WASM 실행 오류:', error.message);
  process.exit(1);
}
