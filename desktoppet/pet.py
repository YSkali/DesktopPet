# -*- coding: utf-8 -*-
"""桌面宠物主逻辑。"""

import logging
import os
import random
import socket
import tkinter as tk
from tkinter import messagebox

from PIL import Image, ImageTk

from ._paths import resource_path
from .animation import AnimationManager
from .config import Config
from .awareness import (
    LINES,
    compute_mood,
    greeting_for,
    read_battery,
    read_cpu_percent,
    read_memory_percent,
    random_line,
    time_period,
)
from .bubble import Bubble
from .packs import Pack, discover_packs
from .version import __version__

logger = logging.getLogger(__name__)

# 单实例锁端口（与旧 single_instance.py 保持一致）
_LOCK_PORT = 47653


def _acquire_lock(port=_LOCK_PORT):
    """占用本地回环端口实现单实例；成功返回 socket，失败返回 None。"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("127.0.0.1", port))
        sock.listen(1)
        return sock
    except OSError:
        sock.close()
        return None


def _clamp_x(x, screen_width, pet_size):
    """把横坐标限制在 [0, screen_width - pet_size]，返回 (x, side)。

    side 为 "left" / "right" / None（在范围内或屏幕过窄）。
    """
    max_x = screen_width - pet_size
    if max_x <= 0:
        return 0, None
    if x <= 0:
        return 0, "left"
    if x >= max_x:
        return max_x, "right"
    return x, None


def _direction_after(side):
    """撞到边缘后应前进的方向：左边缘向右(1)，右边缘向左(-1)。"""
    return 1 if side == "left" else -1


def _setup_window(root, color, topmost=True):
    """配置无边框 + 透明窗口（仅 Windows 色键透明，非 Windows 降级）。

    返回 True 表示透明已生效；False 表示已降级。
    """
    try:
        root.overrideredirect(True)  # 去掉标题栏和边框
    except tk.TclError:
        pass

    import sys
    if sys.platform.startswith("win"):
        root.configure(bg=color)
        try:
            root.attributes("-transparentcolor", color)
            return True
        except tk.TclError as e:
            logger.warning("透明色键设置失败: %s", e)
            return False

    logger.warning("当前平台暂不支持色键透明，角色可能带有底色矩形。")
    root.configure(bg=color)
    try:
        root.attributes("-alpha", 1.0)
    except tk.TclError:
        pass
    return False


class DesktopPet:
    """桌面宠物主类。"""

    # 动画状态
    STATE_IDLE = "idle"
    STATE_WALK_LEFT = "walk_left"
    STATE_WALK_RIGHT = "walk_right"
    STATE_DRAG = "drag"
    STATE_CLICK = "click"
    STATE_PET = "pet"

    # 鼠标移动超过该像素阈值才判定为“拖拽”，否则算“点击”
    DRAG_THRESHOLD = 5

    def __init__(self, config=None, lock=None):
        self.config = config or Config()
        self._lock = lock  # 持有单实例 socket 引用，程序退出前不要释放

        self.transparent_color = self.config.get("transparent_color")
        self.pet_size = int(self.config.get("pet_size"))

        # 主窗口：无边框 + 透明
        self.root = tk.Tk()
        self.root.title(f"DesktopPet v{__version__}")
        self.color_key_enabled = _setup_window(
            self.root, self.transparent_color
        )
        if self.config.get("topmost"):
            try:
                self.root.attributes("-topmost", True)
            except tk.TclError:
                pass

        try:
            self.root.attributes("-alpha", float(self.config.get("opacity")))
        except (tk.TclError, ValueError, TypeError):
            pass

        self.root.geometry(f"{self.pet_size}x{self.pet_size}+500+500")

        canvas_bg = (
            self.transparent_color if self.color_key_enabled else self.root.cget("bg")
        )
        self.canvas = tk.Canvas(
            self.root,
            width=self.pet_size,
            height=self.pet_size,
            bg=canvas_bg,
            highlightthickness=0,
        )
        self.canvas.pack()

        # 素材与动画
        self.assets_dir = resource_path("assets_processed")
        self._ensure_assets()
        self.anim = AnimationManager(self.assets_dir)
        self._build_packs()
        self.active_pack = self._resolve_initial_pack()
        self.load_all_animations()

        # 状态
        self.state = self.STATE_IDLE
        self.is_dragging = False
        self._drag_armed = False
        self._press_root_x = 0
        self._press_root_y = 0
        self.drag_start_x = 0
        self.drag_start_y = 0

        # 移动
        self.move_speed = int(self.config.get("move_speed"))
        self.movement_interval = int(self.config.get("movement_interval"))
        self.direction = 1  # 1=右, -1=左
        self.screen_width = self.root.winfo_screenwidth()

        # 屏幕边缘行为
        self.edge_bounce = bool(self.config.get("edge_bounce"))
        self.edge_pause_ms = int(self.config.get("edge_pause_ms"))

        # 行为计时
        self.walk_counter = 0
        self.idle_counter = 0
        self.is_resting = False
        self._edge_pause_ticks = 0  # 撞到边缘后的停顿倒计时（移动帧数）

        # 动画速度（毫秒）
        self.anim_speed = int(self.config.get("anim_speed"))
        self.walk_anim_speed = int(self.config.get("walk_anim_speed"))
        self.click_reaction_ms = int(self.config.get("click_reaction_ms"))

        self.current_photo = None

        # 系统感知与对话气泡
        self.awareness_enabled = bool(self.config.get("awareness"))
        self.greetings_enabled = bool(self.config.get("greetings"))
        self.awareness_interval = max(1, int(self.config.get("awareness_interval"))) * 1000
        self.awareness_memory = bool(self.config.get("awareness_memory"))
        self.awareness_battery = bool(self.config.get("awareness_battery"))
        self._base_move_speed = self.move_speed
        self._base_anim_speed = self.anim_speed
        self._base_walk_anim_speed = self.walk_anim_speed
        self._base_rest_chance = float(self.config.get("rest_chance"))
        self.rest_chance = self._base_rest_chance
        self.mood = None
        self._last_mood_name = None
        self.bubble = Bubble(self.root, self.pet_size)

        # 交互丰富度
        self.talk_on_click = bool(self.config.get("talk_on_click"))
        self.idle_chatter = bool(self.config.get("idle_chatter"))
        self.chatter_interval = max(3, int(self.config.get("chatter_interval"))) * 1000
        self.affinity = 0            # 亲密度：累计互动次数
        self._hopping = False
        self._click_timer = None

        self.bind_events()
        self.anim.set_animation(self.STATE_IDLE)

        # 启动定时器（循环常驻，开关由控制台实时生效）
        if self.awareness_enabled:
            self.refresh_awareness(initial=True)
        self.root.after(self.awareness_interval, self._awareness_tick)
        if self.greetings_enabled:
            self.say(greeting_for(time_period()))
        self.root.after(self.chatter_interval, self._chatter_tick)

        self.update_animation()
        self.update_movement()

    # ---------- 资源准备 ----------
    def _ensure_assets(self):
        """确保 assets_processed 存在；缺失时可自动从 assets 生成。"""
        has_processed = False
        if os.path.isdir(self.assets_dir):
            for _root, _dirs, files in os.walk(self.assets_dir):
                if any(f.lower().endswith(".png") for f in files):
                    has_processed = True
                    break
        if has_processed:
            return

        if not self.config.get("auto_prepare_assets"):
            logger.error(
                "缺少处理后素材，请先运行: python scripts/prepare_assets.py"
            )
            return

        src_root = resource_path("assets")
        if not os.path.isdir(src_root):
            logger.error(
                "既没有 %s，也找不到源素材 %s", self.assets_dir, src_root
            )
            return

        logger.info("未发现处理后的素材，正在自动处理 ...")
        from .prepare import prepare_all

        total = prepare_all(src_root, self.assets_dir)
        logger.info("自动处理完成，共 %d 张", total)

    # ---------- 角色包 ----------
    def _build_packs(self):
        """内置默认素材 + pets/ 下的角色包。"""
        default = Pack("default", self.assets_dir, {"name": "默认"})
        self.packs = [default]
        self.default_pack_index = 0
        pets_dir = resource_path(self.config.get("pets_dir"))
        extra = discover_packs(pets_dir)
        if extra:
            self.packs.extend(extra)
            logger.info("发现 %d 个角色包", len(extra))

    def _resolve_initial_pack(self):
        """按配置选择初始角色包，找不到就用默认素材。"""
        wanted = (self.config.get("pack") or "").strip()
        if wanted:
            for i, pack in enumerate(self.packs):
                if wanted in (pack.name, pack.display_name):
                    return i
            logger.warning("未找到角色包 %r，使用默认素材。", wanted)
        return self.default_pack_index

    def load_all_animations(self):
        """加载当前角色包的动画，缺失状态回退到默认素材。"""
        self.anim.clear()
        pack = self.packs[self.active_pack]
        default = self.packs[self.default_pack_index]
        for state in (self.STATE_IDLE, self.STATE_WALK_LEFT,
                      self.STATE_DRAG, self.STATE_CLICK, self.STATE_PET):
            count = self.anim.load_animation(state, pack.state_dir(state))
            if count == 0 and pack is not default:
                self.anim.load_animation(state, default.state_dir(state))

    def switch_pack(self, index):
        """切换到指定角色包。"""
        if not (0 <= index < len(self.packs)):
            return
        self.active_pack = index
        self.load_all_animations()
        self.is_resting = False
        self.is_dragging = False
        self._drag_armed = False
        self.set_state(self.STATE_IDLE)
        self.anim.set_animation(self.STATE_IDLE)
        self.update_display()
        logger.info("已切换角色: %s", self.packs[index].display_name)

    # ---------- 系统感知与对话 ----------
    def refresh_awareness(self, initial=False):
        """根据时间和 CPU 负载更新心情，并按比例调整行为参数。"""
        period = time_period()
        cpu = read_cpu_percent()
        memory = read_memory_percent() if self.awareness_memory else None
        battery = read_battery() if self.awareness_battery else None
        self.mood = compute_mood(period, cpu, memory, battery)

        self.move_speed = max(1, int(round(self._base_move_speed * self.mood.move_scale)))
        self.anim_speed = max(80, int(self._base_anim_speed * self.mood.anim_scale))
        self.walk_anim_speed = max(80, int(self._base_walk_anim_speed * self.mood.anim_scale))
        self.rest_chance = min(0.95, self._base_rest_chance * self.mood.rest_scale)

        if initial or self.mood.name != self._last_mood_name:
            batt = "N/A"
            if battery is not None:
                percent, plugged = battery
                batt = f"{percent:.0f}%{' 充电中' if plugged else ''}"
            logger.info(
                "心情: %s (%s) | 时段=%s | CPU=%s | 内存=%s | 电池=%s",
                self.mood.name,
                self.mood.label,
                period,
                "N/A" if cpu is None else f"{cpu:.0f}%",
                "N/A" if memory is None else f"{memory:.0f}%",
                batt,
            )
            self._last_mood_name = self.mood.name

    def _awareness_tick(self):
        if self.awareness_enabled:
            self.refresh_awareness()
        self.root.after(self.awareness_interval, self._awareness_tick)

    def say(self, text, duration_ms=3500):
        """通过气泡说一句话（失败不影响主程序）。"""
        if not text:
            return
        logger.info("桌宠说: %s", text)
        if self.bubble is not None:
            self.bubble.show(text, duration_ms)

    def greet(self):
        """右键“打个招呼”。"""
        if self.mood is not None:
            self.say(self.mood.label)
        else:
            self.say("你好呀～")

    def system_status(self):
        """汇总当前系统状态（时段 / CPU / 内存 / 电池 / 心情）为一段文本。"""
        period_label = {
            "morning": "早上", "day": "白天",
            "evening": "傍晚", "night": "夜晚",
        }.get(time_period(), "未知")
        cpu = read_cpu_percent()
        memory = read_memory_percent()
        battery = read_battery()
        lines = [f"时段：{period_label}"]
        lines.append("CPU：" + ("--" if cpu is None else f"{cpu:.0f}%"))
        lines.append("内存：" + ("--" if memory is None else f"{memory:.0f}%"))
        if battery is None:
            lines.append("电池：无 / 不可用")
        else:
            percent, plugged = battery
            lines.append(f"电池：{percent:.0f}%" + ("（充电中）" if plugged else ""))
        mood = self.mood.label if self.mood else "--"
        lines.append(f"当前心情：{mood}")
        return "\n".join(lines)

    def show_system_status(self):
        """右键“系统状态”：弹窗显示当前感知信息。"""
        messagebox.showinfo("系统状态", self.system_status())

    # ---------- 交互丰富度 ----------
    def _chatter_tick(self):
        """待机时偶尔自言自语一句。"""
        if (self.idle_chatter and self.state == self.STATE_IDLE
                and not self.is_dragging):
            self.say(random_line("chatter"))
        self.root.after(self.chatter_interval, self._chatter_tick)

    def _bounce(self, count=2, amplitude=12, duration=80):
        """原地上下来回弹跳一下，让反应更活泼。"""
        if self._hopping:
            return
        self._hopping = True
        base_x = self.root.winfo_x()
        base_y = self.root.winfo_y()

        def step(i):
            if i >= count * 2:
                self.root.geometry(f"+{base_x}+{base_y}")
                self._hopping = False
                return
            dy = -amplitude if i % 2 == 0 else 0
            self.root.geometry(f"+{base_x}+{base_y + dy}")
            self.root.after(duration, lambda: step(i + 1))

        step(0)

    def _do_click_reaction(self, pet=False):
        """点击 / 抚摸反应：切换动画 + 随机台词 + 弹跳。"""
        if pet:
            anim_name = self.STATE_PET if self.anim.has(self.STATE_PET) else self.STATE_CLICK
            self.state = self.STATE_PET
            category = "pet"
        else:
            anim_name = self.STATE_CLICK
            self.state = self.STATE_CLICK
            category = "click"

        self.is_dragging = False
        self._drag_armed = False
        self.anim.set_animation(anim_name)
        self.update_display()

        if self.talk_on_click:
            self.say(random_line(category))
        self._bounce()

        if self._click_timer is not None:
            try:
                self.root.after_cancel(self._click_timer)
            except (tk.TclError, ValueError):
                pass
        self._click_timer = self.root.after(self.click_reaction_ms, self.on_click_end)

    def on_double_click(self, event):
        """双击 = 抚摸。"""
        self.affinity += 1
        self._do_click_reaction(pet=True)

    # ---------- 事件绑定 ----------
    def bind_events(self):
        # 根窗口与画布都绑定，确保透明区域也能响应
        for widget in (self.root, self.canvas):
            widget.bind("<ButtonPress-1>", self.on_mouse_press)
            widget.bind("<B1-Motion>", self.on_mouse_drag)
            widget.bind("<ButtonRelease-1>", self.on_mouse_release)
            widget.bind("<Double-Button-1>", self.on_double_click)
            widget.bind("<Button-3>", self.on_right_click)
        # macOS 常见用 Button-2 作为右键
        self.root.bind("<Button-2>", self.on_right_click)

    # ---------- 显示 ----------
    def update_display(self):
        frame = self.anim.get_current_frame()
        if not frame:
            return
        if self.state == self.STATE_WALK_RIGHT:
            frame = frame.transpose(Image.FLIP_LEFT_RIGHT)
        self.current_photo = ImageTk.PhotoImage(frame)
        self.canvas.delete("all")
        self.canvas.create_image(
            self.pet_size // 2,
            self.pet_size // 2,
            image=self.current_photo,
            anchor=tk.CENTER,
        )

    def update_animation(self):
        self.anim.next_frame()
        self.update_display()
        if self.state in (self.STATE_WALK_LEFT, self.STATE_WALK_RIGHT):
            speed = self.walk_anim_speed
        else:
            speed = self.anim_speed
        self.root.after(speed, self.update_animation)

    # ---------- 移动 ----------
    def update_movement(self):
        if self.is_dragging or self._hopping or self.state in (
            self.STATE_CLICK, self.STATE_PET
        ):
            self.root.after(50, self.update_movement)
            return

        if self.is_resting:
            self.idle_counter += 1
            if self.idle_counter > random.randint(40, 100):
                self.is_resting = False
                self.idle_counter = 0
                self.direction = random.choice([-1, 1])
                self.set_state(
                    self.STATE_WALK_RIGHT if self.direction == 1 else self.STATE_WALK_LEFT
                )
        else:
            if self._edge_pause_ticks > 0:
                # 撞到边缘后的短暂停顿
                self._edge_pause_ticks -= 1
                self.root.after(self.movement_interval, self.update_movement)
                return
            self.walk_counter += 1
            x = self.root.winfo_x()
            y = self.root.winfo_y()
            new_x = x + self.direction * self.move_speed

            new_x, side = _clamp_x(new_x, self.screen_width, self.pet_size)
            if side is not None:
                # 撞到屏幕边缘：折返、可选弹跳，并短暂停顿
                self.direction = _direction_after(side)
                self.set_state(
                    self.STATE_WALK_RIGHT if self.direction == 1 else self.STATE_WALK_LEFT
                )
                if self.edge_bounce:
                    self._bounce()
                self._edge_pause_ticks = max(
                    1, self.edge_pause_ms // max(1, self.movement_interval)
                )

            self.root.geometry(f"+{new_x}+{y}")

            if self.walk_counter > random.randint(80, 200):
                if random.random() < self.rest_chance:
                    self.is_resting = True
                    self.walk_counter = 0
                    self.set_state(self.STATE_IDLE)

        self.root.after(self.movement_interval, self.update_movement)

    def set_state(self, new_state):
        if new_state != self.state:
            self.state = new_state
            if new_state == self.STATE_WALK_RIGHT:
                # 用同一套走图，显示时左右翻转
                self.anim.set_animation(self.STATE_WALK_LEFT)
            else:
                self.anim.set_animation(new_state)

    # ---------- 鼠标事件 ----------
    def on_mouse_press(self, event):
        self._press_root_x = event.x_root
        self._press_root_y = event.y_root
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        self._drag_armed = False
        self.is_dragging = False

    def on_mouse_drag(self, event):
        dx = abs(event.x_root - self._press_root_x)
        dy = abs(event.y_root - self._press_root_y)
        if not self._drag_armed:
            if dx < self.DRAG_THRESHOLD and dy < self.DRAG_THRESHOLD:
                return  # 还在阈值内，先不触发拖拽
            self._drag_armed = True
            self.is_dragging = True
            self.set_state(self.STATE_DRAG)

        x = self.root.winfo_x() + (event.x - self.drag_start_x)
        y = self.root.winfo_y() + (event.y - self.drag_start_y)
        self.root.geometry(f"+{x}+{y}")

    def on_mouse_release(self, event):
        was_dragging = self.is_dragging
        self.is_dragging = False
        self._drag_armed = False
        if was_dragging:
            # 拖拽结束：说一句拖拽台词并回到待机
            if self.talk_on_click:
                self.say(random_line("drag"))
            self.on_click_end()
        else:
            # 单击：累计亲密度并播放点击反应
            self.affinity += 1
            self._do_click_reaction(pet=False)

    def on_click_end(self):
        self.is_resting = True
        self.idle_counter = 0
        self.set_state(self.STATE_IDLE)

    def on_right_click(self, event):
        menu = tk.Menu(self.root, tearoff=0)
        menu.configure(bg="#2d2d2d", fg="white", activebackground="#4a9eff")
        if len(self.packs) > 1:
            submenu = tk.Menu(menu, tearoff=0)
            for i, pack in enumerate(self.packs):
                mark = "● " if i == self.active_pack else "   "
                submenu.add_command(
                    label=f"{mark}{pack.display_name}",
                    command=lambda i=i: self.switch_pack(i),
                )
            menu.add_cascade(label="切换角色", menu=submenu)
            menu.add_separator()
        menu.add_command(label="设置面板…", command=self.open_control_panel)
        menu.add_command(label="打个招呼", command=self.greet)
        menu.add_command(label="系统状态", command=self.show_system_status)
        menu.add_command(label="关于桌宠", command=self.show_about)
        menu.add_separator()
        menu.add_command(label="退出", command=self.quit_app)
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def show_about(self):
        # 打包为 GUI 程序后没有控制台，必须用弹窗而非 print
        mood_line = f"当前状态：{self.mood.label}" if self.mood else "状态：--"
        messagebox.showinfo(
            "关于桌宠",
            f"DesktopPet v{__version__}\n\n"
            "一个可爱的桌面小伙伴。\n"
            "左键拖拽移动 / 单击互动 / 双击抚摸 / 右键菜单\n\n"
            f"{mood_line}\n"
            f"亲密度：{self.affinity} 次互动",
        )

    def quit_app(self):
        self.root.destroy()

    # ---------- 桌面控制台 ----------
    def open_control_panel(self):
        """打开（或聚焦）桌面控制台设置面板。"""
        try:
            from .ui.panel import ControlPanel
        except Exception as e:  # noqa: BLE001
            logger.warning("控制台不可用: %s", e)
            messagebox.showwarning("控制台", f"无法加载控制台：{e}")
            return
        if getattr(self, "_panel", None) is None:
            self._panel = ControlPanel(pet=self, config=self.config)
        self._panel.open()

    def apply_config(self):
        """从 config 重新读取并即时应用设置（供控制台调用）。"""
        self.pet_size = int(self.config.get("pet_size"))
        self.move_speed = int(self.config.get("move_speed"))
        self._base_move_speed = self.move_speed
        self.movement_interval = int(self.config.get("movement_interval"))
        self.edge_bounce = bool(self.config.get("edge_bounce"))
        self.edge_pause_ms = int(self.config.get("edge_pause_ms"))
        self._base_anim_speed = int(self.config.get("anim_speed"))
        self._base_walk_anim_speed = int(self.config.get("walk_anim_speed"))
        self._base_rest_chance = float(self.config.get("rest_chance"))
        self.anim_speed = self._base_anim_speed
        self.walk_anim_speed = self._base_walk_anim_speed
        self.rest_chance = self._base_rest_chance
        self.click_reaction_ms = int(self.config.get("click_reaction_ms"))
        self.talk_on_click = bool(self.config.get("talk_on_click"))
        self.idle_chatter = bool(self.config.get("idle_chatter"))
        self.chatter_interval = max(3, int(self.config.get("chatter_interval"))) * 1000
        self.awareness_enabled = bool(self.config.get("awareness"))
        self.greetings_enabled = bool(self.config.get("greetings"))
        self.awareness_interval = max(1, int(self.config.get("awareness_interval"))) * 1000
        self.awareness_memory = bool(self.config.get("awareness_memory"))
        self.awareness_battery = bool(self.config.get("awareness_battery"))

        # 窗口层级
        try:
            self.root.attributes("-topmost", bool(self.config.get("topmost")))
        except tk.TclError:
            pass
        # 不透明度
        try:
            self.root.attributes("-alpha", float(self.config.get("opacity")))
        except (tk.TclError, ValueError, TypeError):
            pass
        # 尺寸（窗口 + 画布）
        try:
            self.canvas.config(width=self.pet_size, height=self.pet_size)
            self.root.geometry(f"{self.pet_size}x{self.pet_size}")
            self.bubble.pet_size = self.pet_size
        except tk.TclError:
            pass

        if self.awareness_enabled:
            self.refresh_awareness()
        else:
            self.mood = None
        logger.info("已应用设置")

    def run(self):
        logger.info("=" * 40)
        logger.info("桌宠已启动 v%s", __version__)
        logger.info("窗口位置: (%s, %s)", self.root.winfo_x(), self.root.winfo_y())
        logger.info("窗口大小: %sx%s", self.pet_size, self.pet_size)
        logger.info("已加载动画: %s", list(self.anim.animations.keys()))
        logger.info("操作说明: 左键拖拽移动 / 左键点击互动 / 右键菜单")
        logger.info("=" * 40)
        if not self.anim.animations:
            logger.error("没有任何动画帧被加载，请检查素材目录。")
        self.root.mainloop()


def main():
    """程序入口，返回进程退出码。"""
    handlers = [logging.StreamHandler()]
    try:
        from ._paths import log_file

        handlers.append(logging.FileHandler(log_file(), encoding="utf-8"))
    except Exception:  # noqa: BLE001  —— 无法写日志文件时仍可运行
        pass
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
        handlers=handlers,
    )

    lock = None
    try:
        config = Config()
        if config.get("single_instance"):
            lock = _acquire_lock()
            if lock is None:
                logger.warning("检测到桌宠已在运行，本次启动退出。")
                return 0
        pet = DesktopPet(config=config, lock=lock)
        pet.run()
        return 0
    except Exception:  # noqa: BLE001
        logger.exception("桌宠运行异常")
        return 1


__all__ = ["DesktopPet", "main"]
