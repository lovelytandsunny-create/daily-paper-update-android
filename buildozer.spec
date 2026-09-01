[app]

# 应用名称（显示在手机桌面）
title = 每日论文更新

# 包名（必须全 ASCII，全局唯一）
package.name = dailypaperupdate
package.domain = org.dailypaperupdate

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 1.0.0

# 依赖：Python3 + Kivy
requirements = python3,kivy==2.3.1

orientation = portrait
fullscreen = 0

# 应用图标
icon.filename = %(source.dir)s/icon.png
presplash.filename = %(source.dir)s/icon.png

# 网络权限（PubMed 检索必需）
android.permissions = INTERNET

# Android 目标版本
android.api = 34
android.minapi = 21
android.ndk_api = 21

# NDK 版本（p4a v2024.01.21 配套 r25c）
android.ndk = 25c

# 支持架构（主流手机均为 arm64）
android.archs = arm64-v8a,armeabi-v7a

# 允许打包时自动接受 SDK 许可（CI 必需）
android.accept_sdk_license = True

# 锁定 python-for-android 到 v2024.01.21（用 Python 3.11.5，兼容 Kivy 2.3.1）
p4a.branch = v2024.01.21

[buildozer]

log_level = 2
warn_on_root = 1
