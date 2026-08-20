#!/usr/bin/env python3
"""从 buildbot 下载的核心 zip 生成 RetroGame-Cores 仓库结构。

用法：先把 buildbot 下载的 zip 放到本地目录，再运行本脚本。
  py tools/generate_core_manifest.py --cores-dir <zip目录> --repo-root .
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import shutil
import sys
import zipfile
from pathlib import Path
from typing import Any

CORE_META = {
    "fceumm": {
        "displayName": "FCEUmm",
        "platformIds": ["nes"],
        "runtimeFamily": "libretro",
        "license": "GPL-2.0-or-later",
        "licenseFile": "fceumm.txt",
        "sourceUrl": "https://github.com/libretro/libretro-fceumm",
        "defaultForPlatform": True,
    },
    "mesen": {
        "displayName": "Mesen",
        "platformIds": ["nes"],
        "runtimeFamily": "libretro",
        "license": "GPL-3.0-or-later",
        "licenseFile": "mesen.txt",
        "sourceUrl": "https://github.com/SourMesen/Mesen",
        "defaultForPlatform": False,
    },
}

EXPECTED_SO = {
    "fceumm": "fceumm_libretro_android.so",
    "mesen": "mesen_libretro_android.so",
}


def utc_now() -> str:
    return dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_core_zip(zip_path: Path) -> dict[str, bytes]:
    with zipfile.ZipFile(zip_path) as zf:
        names = zf.namelist()
        so_name = next((n for n in names if n.endswith(".so")), names[0])
        return {so_name: zf.read(so_name)}


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate RetroGame-Cores catalog.")
    parser.add_argument("--cores-dir", required=True, help="包含 buildbot 下载 zip 的目录。")
    parser.add_argument("--repo-root", required=True, help="RetroGame-Cores 仓库根路径。")
    parser.add_argument("--version", default="nightly-20260819", help="核心版本标识。")
    args = parser.parse_args()

    cores_dir = Path(args.cores_dir).resolve()
    repo_root = Path(args.repo_root).resolve()
    now = utc_now()

    cores: list[dict[str, Any]] = []
    for core_id, meta in CORE_META.items():
        so_name = EXPECTED_SO[core_id]
        files = []
        for abi in ("arm64-v8a", "armeabi-v7a", "x86", "x86_64"):
            zip_path = cores_dir / f"{abi}-{so_name}.zip"
            if not zip_path.is_file():
                print(f"跳过缺失核心包：{zip_path.name}", file=sys.stderr)
                continue
            contents = load_core_zip(zip_path)
            so_data = contents[so_name]
            dest = repo_root / "cores" / "nes" / core_id / abi / so_name
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(so_data)
            files.append(
                {
                    "abi": abi,
                    "url": f"../cores/nes/{core_id}/{abi}/{so_name}",
                    "fileName": so_name,
                    "size": len(so_data),
                    "sha256": sha256(so_data),
                    "minSdk": 23,
                }
            )
        license_rel = f"licenses/{meta['licenseFile']}"
        cores.append(
            {
                "id": core_id,
                "displayName": meta["displayName"],
                "platformIds": meta["platformIds"],
                "runtimeFamily": meta["runtimeFamily"],
                "version": args.version,
                "license": meta["license"],
                "licenseUrl": f"../{license_rel}",
                "sourceUrl": meta["sourceUrl"],
                "defaultForPlatform": meta["defaultForPlatform"],
                "files": files,
            }
        )

    manifest = {
        "schemaVersion": 1,
        "catalogId": "retrogame-cores",
        "catalogName": "RetroGame 核心仓库",
        "generatedAt": now,
        "cores": cores,
    }
    out = repo_root / "catalog" / "core-manifest.v1.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    total = sum(len(c["files"]) for c in cores)
    print(f"完成：{len(cores)} 个核心，{total} 个文件")
    return 0


if __name__ == "__main__":
    sys.exit(main())
