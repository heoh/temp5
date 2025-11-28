#include <stdio.h>
#include <dirent.h>
#include <string.h>

// 지정한 경로의 폴더 목록을 출력
void list_directory(const char* path) {
    DIR* dir = opendir(path);
    if (dir == NULL) {
        printf("Cannot open directory: %s\n", path);
        return;
    }
    
    printf("Directory listing of '%s':\n", path);
    
    struct dirent* entry;
    while ((entry = readdir(dir)) != NULL) {
        // . 과 .. 은 제외
        if (strcmp(entry->d_name, ".") == 0 || strcmp(entry->d_name, "..") == 0) {
            continue;
        }
        
        // 폴더인지 표시 (d_type이 지원되는 경우)
        const char* type = (entry->d_type == DT_DIR) ? "[DIR] " : "      ";
        printf("  %s%s\n", type, entry->d_name);
    }
    
    closedir(dir);
}

// 루트 경로("/")의 폴더 목록을 출력
void list_root_directory(void) {
    list_directory("/");
}

int main(int argc, char* argv[]) {
    if (argc > 1) {
        // 인자가 있으면 해당 경로의 디렉토리 목록 출력
        list_directory(argv[1]);
    } else {
        printf("Hello World from WASI!\n");
    }
    return 0;
}
