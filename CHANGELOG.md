# Changelog

本项目的所有重要变更都会记录在此文件。
格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，
版本号遵循 [语义化版本 SemVer](https://semver.org/lang/zh-CN/)。

## [Unreleased]

## [1.10.0] - 2026-09-17

### Added
- **内置角色包**：新增 7 个开箱即用的 CC0 像素动物角色包（小鹿 / 小熊 / 小狼 / 小狐狸 / 小野猪 / 小兔子 / 小马）
  - 素材来源：[OpenGameArt](https://opengameart.org) 的 ScratchIO “Animated Wild Animals” 与 “Animated Horse”，均为 **CC0 公共领域**授权
  - 每个角色包含 `idle`(6) / `walk_left`(8) / `click`(1) / `drag`(1) 四态，统一 128×128 透明画布
  - 附带 `manifest.json`（名称 / 作者 / 许可 / 来源），右键菜单「切换角色」即可选用
- 新增脚本 `scripts/build_packs_from_oga.py`：从素材帧条切帧 → 缩放居中 → 生成角色包（可复现）
- `pets/README.md` 增加「内置角色包」清单与出处说明

### Changed
- 版本号提升至 1.10.0

## [1.9.0] - 2026-09-17

### Added
- **屏幕边缘行为**：桌宠走到屏幕左右边缘时会自动折返，并可选「弹跳 + 短暂停顿」，动作更自然
  - 新增模块 `desktoppet/edge.py`（纯函数 `clamp_x` / `direction_after`，便于测试）
  - 新配置项 `edge_bounce`（边缘弹跳，默认开）、`edge_pause_ms`（撞边停顿毫秒，默认 400）
- **更多感知源**：系统感知在 CPU/时间之外，新增**内存占用**与**电池电量**
  - `awareness.read_memory_percent()` / `read_battery()`（对 psutil 缺失优雅降级）
  - `compute_mood()` 支持内存/电池参数，新增 `LOW_BATTERY` 低电量心情（未充电且 ≤20% 时提醒充电）
  - 新配置项 `awareness_memory`、`awareness_battery`（默认开）
- 右键菜单新增「**系统状态**」：弹窗显示时段 / CPU / 内存 / 电池 / 当前心情
- 控制台「动作」页新增边缘弹跳、边缘停顿；「感知」页新增内存感知、电池感知
- 新增单元测试 `tests/test_edge.py`，并扩充 `tests/test_awareness.py`（内存/电池/低电量优先级）

### Changed
- 版本号提升至 1.9.0

## [1.8.0] - 2026-09-16

### Changed
- **控制台结构项目化**：把单文件 `ui/widgets.py` 拆分为工程化包
  - `ui/theme.py`：颜色 / 字体 / 控件工厂（统一外观，工厂支持调用方覆盖样式）
  - `ui/context.py`：`PageContext`（页面与主程序之间的桥梁）
  - `ui/registry.py`：页面注册表（`Page` / `register` / `load_pages`）
  - `ui/widgets/`：`fields.py`（类型化字段构建器）+ `form.py`（`ConfigPage` 基类）
  - `ui/panel.py`：控制台窗口（导航 + 页面宿主 + 标题栏/底部状态栏）
- 版本号提升至 1.8.0

### Added
- 控制台新增页面：**通用**（素材/单实例/角色包目录/默认角色包）、**工具**（打开配置与目录、导入导出配置）、**日志**（查看运行日志）
- 新增字段类型：`choice`（下拉菜单）、`path`（目录选择）、`color`（取色板）
- 面板增强：底部状态栏（版本 + 配置路径 + 快捷键）、标题栏「保存 (Ctrl+S)」，`Ctrl+S` 保存当前页
- 新配置项 `opacity`（窗口不透明度，即时生效）；`Config.load_from()` 支持导入配置
- `platform_compat.open_path()`：跨平台用系统程序打开文件/目录
- 文件日志：日志同时写入 `logs/desktoppet.log`（供「日志」页查看）

### Fixed
- 修复控制台部分字段（颜色/文本/路径）渲染时报错导致页面空白的问题（`tk.Entry` 误用 `-ipady` 参数、控件工厂关键字冲突）

## [1.7.1] - 2026-09-16

### Fixed
- **控制台「能打开但用不了」的体验问题**：窗口现在打开即居中、短暂置顶（1.5 秒后释放），避免被置顶桌宠遮挡；新增标题栏「关闭」按钮并支持 <Esc> 关闭
- 控制台保存/切换后会在标题栏与页面内显示明确反馈（✓ 已保存并应用 / ⚠ 写入失败），不再「点了没反应」
- 页面构建或保存出错时不再静默吞掉，改为在面板内显示错误信息
- 感知/自言自语定时器改为常驻循环，使得在控制台**开关这些选项能即时生效**（此前只在启动时决定，改开关无效）
- `Config.save()` 健壮化：自动创建目录，写入失败只记日志并返回 `False`（不再抛异常）
- 复选框与滑块改用原生 `tk` 控件并显式着色，规避 Windows 主题下的对比度问题

### Added
- 控制台页面新增「↺ 恢复默认」按钮
- 角色包页面高亮当前项并显示「（当前）」
- `tests/gui_smoke.py`：真机控制台全链路冒烟测试（需图形界面）
- 单元测试补充 `notify` 回调、`Config.save` 容错、`_coerce` 类型转换等用例

## [1.7.0] - 2026-09-16

### Added
- **桌面控制台（页面式功能扩展框架）**：新增 `desktoppet/ui/`，右键菜单新增「设置面板…」，把桌宠升级为可视化配置中心
  - `ui/registry.py`：页面注册表（`Page` / `PageContext` / `@register`），**加功能 = 加一个页面模块**
  - `ui/panel.py`：控制台窗口（左侧导航由注册表动态生成）
  - `ui/widgets.py`：`ConfigPage` 基类，声明 `fields` 即自动生成控件并写回 `config.json`
  - 内置页面：外观 / 动作 / 互动 / 感知 / 角色包 / 关于
- `Config.set()` 方法与 `DesktopPet.apply_config()`：设置保存后即时生效（尺寸、速度、感知、置顶等）
- 控制台单元测试 `tests/test_ui.py`；一键自检新增「桌面控制台」检查项

### Changed
- 包结构新增 `desktoppet.ui`、`desktoppet.ui.pages`；`pyproject.toml` 改用 `packages.find`
- 版本号提升至 1.7.0

## [1.6.0] - 2026-09-16

### Added
- **图片 → 桌宠 流水线**：`desktoppet/pipeline.py` + `scripts/build_pet.py`（含 `build_pet.bat`），把 `upload/` 里的图片一键处理成角色包：自动去背、统一尺寸、按动作状态（idle/walk_left/click/drag/pet）分类并生成 `manifest.json`
- 状态智能识别，支持「状态子目录 / 文件名前缀 / 无提示默认 idle」三种组织方式，关键字中英文均可
- `upload/` 上传目录及说明 `upload/README.md`
- **PyCharm 适配**：`[tool.pytest.ini_options]`、`.editorconfig`、`docs/PYCHARM.md`（解释器/运行/断点调试/测试/流水线运行配置）
- 流水线单元测试 `tests/test_pipeline.py`；自检脚本新增流水线功能检查
- `prepare.process_image` 支持自定义输出尺寸

### Changed
- 以 `scripts/build_pet.py` 统一取代 `scripts/make_pack.py`
- 版本号提升至 1.6.0

## [1.5.0] - 2026-09-16

### Added
- **一键启动脚本**：`start.bat`（Windows）/ `start.sh`（macOS/Linux），自动检查 Python、安装缺失依赖并启动（素材自动处理，无需手动分步）
- **一键自检脚本**：`scripts/check.py`（含 `check.bat` 包装），自动检查 Python 版本、依赖、模块导入、语法编译、素材处理管线、角色包发现、配置读写、版本一致性、打包配置语法，并运行单元测试；输出清晰报告与退出码（0/1），可用于本地验收与 CI 前置检查
- 自检支持 `--skip-tests` 与 `CHECK_DEBUG` 调试开关

### Changed
- 简化启动流程：`python run.py` 即可（缺素材时自动生成），不需再手动先跑预处理
- 版本号提升至 1.5.0

## [1.4.0] - 2026-09-15

### Added
- **更丰富的交互**：
  - **单击**随机说一句台词 + 原地上下一跳
  - **双击**触发「抚摸」反应（专用动画 + 台词）
  - **拖拽结束**说一句拖拽台词
  - **待机时偶尔自言自语**（可开关）
  - **亲密度**累计互动次数，「关于」弹窗展示
- `reactions.py`：分类台词库（click / drag / pet / chatter），随机取词
- 支持 `pet` 状态动画（放入 `assets/pet/` 或角色包 `pet/` 即可启用，缺失则回退 click）
- 配置项 `talk_on_click` / `idle_chatter` / `chatter_interval`
- 台词库单元测试 `tests/test_reactions.py`

### Changed
- 交互反应统一走 `_do_click_reaction`（动画 + 台词 + 弹跳），并加防抖
- 版本号提升至 1.4.0

## [1.3.0] - 2026-09-15

### Added
- **系统感知（System Awareness）**：根据 CPU 负载与时段（早/日/晚/夜）自动调整心情与行为（移动/动画速度、休息频率），高负载时会“累趴/喘气”
- **对话气泡（Speech Bubble）**：桌宠头顶弹出文字，启动时按时段问候
- 右键菜单新增「打个招呼」
- `awareness.py`（心情计算、CPU 读取，psutil 可选降级）、`bubble.py`（气泡窗口）
- 配置项 `awareness` / `greetings` / `awareness_interval`
- `awareness` 可选依赖组（psutil，更精确的 CPU 感知）
- 系统感知单元测试 `tests/test_awareness.py`
- 「关于桌宠」弹窗显示当前心情

### Changed
- 版本号提升至 1.3.0

## [1.2.0] - 2026-09-15

### Added
- **角色包（Character Pack）系统**：`pets/` 下每个子目录即一个角色，右键菜单“切换角色”即时切换（缺失状态自动回退默认素材）
- `scripts/make_pack.py`：一键把一组图片制作成角色包（自动去背、统一尺寸、生成 `manifest.json`）
- `pets/` 目录、`_template` 模板与 `pets/README.md` 制作说明
- 角色包单元测试 `tests/test_packs.py`
- GitHub Issue / PR 模板
- 配置项 `pack`（默认角色包）与 `pets_dir`

### Changed
- `AnimationManager` 新增 `clear()`，支持切换角色包时重载动画
- 打包配置将 `pets/` 一并打入发行包

## [1.1.0] - 2026-09-15

### Added
- 全新的 `desktoppet` Python 包结构，支持 `pip install .` 与 `python -m desktoppet`
- 外部配置文件 `config.json`（速度、大小、置顶、单实例等，无需改源码）
- 单实例锁：避免重复启动多个桌宠
- 跨平台透明窗口适配（Windows / macOS，其他平台降级并提示）
- 完善 `logging` 日志，替换原先的 `print`
- GitHub Actions：CI 检查 + 打 tag 自动打包发布
- 单元测试与 `CHANGELOG`、`CONTRIBUTING` 等工程化文件

### Changed
- 动画帧数**自动扫描**素材目录，不再硬编码 4/4/1/1
- “点击”与“拖拽”通过位移阈值区分，交互更自然
- 素材目录由中文括号命名改为 ASCII：`assets/idle`、`assets/walk_left`、`assets/drag`、`assets/click`
- 预处理脚本迁移到 `scripts/prepare_assets.py`，打包配置迁移到 `packaging/`
- 去背景 flood fill 由 `list.pop(0)` 改为 `collections.deque`，大图处理更快
- 目录结构规范化（`desktoppet/`、`assets/`、`scripts/`、`packaging/`、`docs/`）

### Fixed
- 打包为 GUI 后右键“关于桌宠”无反应的问题（改用弹窗）
- clone 后缺少 `assets_processed/` 导致动画加载失败的问题（支持自动生成）

## [1.0.0] - 2026-06-05

### Added
- 初始版本：透明无边框窗口、待机/走路/拖拽/点击动画、右键菜单
- 素材预处理脚本与 cx_Freeze 打包脚本

[Unreleased]: https://github.com/yourname/desktoppet/compare/v1.6.0...HEAD
[1.6.0]: https://github.com/yourname/desktoppet/compare/v1.5.0...v1.6.0
[1.5.0]: https://github.com/yourname/desktoppet/compare/v1.4.0...v1.5.0
[1.4.0]: https://github.com/yourname/desktoppet/compare/v1.3.0...v1.4.0
[1.3.0]: https://github.com/yourname/desktoppet/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/yourname/desktoppet/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/yourname/desktoppet/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/yourname/desktoppet/releases/tag/v1.0.0
