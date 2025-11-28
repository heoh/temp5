/**
 * Node.js에서 WASI WebAssembly 모듈 실행 예제
 * 
 * 사용법:
 *   node run_wasm.mjs                              # say_hello() 실행
 *   node run_wasm.mjs <wasm_path>                  # 지정 파일로 say_hello() 실행
 *   node run_wasm.mjs <wasm_path> --list-root     # list_root_directory() 호출
 * 
 * 요구사항:
 *   Node.js 20+ (WASI 지원)
 * 
 * 참고: 이 예제는 reactor 모드로 빌드된 WASM 라이브러리를 사용합니다.
 *       (hello_world_wasi_lib - main() 없이 함수만 export)
 */

import { readFile } from 'node:fs/promises';
import { WASI } from 'node:wasi';
import { argv, env } from 'node:process';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';

// 스크립트 디렉토리 기준 경로 계산
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const dummyRootPath = resolve(__dirname, '../dummy_root');

// 커맨드 라인 인자 파싱
const args = process.argv.slice(2);
const listRootFlag = args.includes('--list-root');
const wasmPath = args.find(a => !a.startsWith('--')) || './bazel-bin/main/hello_world_wasi_lib';

// WASI 인스턴스 생성 (더미 루트 디렉토리를 "/"로 매핑)
const wasi = new WASI({
  version: 'preview1',
  args: ['wasm'],
  env: env,
  preopens: listRootFlag ? { '/': dummyRootPath } : {},
});

try {
  // WASM 바이너리 로드
  const wasmBuffer = await readFile(wasmPath);
  
  // WebAssembly 모듈 컴파일 및 인스턴스화
  const wasmModule = await WebAssembly.compile(wasmBuffer);
  const instance = await WebAssembly.instantiate(wasmModule, wasi.getImportObject());
  
  // WASI 초기화 (reactor 모드 - _start 없음)
  wasi.initialize(instance);
  
  if (listRootFlag) {
    // list_root_directory 함수 직접 호출
    console.log('=== list_root_directory() 호출 ===');
    const listRootDir = instance.exports.list_root_directory;
    if (listRootDir) {
      listRootDir();
    } else {
      console.error('오류: list_root_directory 함수가 export되지 않았습니다.');
      process.exit(1);
    }
  } else {
    // say_hello 함수 호출
    const sayHello = instance.exports.say_hello;
    if (sayHello) {
      sayHello();
    } else {
      console.error('오류: say_hello 함수가 export되지 않았습니다.');
      process.exit(1);
    }
  }
  
} catch (error) {
  console.error('WASM 실행 오류:', error.message);
  process.exit(1);
}
