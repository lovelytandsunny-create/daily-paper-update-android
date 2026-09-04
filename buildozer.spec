[app]

# 应用名称（显示在手机桌面）
title = 每日论文更新

# 包名（必须全 ASCII，全局唯一）
package.name = dailypaperupdate
package.domain = org.dailypaperupdate

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,otf

version = 1.1.0

# 依赖：Python 3.12 + Kivy（锁定 Python 3.12，因 Kivy 2.3.1 不兼容 Python 3.13+）
# hostpython3 必须与 python3 版本一致
requirements = python3==3.12.10,hostpython3==3.12.10,kivy==2.3.1

orientation = portrait
fullscreen = 0

# 应用图标
icon.filename = %(source.dir)s/icon.png
presplash.filename = %(source.dir)s/icon.png

# 网络权限（PubMed 检索必需）
android.permissions = INTERNET

# Android 目标版本（API 35 = Android 15，支持 16KB page size 的新机型）
android.api = 35
android.minapi = 21
android.ndk_api = 21

# NDK 版本（r28c 支持 Android 15+ 的 16KB 内存页对齐）
android.ndk = 28c

# 支持架构（现代手机均为 64 位 arm64，armeabi-v7a 32位已淘汰且与 NDK r28c 编译不兼容）
android.archs = arm64-v8a

# 允许打包时自动接受 SDK 许可（CI 必需）
android.accept_sdk_license = True

# python-for-android v2026.05.09（支持新 Android/NDK r28c）
p4a.branch = v2026.05.09

# 本地 recipe（修复 Python 3.12 在 NDK r28c 上 grpmodule 编译失败）
p4a.local_recipes = local_recipes

[buildozer]

log_level = 2
warn_on_root = 1
