#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DesktopPet 一键自检脚本 / one-click self-test.

自动检查运行环境、依赖、素材处理、角色包、配置、版本一致性与打包配置，
并输出清晰的通过/失败报告。适用于本地验收与 CI 前置检查。

用法::

    python scripts/check.py            # 完整自检
    python scripts/check.py --skip-tests   # 跳过单元测试（未装 pytest 时）

退出码：全部通过 = 0，存在失败 = 1。
"""

import argparse
import os
import py_compile
import subprocess
import sys
import tempfile
import traceback

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

PASS, FAIL, SKIP = "PASS", "FAIL", "SKIP"
ICON = {PASS: "[PASS]", FAIL: "[FAIL]", SKIP: "[SKIP]"}


class SkipCheck(Exception):
    """用于标记“跳过”而非失败。"""


class Checker:
    def __init__(self):
        self.results = []  # (name, status, detail)

    def run(self, name, fn):
        try:
            detail = fn()
            self.results.append((name, PASS, detail or "OK"))
        except SkipCheck as e:
            self.results.append((name, SKIP, str(e)))
        except Exception as e:  # noqa: BLE001
            self.results.append((name, FAIL, f"{type(e).__name__}: {e}"))
            if os.environ.get("CHECK_DEBUG"):
                traceback.print_exc()


# ---------- 各项检查 ----------

def check_python():
    if sys.version_info < (3, 9):
        raise AssertionError(f"需要 Python 3.9+，当前 {sys.version.split()[0]}")
    return f"Python {sys.version.split()[0]}"


def check_dependencies():
    import PIL  # noqa: F401
    import tkinter  # noqa: F401
    return f"Pillow {PIL.__version__}, Tk {tkinter.TkVersion}"


def check_imports():
    import importlib

    mods = [
        "desktoppet",
        "desktoppet.pet",
        "desktoppet.animation",
        "desktoppet.config",
        "desktoppet.prepare",
        "desktoppet.packs",
        "desktoppet.awareness",
        "desktoppet.bubble",
        "desktoppet.pipeline",
        "desktoppet.version",
        "desktoppet.ui",
        "desktoppet.ui.theme",
        "desktoppet.ui.context",
        "desktoppet.ui.registry",
        "desktoppet.ui.widgets",
        "desktoppet.ui.widgets.fields",
        "desktoppet.ui.widgets.form",
        "desktoppet.ui.panel",
        "desktoppet.ui.pages",
    ]
    for m in mods:
        importlib.import_module(m)
    return f"{len(mods)} 个模块导入成功"


def check_bytecompile():
    files = []
    for base in ("desktoppet", "scripts"):
        d = os.path.join(ROOT, base)
        for r, _dirs, fs in os.walk(d):
            files += [os.path.join(r, f) for f in fs if f.endswith(".py")]
    run_py = os.path.join(ROOT, "run.py")
    if os.path.isfile(run_py):
        files.append(run_py)
    # 编译产物写入临时目录，避免污染用户目录
    with tempfile.TemporaryDirectory() as tmp:
        for i, f in enumerate(files):
            py_compile.compile(f, cfile=os.path.join(tmp, f"{i}.pyc"), doraise=True)
    return f"{len(files)} 个文件编译通过"


def check_assets_pipeline():
    from PIL import Image

    from desktoppet.prepare import TARGET_SIZE, process_image

    with tempfile.TemporaryDirectory() as tmp:
        src = os.path.join(tmp, "src.png")
        dst = os.path.join(tmp, "out.png")
        Image.new("RGB", (300, 200), (255, 255, 255)).save(src)
        assert process_image(src, dst), "process_image 返回 False"
        with Image.open(dst) as out:
            assert out.size == TARGET_SIZE, f"尺寸异常: {out.size}"
            assert out.mode == "RGBA", f"通道异常: {out.mode}"

    proc = os.path.join(ROOT, "assets_processed")
    count = 0
    if os.path.isdir(proc):
        for r, _dirs, fs in os.walk(proc):
            count += sum(1 for f in fs if f.lower().endswith(".png"))
    return f"处理管线 OK；assets_processed 现有 {count} 张"


def check_packs():
    from desktoppet.packs import discover_packs

    packs = discover_packs(os.path.join(ROOT, "pets"))
    return f"发现 {len(packs)} 个角色包: {[p.name for p in packs]}"


def check_control_panel():
    from desktoppet.config import DEFAULTS

    from desktoppet.ui.registry import load_pages
    from desktoppet.ui.widgets.fields import BUILDERS

    pages = load_pages()
    assert pages, "未发现任何控制台页面"
    ids = [p.id for p in pages]
    assert len(ids) == len(set(ids)), f"页面 id 重复: {ids}"
    for p in pages:
        assert getattr(p, "title", ""), f"{p.id} 缺少标题"
        fields = getattr(p, "fields", ())
        for field in fields:
            assert field["key"] in DEFAULTS, f"{p.id}: 未知配置键 {field['key']}"
            kind = field.get("kind", "str")
            assert kind in BUILDERS, f"{p.id}: 未知字段类型 {kind}"
    return f"{len(pages)} 个页面: {ids}；字段类型 {sorted(BUILDERS)}"


def check_config():
    from desktoppet.config import Config

    with tempfile.TemporaryDirectory() as tmp:
        p = os.path.join(tmp, "config.json")
        c = Config(path=p)
        assert c.save(p), "配置写入失败"
        c2 = Config(path=p)
        assert c2.get("move_speed") == c.get("move_speed"), "读写不一致"
    return "读写往返一致"


def check_version_consistency():
    import re

    from desktoppet.version import __version__

    setup_cx = os.path.join(ROOT, "packaging", "setup_cx.py")
    with open(setup_cx, encoding="utf-8") as f:
        src = f.read()
    m = re.search(r'version="([^"]+)"', src)
    if not m:
        raise AssertionError("packaging/setup_cx.py 未找到 version 字段")
    if m.group(1) != __version__:
        raise AssertionError(
            f"版本不一致: version.py={__version__} setup_cx={m.group(1)}"
        )
    return f"版本一致: {__version__}"


def check_packaging_syntax():
    import ast

    with open(os.path.join(ROOT, "packaging", "setup_cx.py"), encoding="utf-8") as f:
        ast.parse(f.read())
    return "setup_cx.py 语法 OK"


def check_tests():
    try:
        import pytest  # noqa: F401
    except ImportError:
        raise SkipCheck("未安装 pytest（pip install pytest）")

    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"],
        cwd=ROOT, capture_output=True, text=True, env=env,
    )
    lines = (proc.stdout + proc.stderr).strip().splitlines()
    summary = lines[-1] if lines else "(无输出)"
    if proc.returncode != 0:
        raise AssertionError(f"pytest 失败: {summary}")
    return summary


def check_pipeline():
    from PIL import Image

    from desktoppet.pipeline import build_pet, classify_state

    assert classify_state("idle_01") == "idle"
    assert classify_state("向左走") == "walk_left"
    assert classify_state("点击") == "click"
    with tempfile.TemporaryDirectory() as tmp:
        src = os.path.join(tmp, "upload", "cat", "idle")
        os.makedirs(src)
        Image.new("RGB", (100, 100), (255, 255, 255)).save(os.path.join(src, "01.png"))
        r = build_pet(os.path.join(tmp, "upload", "cat"), "cat",
                      out_dir=os.path.join(tmp, "pets"))
        assert r["total"] == 1, r
    return "图片→角色包 生成 OK"


# ---------- 主流程 ----------
def build_checks(skip_tests):
    checks = [
        ("Python 版本", check_python),
        ("依赖 Pillow/Tk", check_dependencies),
        ("模块导入", check_imports),
        ("语法编译", check_bytecompile),
        ("素材处理管线", check_assets_pipeline),
        ("角色包发现", check_packs),
        ("图片流水线", check_pipeline),
        ("桌面控制台", check_control_panel),
        ("配置读写", check_config),
        ("版本一致性", check_version_consistency),
        ("打包配置语法", check_packaging_syntax),
    ]
    if not skip_tests:
        checks.append(("单元测试", check_tests))
    return checks


def main(argv=None):
    parser = argparse.ArgumentParser(description="DesktopPet 一键自检")
    parser.add_argument("--skip-tests", action="store_true", help="跳过单元测试")
    args = parser.parse_args(argv)

    checker = Checker()
    print("=" * 60)
    print(" DesktopPet 自检 / Self-Test")
    print("=" * 60)

    for name, fn in build_checks(args.skip_tests):
        checker.run(name, fn)

    width = max(len(n) for n, _s, _d in checker.results)
    n_pass = n_fail = n_skip = 0
    for name, status, detail in checker.results:
        print(f"{ICON[status]} {name.ljust(width)}  {detail}")
        if status == PASS:
            n_pass += 1
        elif status == FAIL:
            n_fail += 1
        else:
            n_skip += 1

    print("-" * 60)
    print(f"结果: {n_pass} 通过 / {n_fail} 失败 / {n_skip} 跳过")
    if n_fail == 0:
        print("✅ 自检通过，可以启动: 双击 start.bat 或运行 python run.py")
    else:
        print("❌ 自检未通过，请根据上面的 [FAIL] 项排查。")
    print("=" * 60)
    return 1 if n_fail else 0


if __name__ == "__main__":
    # Windows 终端默认 GBK，打印 emoji 会崩溃；强制 UTF-8 输出
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    sys.exit(main())
