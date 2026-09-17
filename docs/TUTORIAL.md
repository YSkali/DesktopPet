> **说明**：本文是项目的「0 基础开发教程」，侧重原理与逐行讲解。
> 项目**当前最新的目录结构与启动方式**请以根目录 [README](../README.md) 为准。
> 快速验收步骤见 [TESTING.md](TESTING.md)，日常使用见 [使用手册.txt](使用手册.txt)。

# 🐾 桌面宠物 - 0基础完整开发教程

> 本教程将带你从零开始，一步步完成一个桌面宠物程序的开发和打包。
> 即使你没有任何编程经验，也能跟着完成！

---

## 📋 目录

1. [项目简介](#1-项目简介)
2. [环境搭建](#2-环境搭建)
3. [项目结构](#3-项目结构)
4. [第一步：准备素材](#4-第一步准备素材)
5. [第二步：图片预处理](#5-第二步图片预处理)
6. [第三步：创建透明窗口](#6-第三步创建透明窗口)
7. [第四步：加载并显示图片](#7-第四步加载并显示图片)
8. [第五步：实现动画系统](#8-第五步实现动画系统)
9. [第六步：实现移动逻辑](#9-第六步实现移动逻辑)
10. [第七步：添加互动功能](#10-第七步添加互动功能)
11. [第八步：打包发布](#11-第八步打包发布)
12. [常见问题](#12-常见问题)

---

## 1. 项目简介

### 我们要做的是什么？

一个能在桌面上走来走去的小宠物：
- ✅ 透明背景，只有角色可见
- ✅ 会自己左右走动
- ✅ 支持拖拽移动
- ✅ 点击有互动反应
- ✅ 右键菜单
- ✅ 打包成 exe，可以放在 U 盘分享

### 技术栈

| 技术 | 作用 | 为什么选它 |
|------|------|------------|
| Python | 编程语言 | 简单易学，适合新手 |
| Tkinter | 界面框架 | Python 自带，无需额外安装 |
| Pillow | 图像处理 | 处理图片透明度 |
| cx_Freeze | 打包工具 | 把程序打包成 exe |

---

## 2. 环境搭建

### 2.1 安装 Python

1. **下载 Python**
   - 访问：https://www.python.org/downloads/
   - 点击下载最新版本（建议 3.10 或更高）

2. **安装 Python**
   - 运行下载的安装程序
   - ⚠️ **重要**：勾选 "Add Python to PATH"
   - 点击 "Install Now"

3. **验证安装**
   - 打开命令提示符（Win+R，输入 cmd）
   - 输入以下命令：
   ```bash
   python --version
   ```
   - 如果显示 Python 版本号，说明安装成功

### 2.2 安装依赖库

打开命令提示符，输入：

```bash
pip install Pillow cx_Freeze
```

等待安装完成即可。

### 2.3 安装代码编辑器（可选）

推荐使用以下任一编辑器：
- **VS Code**：https://code.visualstudio.com/
- **PyCharm**：https://www.jetbrains.com/pycharm/
- **记事本**：最简单，系统自带

---

## 3. 项目结构

创建一个新文件夹，命名为 `桌宠开发`，在里面创建以下结构：

```
桌宠开发/
├── pet.py              ← 主程序（宠物核心逻辑）
├── prepare_assets.py   ← 素材处理脚本
├── setup_cx.py         ← 打包配置文件
├── build.bat           ← 一键打包脚本
│
├── assets/             ← 原始素材文件夹
│   ├── idle/           ← 待机动画图片
│   ├── walk_left/      ← 走路动画图片
│   ├── click/          ← 点击反应图片
│   └── drag/           ← 拖拽状态图片
│
└── assets_processed/   ← 处理后的素材（自动生成）
```

---

## 4. 第一步：准备素材

### 4.1 素材要求

| 项目 | 要求 |
|------|------|
| 格式 | PNG、JPG 均可 |
| 尺寸 | 建议 128×128 或 256×256 像素 |
| 背景 | 白色背景（程序会自动去除） |

### 4.2 需要准备的素材

| 文件夹 | 说明 | 数量 | 命名 |
|--------|------|------|------|
| `assets/idle/` | 待机动画 | 2-8张 | 任意名称 |
| `assets/walk_left/` | 向左走路动画 | 4-8张 | 任意名称 |
| `assets/click/` | 点击反应 | 1-2张 | 任意名称 |
| `assets/drag/` | 拖拽状态 | 1张 | 任意名称 |

### 4.3 素材来源

- **自己画**：用画图工具、Photoshop、Aseprite 等
- **网上下载**：搜索 "pixel pet sprite" 或 "桌宠素材"
- **AI 生成**：用 AI 工具生成角色图片

---

## 5. 第二步：图片预处理

### 5.1 创建 `prepare_assets.py`

这个脚本会：
1. 统一所有图片尺寸为 128×128
2. 去除白色背景
3. 转换为透明 PNG

**完整代码：**

```python
# -*- coding: utf-8 -*-
"""
图片预处理脚本
将素材统一处理为 128x128 的透明 PNG
"""

import os
from PIL import Image

# 目标尺寸
TARGET_SIZE = (128, 128)

# 源目录 → 目标目录映射
ASSET_MAP = {
    "assets/idle": "assets_processed/idle",
    "assets/walk_left": "assets_processed/walk_left",
    "assets/drag": "assets_processed/drag",
    "assets/click": "assets_processed/click",
}


def is_white_pixel(pixel, threshold=240):
    """判断像素是否接近白色"""
    r, g, b = pixel[0], pixel[1], pixel[2]
    return r >= threshold and g >= threshold and b >= threshold


def remove_background_floodfill(img, threshold=240):
    """
    使用边缘填充算法去除背景
    只去除与图片边缘相连的白色区域，保留人物内部的白色
    """
    pixels = img.load()
    width, height = img.size
    visited = set()

    # 从四个边缘开始 flood fill
    edges = []
    for x in range(width):
        edges.append((x, 0))
        edges.append((x, height - 1))
    for y in range(height):
        edges.append((0, y))
        edges.append((width - 1, y))

    # BFS flood fill
    queue = []
    for pos in edges:
        if pos not in visited:
            x, y = pos
            if is_white_pixel(pixels[x, y], threshold):
                queue.append(pos)
                visited.add(pos)

    while queue:
        x, y = queue.pop(0)
        pixels[x, y] = (pixels[x, y][0], pixels[x, y][1], pixels[x, y][2], 0)

        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height:
                if (nx, ny) not in visited:
                    if is_white_pixel(pixels[nx, ny], threshold):
                        queue.append((nx, ny))
                        visited.add((nx, ny))

    return img


def process_image(input_path, output_path, remove_bg=True, bg_threshold=240):
    """处理单张图片：调整大小、转为 RGBA、去除白色背景"""
    try:
        img = Image.open(input_path)

        # 转为 RGBA（添加透明通道）
        if img.mode != "RGBA":
            img = img.convert("RGBA")

        # 调整大小
        img = img.resize(TARGET_SIZE, Image.Resampling.LANCZOS)

        # 去除白色背景
        if remove_bg:
            img = remove_background_floodfill(img, bg_threshold)

        # 保存
        img.save(output_path, "PNG")
        print(f"  OK: {os.path.basename(output_path)}")
        return True
    except Exception as e:
        print(f"  FAIL: {os.path.basename(input_path)} - {e}")
        return False


def process_folder(src_dir, dst_dir):
    """处理整个文件夹"""
    os.makedirs(dst_dir, exist_ok=True)

    files = sorted([
        f for f in os.listdir(src_dir)
        if f.lower().endswith((".png", ".jpg", ".jpeg", ".bmp"))
    ])

    print(f"\n[{os.path.basename(dst_dir)}] 共 {len(files)} 张")

    for i, filename in enumerate(files, 1):
        input_path = os.path.join(src_dir, filename)
        output_name = f"{i:02d}.png"
        output_path = os.path.join(dst_dir, output_name)
        process_image(input_path, output_path)


def main():
    print("=" * 50)
    print("桌宠素材预处理工具")
    print("=" * 50)

    total = 0
    for src, dst in ASSET_MAP.items():
        if os.path.exists(src):
            process_folder(src, dst)
            total += len(os.listdir(dst))
        else:
            print(f"\n[SKIP] 目录不存在: {src}")

    print("\n" + "=" * 50)
    print(f"处理完成！共 {total} 张图片")
    print("输出目录: assets_processed/")
    print("=" * 50)


if __name__ == "__main__":
    main()
```

### 5.2 运行素材处理

```bash
python prepare_assets.py
```

成功后会看到：
```
==================================================
桌宠素材预处理工具
==================================================

[idle] 共 4 张
  OK: 01.png
  OK: 02.png
  OK: 03.png
  OK: 04.png

[walk_left] 共 4 张
  OK: 01.png
  ...

处理完成！共 10 张图片
输出目录: assets_processed/
==================================================
```

---

## 6. 第三步：创建透明窗口

### 6.1 创建 `pet.py`

先创建一个最基础的透明窗口：

```python
# -*- coding: utf-8 -*-
"""
桌面宠物 - 主程序
"""

import tkinter as tk


class DesktopPet:
    """桌面宠物主类"""

    # 透明颜色键（用于背景透明）
    TRANSPARENT_COLOR = '#abcdef'

    def __init__(self):
        # 创建主窗口
        self.root = tk.Tk()

        # 窗口设置：无边框、透明、置顶
        self.root.overrideredirect(True)  # 无边框
        self.root.attributes('-topmost', True)  # 置顶

        # 透明设置
        self.root.configure(bg=self.TRANSPARENT_COLOR)
        self.root.attributes('-transparentcolor', self.TRANSPARENT_COLOR)

        # 窗口大小和位置
        self.pet_size = 128
        self.root.geometry(f'{self.pet_size}x{self.pet_size}+500+500')

    def run(self):
        """运行程序"""
        print("桌宠已启动！")
        self.root.mainloop()


if __name__ == "__main__":
    pet = DesktopPet()
    pet.run()
```

### 6.2 测试运行

```bash
python pet.py
```

如果看到一个透明的小窗口出现在屏幕上，说明成功！

---

## 7. 第四步：加载并显示图片

### 7.1 添加图片加载功能

在 `pet.py` 中添加以下代码：

```python
import sys
import os
import tkinter as tk
from PIL import Image, ImageTk


def resource_path(relative_path):
    """获取资源文件路径，支持打包后的路径"""
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


class DesktopPet:
    TRANSPARENT_COLOR = '#abcdef'

    def __init__(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        self.root.configure(bg=self.TRANSPARENT_COLOR)
        self.root.attributes('-transparentcolor', self.TRANSPARENT_COLOR)

        self.pet_size = 128
        self.root.geometry(f'{self.pet_size}x{self.pet_size}+500+500')

        # 创建画布
        self.canvas = tk.Canvas(
            self.root,
            width=self.pet_size,
            height=self.pet_size,
            bg=self.TRANSPARENT_COLOR,
            highlightthickness=0
        )
        self.canvas.pack()

        # 加载并显示图片
        self.show_image('assets_processed/idle/01.png')

    def show_image(self, path):
        """显示图片"""
        full_path = resource_path(path)
        if os.path.exists(full_path):
            img = Image.open(full_path)
            self.current_photo = ImageTk.PhotoImage(img)
            self.canvas.delete('all')
            self.canvas.create_image(
                self.pet_size // 2,
                self.pet_size // 2,
                image=self.current_photo,
                anchor=tk.CENTER
            )
            print(f"显示图片: {path}")
        else:
            print(f"图片不存在: {full_path}")

    def run(self):
        print("桌宠已启动！")
        self.root.mainloop()


if __name__ == "__main__":
    pet = DesktopPet()
    pet.run()
```

### 7.2 测试运行

```bash
python pet.py
```

应该能看到宠物图片显示在桌面上！

---

## 8. 第五步：实现动画系统

### 8.1 添加动画管理器

在 `pet.py` 开头添加动画管理类：

```python
class AnimationManager:
    """动画管理器：负责加载和切换动画帧"""

    def __init__(self):
        self.animations = {}  # 动画名称 -> [帧列表]
        self.current_anim = None
        self.current_frame = 0

    def load_animation(self, name, folder, count):
        """加载一组动画帧"""
        frames = []
        for i in range(1, count + 1):
            path = resource_path(os.path.join(folder, f"{i:02d}.png"))
            if os.path.exists(path):
                try:
                    img = Image.open(path)
                    if img.mode != 'RGBA':
                        img = img.convert('RGBA')
                    frames.append(img)
                except Exception as e:
                    print(f"Failed to load {path}: {e}")

        if frames:
            self.animations[name] = frames
            print(f"Loaded {name}: {len(frames)} frames")

    def set_animation(self, name):
        """切换动画"""
        if name != self.current_anim and name in self.animations:
            self.current_anim = name
            self.current_frame = 0

    def get_current_frame(self):
        """获取当前帧"""
        if self.current_anim and self.current_anim in self.animations:
            frames = self.animations[self.current_anim]
            return frames[self.current_frame % len(frames)]
        return None

    def next_frame(self):
        """前进到下一帧"""
        if self.current_anim and self.current_anim in self.animations:
            frames = self.animations[self.current_anim]
            self.current_frame = (self.current_frame + 1) % len(frames)
```

### 8.2 在 DesktopPet 中使用动画

```python
class DesktopPet:
    TRANSPARENT_COLOR = '#abcdef'

    # 动画状态常量
    STATE_IDLE = "idle"
    STATE_WALK_LEFT = "walk_left"
    STATE_WALK_RIGHT = "walk_right"
    STATE_DRAG = "drag"
    STATE_CLICK = "click"

    def __init__(self):
        # ... 窗口设置代码 ...

        # 动画管理器
        self.anim = AnimationManager()
        self.load_all_animations()

        # 动画速度（毫秒）
        self.anim_speed = 400  # 待机动画
        self.walk_anim_speed = 300  # 走路动画

        # 当前状态
        self.state = self.STATE_IDLE

        # 设置初始动画
        self.anim.set_animation(self.STATE_IDLE)

        # 启动动画更新
        self.update_animation()

    def load_all_animations(self):
        """加载所有动画资源"""
        self.anim.load_animation(self.STATE_IDLE, "assets_processed/idle", 4)
        self.anim.load_animation(self.STATE_WALK_LEFT, "assets_processed/walk_left", 4)
        self.anim.load_animation(self.STATE_DRAG, "assets_processed/drag", 1)
        self.anim.load_animation(self.STATE_CLICK, "assets_processed/click", 1)

    def update_display(self):
        """更新显示的图片"""
        frame = self.anim.get_current_frame()
        if frame:
            # 如果是向右走，水平翻转图片
            if self.state == self.STATE_WALK_RIGHT:
                frame = frame.transpose(Image.FLIP_LEFT_RIGHT)

            self.current_photo = ImageTk.PhotoImage(frame)
            self.canvas.delete('all')
            self.canvas.create_image(
                self.pet_size // 2,
                self.pet_size // 2,
                image=self.current_photo,
                anchor=tk.CENTER
            )

    def update_animation(self):
        """动画帧更新"""
        self.anim.next_frame()
        self.update_display()

        # 根据状态选择动画速度
        if self.state in (self.STATE_WALK_LEFT, self.STATE_WALK_RIGHT):
            speed = self.walk_anim_speed
        else:
            speed = self.anim_speed

        self.root.after(speed, self.update_animation)
```

### 8.3 测试运行

```bash
python pet.py
```

宠物应该会播放待机动画了！

---

## 9. 第六步：实现移动逻辑

### 9.1 添加移动功能

在 `__init__` 中添加：

```python
        # 移动相关
        self.move_speed = 2  # 移动速度（像素/帧）
        self.direction = 1  # 1=右, -1=左
        self.screen_width = self.root.winfo_screenwidth()

        # 行为计时
        self.walk_counter = 0
        self.idle_counter = 0
        self.is_resting = False
        self.is_dragging = False

        # 启动移动更新
        self.update_movement()
```

### 9.2 添加移动更新函数

```python
    def update_movement(self):
        """移动逻辑更新"""
        if self.is_dragging or self.state == self.STATE_CLICK:
            self.root.after(80, self.update_movement)
            return

        if self.is_resting:
            # 休息中
            self.idle_counter += 1
            if self.idle_counter > random.randint(40, 100):  # 休息 2-5 秒
                self.is_resting = False
                self.idle_counter = 0
                self.direction = random.choice([-1, 1])
                self.set_state(self.STATE_WALK_RIGHT if self.direction == 1 else self.STATE_WALK_LEFT)
        else:
            # 走动中
            self.walk_counter += 1
            x = self.root.winfo_x()
            y = self.root.winfo_y()
            new_x = x + self.direction * self.move_speed

            # 边界检测
            if new_x <= 0:
                new_x = 0
                self.direction = 1
                self.set_state(self.STATE_WALK_RIGHT)
            elif new_x >= self.screen_width - self.pet_size:
                new_x = self.screen_width - self.pet_size
                self.direction = -1
                self.set_state(self.STATE_WALK_LEFT)

            self.root.geometry(f'+{new_x}+{y}')

            # 随机决定是否休息
            if self.walk_counter > random.randint(80, 200):
                if random.random() < 0.3:  # 30% 概率休息
                    self.is_resting = True
                    self.walk_counter = 0
                    self.set_state(self.STATE_IDLE)

        self.root.after(80, self.update_movement)

    def set_state(self, new_state):
        """切换状态"""
        if new_state != self.state:
            self.state = new_state
            if new_state == self.STATE_WALK_RIGHT:
                self.anim.set_animation(self.STATE_WALK_LEFT)
            else:
                self.anim.set_animation(new_state)
```

记得在开头添加 `import random`。

### 9.3 测试运行

```bash
python pet.py
```

宠物应该会在屏幕上左右走动了！

---

## 10. 第七步：添加互动功能

### 10.1 添加事件绑定

在 `__init__` 中添加：

```python
        # 绑定事件
        self.bind_events()
```

### 10.2 添加事件处理函数

```python
    def bind_events(self):
        """绑定鼠标事件"""
        self.root.bind('<ButtonPress-1>', self.on_mouse_press)
        self.root.bind('<B1-Motion>', self.on_mouse_drag)
        self.root.bind('<ButtonRelease-1>', self.on_mouse_release)
        self.root.bind('<Button-3>', self.on_right_click)

        self.canvas.bind('<ButtonPress-1>', self.on_mouse_press)
        self.canvas.bind('<B1-Motion>', self.on_mouse_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_mouse_release)
        self.canvas.bind('<Button-3>', self.on_right_click)

    def on_mouse_press(self, event):
        """鼠标按下"""
        self.is_dragging = True
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        self.set_state(self.STATE_DRAG)

    def on_mouse_drag(self, event):
        """鼠标拖拽"""
        if self.is_dragging:
            x = self.root.winfo_x() + (event.x - self.drag_start_x)
            y = self.root.winfo_y() + (event.y - self.drag_start_y)
            self.root.geometry(f'+{x}+{y}')

    def on_mouse_release(self, event):
        """鼠标释放"""
        if self.is_dragging:
            self.is_dragging = False
            self.set_state(self.STATE_CLICK)
            self.root.after(800, self.on_click_end)

    def on_click_end(self):
        """点击反应结束"""
        self.is_resting = True
        self.idle_counter = 0
        self.set_state(self.STATE_IDLE)

    def on_right_click(self, event):
        """右键菜单"""
        menu = tk.Menu(self.root, tearoff=0)
        menu.configure(bg='#2d2d2d', fg='white', activebackground='#4a9eff')

        menu.add_command(label="关于桌宠", command=self.show_about)
        menu.add_separator()
        menu.add_command(label="退出", command=self.quit_app)

        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def show_about(self):
        """显示关于信息"""
        print("桌宠 v1.0 - 一个可爱的桌面小伙伴")

    def quit_app(self):
        """退出程序"""
        self.root.destroy()
```

### 10.3 测试运行

```bash
python pet.py
```

现在可以：
- 左键拖拽移动宠物
- 左键点击让宠物做出反应
- 右键打开菜单

---

## 11. 第八步：打包发布

### 11.1 创建 `setup_cx.py`

```python
# -*- coding: utf-8 -*-
"""
cx_Freeze 打包配置
"""

import sys
from cx_Freeze import setup, Executable

# 依赖项
build_exe_options = {
    "packages": ["tkinter", "PIL"],
    "include_files": [("assets_processed", "assets_processed")],
    "excludes": ["unittest", "email", "html", "http", "xml", "pydoc"],
}

# 基础配置
base = "gui" if sys.platform == "win32" else None

setup(
    name="DesktopPet",
    version="1.0",
    description="桌面宠物",
    options={"build_exe": build_exe_options},
    executables=[
        Executable(
            "pet.py",
            base=base,
            target_name="DesktopPet.exe",
        )
    ],
)
```

### 11.2 创建 `build.bat`（一键打包脚本）

```bat
@echo off
chcp 65001 >nul
echo ========================================
echo 桌宠打包工具
echo ========================================
echo.

echo [1/2] 正在处理素材...
python prepare_assets.py
echo.

echo [2/2] 正在打包...
python setup_cx.py build
echo.

echo ========================================
if exist "build\exe.win-amd64-3.14\DesktopPet.exe" (
    echo [完成] 打包成功！
    echo 文件位置: build\exe.win-amd64-3.14\DesktopPet.exe
) else (
    echo [错误] 打包失败
)
echo ========================================
pause
```

### 11.3 打包

**方式一：双击 `build.bat`**

**方式二：命令行**
```bash
python setup_cx.py build
```

### 11.4 打包完成

文件位置：
```
桌宠开发\build\exe.win-amd64-3.14\
├── DesktopPet.exe      ← 主程序
├── assets_processed/   ← 素材
├── lib/                ← 运行库
└── python314.dll       ← Python 运行时
```

### 11.5 分享给别人

将整个 `build\exe.win-amd64-3.14\` 文件夹压缩成 zip 发送。

对方收到后：
1. 解压文件夹
2. 双击 `DesktopPet.exe`
3. 桌宠就出现了！

---

## 12. 常见问题

### Q: 运行后没有显示？

**A:** 检查以下几点：
1. 素材是否已处理（运行 `prepare_assets.py`）
2. `assets_processed` 文件夹是否存在
3. 文件夹中是否有图片

### Q: 背景有白色？

**A:** 重新处理素材：
```bash
python prepare_assets.py
```

### Q: 动画太快/太慢？

**A:** 修改 `pet.py` 中的数值：
```python
self.anim_speed = 400        # 待机动画（越大越慢）
self.walk_anim_speed = 300   # 走路动画（越大越慢）
```

### Q: 移动太快/太慢？

**A:** 修改 `pet.py` 中的数值：
```python
self.move_speed = 2  # 移动速度（越大越快）
```

### Q: 打包后用的是旧素材？

**A:** 先删除 `build` 文件夹再打包：
```bash
rm -rf build
python setup_cx.py build
```

### Q: 如何更换宠物外观？

**A:** 
1. 将新图片放入 `assets/` 对应文件夹
2. 运行 `python prepare_assets.py`
3. 运行 `python pet.py` 测试

---

## 🎉 完成！

恭喜你完成了桌面宠物的开发！

你现在拥有了：
- ✅ 一个能在桌面走动的宠物
- ✅ 支持拖拽和点击互动
- ✅ 可以打包成 exe 分享给别人

如果想添加更多功能，可以尝试：
- 添加音效
- 添加对话气泡
- 添加更多动画状态
- 添加宠物属性（饥饿度、心情等）

祝你玩得开心！🐾
