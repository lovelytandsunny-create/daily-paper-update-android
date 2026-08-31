# 📱 每日论文更新 — Android 版（APK）

这是桌面版「每日论文更新」的安卓移植版，功能一致：勾选研究方向 → 检索 PubMed 最新论文 → 分类浏览 → 点击 DOI 跳转原文。

## 目录结构

```
android-app/
├── main.py                 # Kivy 应用（纯标准库 + Kivy）
├── buildozer.spec          # APK 构建配置
├── icon.png                # 应用图标
├── .github/workflows/
│   └── build-apk.yml       # GitHub Actions 自动编译工作流
└── README.md
```

---

## 如何生成 APK 并得到下载地址

**本机无法直接编译 APK**（Windows 缺少 Linux/Android SDK 环境），因此采用 **GitHub Actions 云编译**：把代码推到 GitHub，云端自动编译出 `.apk`，下载地址就是 GitHub Releases 链接。

### 第 1 步：安装 GitHub CLI（可选但推荐）

> 已安装 Git。若没有 `gh`，可去 https://github.com 网页手动建仓库。

### 第 2 步：创建仓库并推送

在 PowerShell 中执行（把 `你的用户名` 换成你的 GitHub 用户名）：

```powershell
cd "c:\Users\admin\.vscode\DB\ZZH\每日更新\android-app"

git init
git add .
git commit -m "Daily Paper Update Android app v1.0"

# 方式 A：用 gh 命令行（已登录 GitHub）
gh repo create daily-paper-update-android --public --source=. --push

# 方式 B：手动在网页建好空仓库后
git remote add origin https://github.com/你的用户名/daily-paper-update-android.git
git branch -M main
git push -u origin main
```

### 第 3 步：触发编译

推送后，进入仓库 **Actions** 页面：
1. 左侧选 **Build Android APK**
2. 点 **Run workflow** → **Run workflow**（手动触发）

首次编译约 **15~30 分钟**（自动下载 Android SDK/NDK，后续因缓存会快很多）。

### 第 4 步：下载 APK（两种方式）

| 方式 | 操作 | 下载地址 |
|------|------|---------|
| **临时下载** | Actions 页面 → 本次运行 → **Artifacts** 下载 `dailypaperupdate-debug-apk` | 仅构建产物页 |
| **永久下载链接** | 打一个版本标签，自动发布到 Releases | `https://github.com/你的用户名/daily-paper-update-android/releases` |

**打标签发布（得到永久下载地址）：**

```powershell
git tag v1.0.0
git push origin v1.0.0
```

推送标签后工作流会自动编译并把 APK 发布到 **Releases** 页面，那个链接就是可分享、可长期访问的下载地址。

---

## 安装到手机

1. 下载 `*.apk` 文件传到手机
2. 点击安装（需允许「安装未知来源应用」）
3. 打开「每日论文更新」，勾选方向 → 点「开始更新」

> 因为是 debug 签名构建，部分手机首次安装会提示风险，选「仍然安装」即可。若要正式上架/去掉警告，需配置签名密钥（另见下方「正式签名」）。

---

## 本地开发调试（可选）

在电脑上无需打包也能运行 UI（需安装 Kivy）：

```powershell
pip install kivy
python main.py
```

## 正式签名（去警告 / 上架）

如需正式签名的 release APK，在 buildozer.spec 的 `[app]` 段增加签名配置，并用 `buildozer android release` 编译。

---

## 常见问题

- **编译失败**：多数是网络问题导致 SDK 下载超时，重跑一次 Actions 即可（缓存会续传）。
- **手机提示无法联网**：已配置 `INTERNET` 权限，无需额外操作。
- **想改研究方向**：编辑 `main.py` 顶部的 `TOPICS` 列表即可。
