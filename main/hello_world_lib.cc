/**
 * WASI Reactor 모드 라이브러리 (C++)
 * 
 * 이 파일은 main() 없이 export 함수만 제공합니다.
 * -mexec-model=reactor 플래그로 빌드하면 _start 대신 _initialize가 생성됩니다.
 * 클라이언트에서 개별 함수를 직접 호출할 수 있습니다.
 */

#include <iostream>
#include <dirent.h>
#include <sys/stat.h>
#include <cstring>
#include <string>

// WASM export 매크로
#ifdef __wasm__
#define WASM_EXPORT_AS(name) __attribute__((export_name(#name)))
#else
#define WASM_EXPORT_AS(name)
#endif

// C 링크 래퍼 함수 선언 (WASM export용)
extern "C" {
    WASM_EXPORT_AS(list_root_directory)
    void wasm_list_root_directory();
    
    WASM_EXPORT_AS(list_directory)
    void wasm_list_directory(const char* path);
    
    WASM_EXPORT_AS(say_hello)
    void wasm_say_hello();
}

// 지정한 경로의 폴더 목록을 출력
void list_directory(const std::string& path) {
    std::cout << "Directory listing of '" << path << "':" << std::endl;
    
    DIR* dir = opendir(path.c_str());
    if (dir == nullptr) {
        std::cout << "Cannot open directory: " << path << std::endl;
        return;
    }
    
    struct dirent* entry;
    while ((entry = readdir(dir)) != nullptr) {
        // . 과 .. 은 제외
        if (std::strcmp(entry->d_name, ".") == 0 || std::strcmp(entry->d_name, "..") == 0) {
            continue;
        }
        
        // 폴더인지 표시
        const char* type = (entry->d_type == DT_DIR) ? "[DIR] " : "      ";
        std::cout << "  " << type << entry->d_name << std::endl;
    }
    
    closedir(dir);
}

// 루트 경로("/")의 폴더 목록을 출력
void list_root_directory() {
    list_directory("/");
}

// C 링크 래퍼 함수 구현 (WASM export용)
void wasm_list_root_directory() {
    list_root_directory();
}

void wasm_list_directory(const char* path) {
    list_directory(std::string(path));
}

void wasm_say_hello() {
    std::cout << "Hello World from WASI!" << std::endl;
}
