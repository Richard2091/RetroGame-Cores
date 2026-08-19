# RetroGame-Cores

Retro Hall 模拟器项目的核心资源仓库，按《资源仓库规范》组织，通过 GitHub Pages 发布，供客户端按平台下载模拟器核心。

## 结构

```text
catalog/
  core-manifest.v1.json    # 核心清单（版本、许可证、来源、ABI、sha256）
cores/
  nes/
    fceumm/                # FCEUmm 核心（默认）
      arm64-v8a/           # fceumm_libretro_android.so
      armeabi-v7a/
    mesen/                 # Mesen 核心
      arm64-v8a/
      armeabi-v7a/
licenses/                  # 核心许可证说明
tools/
  generate_core_manifest.py
```

## 核心来源

- 构建产物：libretro buildbot nightly（https://buildbot.libretro.com/nightly/android/latest/）
- 每个核心的 `sha256` 为实际文件 SHA-256，`size` 为实际字节数。
- 核心 `version` 为 nightly 快照日期，随 buildbot 更新维护。

## 维护

```bash
py tools/generate_core_manifest.py --cores-dir <buildbot-zip目录> --repo-root .
```
