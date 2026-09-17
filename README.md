# 🐾 DesktopPet · 桌面宠物

> 一个可爱的桌面小宠物，会在屏幕上走来走去，支持拖拽与点击互动。
> A cute desktop pet that walks around your screen.

<p align="center">
  <img src="https://github.com/YSkali/DesktopPet/blob/main/docs/images/1.png?raw=true" alt="DesktopPet 桌宠形象" width="320">
  <br>
  <em>桌宠形象 · 自动走动 · 拖拽 · 点击互动</em>
</p>

## 📸 截图

<div align="center">

| 🖱️ 右键菜单 | 🧠 系统状态 | ℹ️ 关于桌宠 |
|:---:|:---:|:---|
| ![右键菜单](https://github.com/YSkali/DesktopPet/blob/main/docs/images/2.png?raw=true) | ![系统状态](https://github.com/YSkali/DesktopPet/blob/main/docs/images/3.png?raw=true) | ![关于桌宠](https://github.com/YSkali/DesktopPet/blob/main/docs/images/4.png?raw=true) |
| 呼出操作面板 | CPU / 电池 / 时段感知 | 版本 · 心情 · 亲密度 |

</div>

<div align="center">

| 🎛️ 控制台 |
|:---:|
| ![控制台](https://github.com/YSkali/DesktopPet/blob/main/docs/images/5.png?raw=true) |
| 页面式功能扩展 · 实时生效 |

</div>

<p align="center">
  <img alt="platform" src="https://img.shields.io/badge/platform-Windows-blue">
  <img alt="python" src="https://img.shields.io/badge/python-3.9%2B-brightgreen">
  <img alt="license" src="https://img.shields.io/badge/license-MIT-green">
</p>

---

## ✨ 特性 Features

- 🪟 **透明无边框窗口**：只有角色可见，始终置顶（Windows 色键透明）
- 🚶 **自动走动**：左右移动、随机停下休息
- 🖱️ **拖拽 & 点击**：拖拽移动位置，点击有互动反应
- 🖱️ **右键菜单**：设置面板 / 切换角色 / 打招呼 / 关于 / 退出
- 🎛️ **可视化控制台**：右键「设置面板…」，页面式设置外观/通用/动作/互动/感知/角色包/工具/日志，实时生效
- 🎛️ **可配置**：`config.json` 调整速度、大小、置顶等，无需改代码
- 🖼️ **自定义素材**：放入白底图片，脚本自动去背、统一尺寸
- 📦 **一键打包**：`build.bat` 生成可直接分发的 exe

> ⚠️ **平台说明**：色键透明基于 Windows 的 `-transparentcolor`，**仅 Windows 支持**；其他平台会降级（角色可能带底色矩形）。

---

## 🚀 快速开始 Quick Start

### 方式一：下载可执行文件（推荐普通用户）

前往 [Releases](https://github.com/yourname/desktoppet/releases) 下载 `DesktopPet-win64.zip`，解压后双击 `DesktopPet.exe` 即可。

### 方式二：一键启动（源码，最简单）⭐

克隆后**双击 `start.bat`**（Windows）或运行 `./start.sh`（macOS/Linux）即可。
脚本会自动检查 Python、安装缺失依赖并启动（素材会自动处理，无需手动跑预处理）。

也可以直接：

```bash
git clone https://github.com/yourname/desktoppet.git
cd desktoppet
python run.py        # 会自动处理素材并启动（等价于 python -m desktoppet）
```

### 方式三：手动分步（需要精细控制时）

```bash
pip install -r requirements.txt
python scripts/prepare_assets.py   # 处理素材（生成 assets_processed/）
python run.py                      # 启动
```

### 🔍 一键自检

不确定环境是否正确？运行自检脚本，自动检查 Python 版本、依赖、素材处理、
角色包、配置、版本一致性与打包配置，并运行单元测试：

```bash
python scripts/check.py     # 或双击 check.bat
```

---

## 🎮 操作说明 Controls

| 操作 | 效果 |
|------|------|
| 左键拖拽 | 移动宠物位置 |
| 左键单击 | 随机说句话 + 原地一跳 |
| 左键双击 | 抚摸（专门反应 + 台词） |
| 右键点击 | 打开菜单（设置面板 / 切换角色 / 打招呼 / 关于 / 退出） |

> 待机时宠物还会**偶尔自言自语**；累计互动会提升「亲密度」（在「关于」里查看）。

---

## 🖥️ 桌面控制台 Control Panel

右键桌宠 → **「设置面板…」**，打开可视化控制台（**页面式功能扩展**）：

| 页面 | 内容 |
|------|------|
| 外观 | 宠物大小、不透明度、始终置顶、透明色 |
| 通用 | 自动处理素材、单实例、角色包目录、默认角色包 |
| 动作 | 移动速度、移动/动画间隔、休息概率 |
| 互动 | 点击台词、待机自言自语、反应时长 |
| 感知 | 系统感知开关、启动问候、感知间隔、内存/电池感知 |
| 角色包 | 列出并一键切换 `pets/` 下的角色包 |
| 工具 | 打开配置/目录、导入导出配置 |
| 日志 | 查看运行日志 |
| 关于 | 版本、当前心情、亲密度 |

修改后点「保存并应用」（或按 `Ctrl+S`）→ 立即写入 `config.json` 并生效（透明色需重启）。
窗口支持 <kbd>Esc</kbd> 关闭，底部状态栏显示版本与配置路径。

### ➕ 加功能 = 加页面

框架核心是**页面注册表**：在 `desktoppet/ui/pages/` 新建一个模块，
继承 `ConfigPage`（或用 `Page` 自定义界面）并用 `@register` 注册即可，
控制台会自动发现，无需改动控制台本体。

```python
# desktoppet/ui/pages/myfeature.py
from ..registry import register
from ..widgets import ConfigPage

@register
class MyFeaturePage(ConfigPage):
    id = "myfeature"
    title = "我的功能"
    order = 60
    fields = (
        {"key": "move_speed", "label": "移动速度", "kind": "int", "from": 1, "to": 10},
    )
```

---

## ⚙️ 配置 Configuration

复制 `config.example.json` 为 `config.json`，按需修改（全部可选）：

```json
{
  "pet_size": 128,
  "topmost": true,
  "opacity": 1.0,
  "anim_speed": 400,
  "walk_anim_speed": 300,
  "move_speed": 2,
  "movement_interval": 80,
  "rest_chance": 0.3,
  "edge_bounce": true,
  "edge_pause_ms": 400,
  "click_reaction_ms": 800,
  "auto_prepare_assets": true,
  "single_instance": true
}
```

| 字段 | 说明 |
|------|------|
| `pet_size` | 宠物边长（像素） |
| `topmost` | 是否始终置顶 |
| `opacity` | 窗口不透明度（0.2–1.0） |
| `anim_speed` | 待机动画间隔（毫秒，越大越慢） |
| `walk_anim_speed` | 走路动画间隔（毫秒） |
| `move_speed` | 每次移动像素（越大越快） |
| `rest_chance` | 走动后休息的概率 |
| `edge_bounce` | 走到屏幕边缘时是否弹跳 |
| `edge_pause_ms` | 撞到边缘后停顿的毫秒数 |
| `awareness_memory` | 是否把内存占用纳入心情判断 |
| `awareness_battery` | 是否把电池电量纳入心情判断 |
| `auto_prepare_assets` | 缺少处理后素材时自动生成 |
| `single_instance` | 是否只允许运行一个实例 |

---

## 🎨 自定义宠物外观 Custom Assets

> 推荐用上面的 **上传图片 → 一键生成 Pipeline**，更省事；下面是手动方式。

1. 在 `assets/` 下准备素材（白底、建议 128×128）：

   ```
   assets/
   ├── idle/        待机（2–8 张）
   ├── walk_left/   向左走（4–8 张，向右走会自动镜像）
   ├── click/       点击反应（1 张）
   └── drag/        拖拽状态（1 张）
   ```

2. 运行 `python scripts/prepare_assets.py`，输出到 `assets_processed/`。
3. 重新启动桌宠。

> 帧数无需在代码里写死：程序会自动扫描目录中的所有 PNG。

---

## 🎭 角色包 Character Packs

除了内置素材，你可以把多个角色放进 `pets/` 目录，在**右键菜单 → 切换角色**中随时切换：

> 📦 项目已内置 **7 个 CC0 公共领域**像素动物角色包（小鹿 / 小熊 / 小狼 / 小狐狸 / 小野猪 / 小兔子 / 小马），
> 素材来自 [OpenGameArt](https://opengameart.org) 的 ScratchIO 作品，开箱即用。
> 可用 `python scripts/build_packs_from_oga.py --src <素材目录>` 复现生成。

```
pets/
└── my_pet/
    ├── manifest.json     # {"name": "咪咪", "author": "you"}
    ├── idle/             # 待机帧
    ├── walk_left/        # 向左走帧（向右自动镜像）
    ├── click/            # 点击反应
    └── drag/             # 拖拽状态
```

一键制作（自动去背、统一尺寸、生成 manifest）：

```bash
python scripts/build_pet.py path/to/source --name my_pet --display-name "咪咪"
```

详见 [pets/README.md](pets/README.md)。缺少的状态会自动回退到默认素材。

---

## 📤 上传图片 → 一键生成桌宠 Pipeline

把图片放进 `upload/<角色名>/`，运行流水线即可自动生成一个桌宠角色包：

```bash
python scripts/build_pet.py            # 处理 upload/ 下所有角色目录
python scripts/build_pet.py upload/cat # 只处理某一个
# Windows 也可双击 build_pet.bat
```

流水线会：**自动去白底 → 统一 128×128 → 按动作状态分类 → 生成 `pets/<角色名>/` + `manifest.json`**。
重启桌宠后，右键菜单 → 切换角色 即可看到。

图片按任意方式组织都行，程序会智能识别状态（英文/中文关键字都认）：

```
upload/cat/
├── idle/01.png          # ① 状态子目录
├── walk_left/01.png
├── idle_02.png          # ② 文件名前缀（与 ① 可混用）
└── 01.png               # ③ 无提示 → 归为待机
```

支持状态：待机 `idle`、走路 `walk_left`、点击 `click`、拖拽 `drag`、抚摸 `pet`。
详见 [upload/README.md](upload/README.md)。

---

## 🧠 系统感知 & 对话 System Awareness

桌宠会“感知”你的电脑状态，并按心情调整行为：

- 🌙 **深夜**会打哈欠、动作变慢（想睡觉）
- ☀️ **清晨**精力充沛，走得更勤
- 🔥 **CPU 高负载**时会“累趴”、放慢速度并多休息
- 💬 启动时按**时段问候**，右键「打个招呼」可让它说句话

无需额外配置；可选安装 `psutil` 让 CPU 感知更精确：

```bash
pip install ".[awareness]"     # 或 pip install psutil
```

在 `config.json` 中开关：`"awareness": true`、`"greetings": true`、`"awareness_interval": 15`。

---

## 📦 打包为 exe Packaging

```bash
# Windows：双击 packaging/build.bat，或手动：
python scripts/prepare_assets.py
python packaging/setup_cx.py build
```

产物在 `build/exe.*/` 目录，整个文件夹可拷贝到 U 盘分发。

---

## 🗂️ 项目结构 Structure

```
desktoppet/
├── desktoppet/            # 主程序包（10 个核心模块）
│   ├── pet.py             # 宠物主逻辑（含单实例锁 / 边缘行为 / 窗口设置）
│   ├── animation.py       # 动画加载/切换（自动扫描帧）
│   ├── config.py          # 配置管理
│   ├── awareness.py       # 系统感知 + 人格台词（心情 / CPU / 电池）
│   ├── packs.py           # 角色包发现与切换
│   ├── bubble.py          # 对话气泡
│   ├── prepare.py         # 素材预处理（去白底）
│   ├── pipeline.py        # 图片 → 角色包流水线
│   ├── _paths.py          # 路径工具（兼容打包）+ open_path
│   ├── version.py         # 版本号唯一来源
│   ├── ui/                # 桌面控制台（页面式功能扩展）⭐
│   │   ├── theme.py       # 颜色 / 字体 / 控件工厂
│   │   ├── context.py     # PageContext（页面 ↔ 主程序桥梁）
│   │   ├── registry.py    # 页面注册表（@register）
│   │   ├── widgets/       # fields.py 字段构建器 + form.py 配置页基类
│   │   ├── panel.py       # 控制台窗口（导航 / 状态栏）
│   │   └── pages/         # 内置页面（外观/通用/动作/互动/感知/角色包/工具/日志/关于）
│   └── __main__.py        # python -m desktoppet
├── assets/                # 原始素材
├── assets_processed/      # 处理后的素材（自动生成，已 gitignore）
├── pets/                  # 角色包（7 个内置 + 自定义）
├── upload/                # 上传图片 → 流水线生成角色包
├── scripts/               # 开发工具（check / build_pet / prepare_assets）
├── packaging/             # cx_Freeze 打包配置
├── docs/                  # 详细教程 / 测试指南
├── tests/                 # 单元测试（与模块 1:1 对应）
├── run.py                 # 源码启动入口
├── pyproject.toml
├── CHANGELOG.md
├── CONTRIBUTING.md
└── LICENSE
```

---

## 🧪 开发与测试 Development

```bash
pip install -r requirements.txt -r requirements-dev.txt
pytest -q
```

详见 [CONTRIBUTING.md](CONTRIBUTING.md)。本地验收步骤见 [docs/TESTING.md](docs/TESTING.md)，图文教程见 [docs/TUTORIAL.md](docs/TUTORIAL.md)。

> 🐍 用 **PyCharm** 打开调试？见 [docs/PYCHARM.md](docs/PYCHARM.md)（解释器配置、运行/断点调试 `run.py`、测试与流水线运行配置）。

---

## 🗺️ Roadmap

- [x] v1.0 基础桌宠（透明窗口 / 走动 / 拖拽 / 点击）
- [x] v1.1 工程化（配置文件、单实例、自动扫描帧、日志、CI、打包发布）
- [x] v1.2 角色包体系（`pets/` + `manifest.json` + 右键切换角色）
- [x] v1.3 系统感知（CPU/时间）+ 对话气泡
- [x] v1.4 更丰富的交互（单击/双击/拖拽台词、待机自言自语、弹跳、亲密度）
- [x] v1.5 简化启动（`start.bat` / `start.sh`）+ 一键自检（`scripts/check.py`）
- [x] v1.6 上传图片 → 流水线生成角色包（`upload/` + `build_pet.py`）+ PyCharm 适配
- [x] v1.7 桌面控制台：页面式功能扩展框架（右键「设置面板…」，加功能 = 加页面）
- [x] v1.8 控制台工程化（`ui/` 拆分为 theme/context/registry/widgets/pages）+ 工具/日志页、导入导出配置、不透明度、Ctrl+S
- [ ] v2.0 AI 对话（接入 LLM / 本地 Ollama）

---

## 🙏 致谢 Credits

- 素材：请在替换为自己的图片后，在此注明来源与授权。

---

## 📄 许可 License

本项目基于 [MIT License](LICENSE) 开源。

---

<h3 align="center">English</h3>

<p align="center">
  <b>DesktopPet</b> — a cute desktop pet that walks around your screen.
</p>

## Features

- 🪟 Transparent frameless window, always on top
- 🚶 Walks around automatically, rests randomly
- 🖱️ Drag to move, click to interact
- 🎛️ Configurable via `config.json` (no code editing)
- 🖼️ Custom sprites (auto background removal)
- 📦 One-click packaging into a standalone executable

> ⚠️ **Platform**: color-key transparency is Windows-native (best on Windows). macOS uses system transparency; other platforms fall back gracefully.

## Quick Start

Download `DesktopPet-win64.zip` from [Releases](https://github.com/yourname/desktoppet/releases), or run from source:

```bash
git clone https://github.com/yourname/desktoppet.git
cd desktoppet
pip install -r requirements.txt
python scripts/prepare_assets.py
python run.py
```

## Roadmap

- [x] v1.0 Basic desktop pet
- [x] v1.1 Engineering (config, single instance, auto frame scan, logging, CI, release)
- [x] v1.2 Character packs
- [x] v1.3 System awareness (CPU/time) + speech bubble
- [x] v1.4 Richer interactions (click / double-click / drag lines, idle chatter, bounce)
- [x] v1.5 One-click start (`start.bat` / `start.sh`) + self-test (`scripts/check.py`)
- [x] v1.6 Upload images → pipeline to build pet packs (`upload/` + `build_pet.py`) + PyCharm guide
- [x] v1.7 Control panel: page-based feature extension (right-click「设置面板…」; add feature = add page)
- [x] v1.8 Control panel modularized (`ui/` split into theme/context/registry/widgets/pages) + tools/logs pages, config import/export, opacity, Ctrl+S
- [ ] v2.0 AI chat (LLM / local Ollama)

## License

[MIT](LICENSE)
