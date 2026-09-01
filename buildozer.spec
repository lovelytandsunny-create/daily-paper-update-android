[app]

# 应用名称（显示在手机桌面）
title = 每日论文更新

# 包名（必须全 ASCII，全局唯一）
package.name = dailypaperupdate
package.domain = org.dailypaperupdate

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 1.0.0

# 依赖：Python3 + Kivy（锁定 Python 3.11，Kivy 2.3.1 尚不兼容 3.14）
requirements = python3==3.11.9,kivy==2.3.1

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

# 支持架构（主流手机均为 arm64）
android.archs = arm64-v8a,armeabi-v7a

# 允许打包时自动接受 SDK 许可（CI 必需）
android.accept_sdk_license = True

[buildozer]

log_level = 2
warn_on_root = 1
