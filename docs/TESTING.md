# 本地测试步骤指导 · Local Testing Guide

本文档指导你在本地（Windows）验收桌面宠物项目。
按顺序执行，任何一步失败都可对照「常见问题」排查。

---

> **⚡ 最快方式（推荐）**：直接双击 `check.bat`（或运行 `python scripts/check.py`），
> 它会**自动完成**环境检查、依赖、模块导入、语法编译、素材管线、角色包、配置、
> 版本一致性和单元测试，并打印通过/失败报告。若显示「✅ 自检通过」，
> 再双击 `start.bat` 即可启动。下面 0–9 节是逐项手动指导，供深入排查时使用。

---

## 0. 前置检查（一次性）

打开 **CMD 或 PowerShell**，进入项目根目录：

```bat
cd /d Y:\个人项目集\桌宠开发
```

确认 Python 版本（建议 3.9+，你机器上实测 3.12）：

```bat
python --version
```

确认 tkinter 可用（Python 自带，一般无需安装）：

```bat
python -c "import tkinter; print('tkinter OK', tkinter.TkVersion)"
```

> 如果提示 tkinter 找不到，说明你的 Python 是不带 Tk 的精简版，
> 重新安装官方 python.org 版本并勾选 "tcl/tk" 即可。

---

## 1. 安装依赖

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

（开发/测试/打包额外依赖）

```bat
pip install -r requirements-dev.txt
```

**预期**：Pillow 安装成功，无报错。

---

## 2. 素材预处理

```bat
python scripts\prepare_assets.py
```

**预期输出**（你当前素材为 10 张）：

```
处理 idle       -> idle (4 张)
处理 walk_left  -> walk_left (4 张)
处理 drag       -> drag (1 张)
处理 click      -> click (1 张)
处理完成！共 10 张图片
```

**检查**：`assets_processed\` 下应生成 `idle\01..04.png`、`walk_left\01..04.png`、
`drag\01.png`、`click\01.png`。
用图片查看器打开，确认**白底已去、角色完整、内部白色（眼睛等）保留**。

---

## 3. 运行单元测试（不需要图形界面）

```bat
pytest -q
```

**预期**：全部通过（约 50+ 项）。

若未安装 pytest：`pip install pytest`。

---

## 4. 启动桌宠（核心验收）

```bat
python run.py
```

**预期**：
- 桌面上出现一个**透明背景**的小宠物，无标题栏、始终置顶；
- 它会自己**左右走动**，偶尔停下；
- 控制台打印启动日志（版本、窗口位置、已加载动画）。

**逐项手动验收（对照操作表）：**

| 步骤 | 操作 | 预期结果 |
|---|---|---|
| 4.1 | 左键**点击**宠物 | 播放点击反应动画，约 0.8 秒后恢复待机 |
| 4.2 | 左键**按住拖动** | 宠物跟随鼠标移动，松手后回到待机 |
| 4.3 | 走到屏幕左右边缘 | 自动掉头，不会跑出屏幕 |
| 4.4 | **右键**点击宠物 | 弹出菜单（关于桌宠 / 退出） |
| 4.5 | 菜单点「关于桌宠」 | 弹出信息框（版本号 + 操作说明） |
| 4.6 | 菜单点「退出」 | 程序正常退出 |

**关键修复验证**：
- 4.2 中**轻轻点一下不应触发拖拽**（位移阈值），4.1 才应触发点击反应；
- 右键「关于」**必须有弹窗**（旧版打包后无反应的问题已修复）。

---

## 5. 配置文件验证（可选）

```bat
copy config.example.json config.json
```

编辑 `config.json`，例如把 `"move_speed": 2` 改成 `"move_speed": 8`，重启宠物。
**预期**：移动明显变快。

> `config.json` 已被 `.gitignore` 忽略，不会污染仓库。

---

## 6. 单实例验证（可选）

先启动一个桌宠，保持运行；再开一个终端执行 `python run.py`。

**预期**：第二个进程打印「检测到桌宠已在运行，本次启动退出」，不出现第二只宠物。

---

## 7. 打包验证（生成 exe）

方式一（推荐）：

```bat
packaging\build.bat
```

方式二（手动）：

```bat
python scripts\prepare_assets.py
python packaging\setup_cx.py build
```

**预期**：生成 `build\exe.win-amd64-3.12\DesktopPet.exe`（目录名以实际 Python 版本为准）。

**打包后验收**：
1. 进入 `build\exe.*\`，双击 `DesktopPet.exe`；
2. 宠物正常显示、走动（无控制台窗口是正确的）；
3. **右键 → 关于桌宠**，确认**弹窗正常**（这是最关键的打包修复点）；
4. 把整个 `build\exe.*\` 文件夹拷到别的目录/U 盘再运行，确认素材随包携带、能独立运行。

---

## 8. 跨平台透明自检（如果你也测 macOS/Linux）

- Windows：色键透明，背景应完全透明；
- macOS：系统透明，正常；
- Linux：会**降级**（角色可能带底色矩形），控制台会打印警告——属预期行为。

---

## 9. 交互功能验证（v1.4.0 新增）⭐

启动 `python run.py` 后，按顺序验证以下新交互（这些是本次重点验收项）：

| 编号 | 操作 | 预期结果 |
|---|---|---|
| 9.1 | **左键单击**宠物 | 头顶气泡随机弹出**一句台词**（如“呀！”“别戳我啦～”），并**原地上下一跳** |
| 9.2 | **左键双击**宠物 | 触发**抚摸反应**（台词如“好舒服～”）。若 `assets/pet/` 或角色包内有 `pet/` 帧则播放该动画，否则回退点击动画 |
| 9.3 | **按住拖动**后松手 | 松手时气泡弹出**拖拽台词**（如“要带我去哪呀？”），随后回到待机 |
| 9.4 | 让宠物**待机约 25 秒** | 宠物**自发说一句话**（无需任何操作）——验证“自言自语” |
| 9.5 | **连续多次**单击/双击 | 每次台词不同（随机），反复点击不会卡住或叠加异常 |
| 9.6 | 右键 → **关于桌宠** | 弹窗显示版本、当前心情，以及**亲密度：N 次互动**（N = 之前的累计点击数+双击数） |

**一键关闭这些交互（可选）**：在 `config.json` 中设置

```json
{ "talk_on_click": false, "idle_chatter": false }
```

**验证台词的随机与多样性（命令行即可，无需图形界面）：**

```bat
python -c "from desktoppet.awareness import random_line, LINES; print([random_line('click') for _ in range(5)])"
```

预期：输出 5 句不同的点击台词，均在 `LINES['click']` 中。

---

## 常见问题 Troubleshooting

| 现象 | 原因 / 解决 |
|---|---|
| `ModuleNotFoundError: No module named 'desktoppet'` | 不在项目根目录运行；或未 `pip install -e .`。请在根目录用 `python run.py` |
| 宠物是纯色方块、无角色 | `assets_processed\` 为空或素材未处理，重跑 `python scripts\prepare_assets.py` |
| 报 `OSError: [Errno 5] Input/output error` | 若是网络盘/同步盘（如某些云盘挂载）写入 `.pyc` 失败所致；把项目放到本地磁盘（如 `D:\`）再试 |
| 点击没反应 | 点在**透明区域**不算；请点在角色图像上；或确认 4.2/4.1 的位移阈值行为 |
| 打包后右键「关于」没反应 | 确认用的是新版 `desktoppet/pet.py`（已改用弹窗） |
| `build` 目录没生成 exe | 看 `packaging\build.bat` 输出，通常是缺 `cx_Freeze`：`pip install cx_Freeze` |
| 无法激活 venv（PowerShell 报执行策略） | 运行 `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`，或改用 CMD |

---

## 验收清单（逐项打勾）

- [ ] `python --version` 正常，tkinter 可用
- [ ] `pip install -r requirements.txt` 成功
- [ ] `python scripts\prepare_assets.py` 输出「共 10 张」，图片去背正确
- [ ] `pytest -q` 显示 6 passed
- [ ] `python run.py` 宠物透明显示并能走动
- [ ] 点击 / 拖拽 / 右键菜单 / 关于弹窗 / 退出 全部正常
- [ ] 单击有台词+弹跳；双击抚摸；拖拽有台词；待机会自言自语（见第 9 节）
- [ ] 「关于」弹窗显示亲密度计数
- [ ] `config.json` 改速度生效
- [ ] 二次启动被单实例拦截
- [ ] `packaging\build.bat` 生成 exe，且 exe 右键「关于」有弹窗
- [ ] exe 目录拷走后可独立运行

全部通过后，即可在项目根目录 `git init` 并推送到 GitHub 新仓库。
