#include <iostream>
#include <dirent.h>
#include <sys/stat.h>
#include <cstring>
#include <string>

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

int main(int argc, char* argv[]) {
    if (argc > 1) {
        // 인자가 있으면 해당 경로의 디렉토리 목록 출력
        list_directory(argv[1]);
    } else {
        // 인자가 없으면 기본 메시지 출력
        std::cout << "Hello World" << std::endl;
    }
    return 0;
}
