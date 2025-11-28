# temp5

## 빌드 방법

1. Bazelisk 다운로드 및 설치:
```bash
wget -O bazel https://github.com/bazelbuild/bazelisk/releases/latest/download/bazelisk-linux-amd64
chmod +x bazel
```

2. 프로젝트 빌드:
```bash
./bazel build //main:hello_world
```

## 실행 방법

빌드 후 다음 명령어로 실행:
```bash
./bazel-bin/main/hello_world
```
