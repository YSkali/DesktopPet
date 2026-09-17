# 在 PyCharm 中打开与调试 / PyCharm Guide

本文件说明如何在 PyCharm 中打开、运行和调试本项目。

## 1. 打开项目

`File → Open`，选择项目根目录（包含 `pyproject.toml` 的那一层），
PyCharm 会自动识别为 Python 项目。

## 2. 配置解释器

`File → Settings → Project → Python Interpreter → Add Interpreter`
→ 选择已有的 Python 3.9+，或新建一个 venv（推荐）。

然后安装依赖（可在 PyCharm 的 Terminal 中执行）：

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt   # 开发/测试/打包
```

> 建议把项目解释器设为 venv，隔离依赖。

## 3. 运行桌宠

项目根目录的 **`run.py`** 是启动入口。

- 直接右键 `run.py` → **Run 'run'**；
- 或点击工具栏绿色 ▶（首次会自动生成一个运行配置）。

也可以运行 `desktoppet/__main__.py`（等价于 `python -m desktoppet`）。

## 4. 调试（断点）

1. 在 `desktoppet/pet.py` 的关键方法（如 `on_mouse_press`、
   `_do_click_reaction`、`refresh_awareness`）左侧点一下设置**断点**；
2. 右键 `run.py` → **Debug 'run'**；
3. 桌宠窗口出现后，在界面上点击/拖拽宠物即可命中断点，
   用 **Debug 面板** 查看变量、调用栈、单步执行。

> 提示：Tkinter 事件在 `mainloop` 中触发，断点会在界面操作时命中。

## 5. 运行测试

- 右键 `tests/` 目录 → **Run 'pytest in tests'**；
- 或使用内置终端：`pytest -q`。

`pyproject.toml` 已配置 `[tool.pytest.ini_options]`，PyCharm 会自动识别测试。

## 6. 使用流水线（上传图片 → 生成桌宠）

1. 把图片放进 `upload/<角色名>/`；
2. 右键 `scripts/build_pet.py` → **Run**；
3. 生成的角色包出现在 `pets/<角色名>/`；
4. 重新运行 `run.py`，右键菜单 → 切换角色。

## 7. 常用运行配置一览（可手动新建）

| 名称 | 类型 | 脚本 / 模块 | 参数 |
|------|------|------------|------|
| Run Pet | Python | `run.py` | — |
| Self-Test | Python | `scripts/check.py` | — |
| Build Pet | Python | `scripts/build_pet.py` | — |
| Prepare Assets | Python | `scripts/prepare_assets.py` | — |
| Tests | pytest | `tests/` | — |

## 8. 项目结构速览

```
desktoppet/     主程序包（pet / animation / pipeline / config ...）
scripts/        命令行脚本（prepare_assets / build_pet / check）
packaging/      打包配置（cx_Freeze）
upload/         上传图片放这里
pets/           生成/自定义的角色包
tests/          单元测试
assets/         内置默认素材
run.py          启动入口（PyCharm 运行这个）
```

## 9. 小贴士

- **中文乱码**：`File → Settings → Editor → File Encodings` 全部设为 UTF-8；本项目源码均为 UTF-8。
- **换行符**：项目含 `.editorconfig`，PyCharm 会自动统一（`.bat` 用 CRLF）。
- **不要提交** `__pycache__/`、`assets_processed/`、`.idea/`（已在 `.gitignore`）。
