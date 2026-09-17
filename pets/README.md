# 角色包 Character Packs

把自定义角色放入本目录，即可在桌宠**右键菜单 → 切换角色**中随时切换。
无需改动任何代码或重新打包（源码运行时）。

## 目录格式

```
pets/
└── my_pet/               ← 目录名即角色包标识
    ├── manifest.json     ← 可选，描述信息
    ├── idle/             ← 待机帧（2–8 张）
    │   ├── 01.png
    │   └── 02.png ...
    ├── walk_left/        ← 向左走帧（4–8 张，向右走自动镜像）
    ├── click/            ← 点击反应（1 张）
    └── drag/             ← 拖拽状态（1 张）
```

- 图片建议为白底、128×128，程序会自动去背并统一尺寸。
- 缺少的状态会自动回退到内置默认素材。
- 以 `_` 或 `.` 开头的目录会被忽略（见 `_template/`）。

## manifest.json 示例

```json
{
  "name": "咪咪",
  "author": "yourname",
  "description": "一只橘猫"
}
```

## 如何制作

**方式一：脚本一键生成（推荐）**

把图片放进 `upload/<角色名>/`（可用状态子目录或文件名前缀分类），然后：

```bash
python scripts/build_pet.py                       # 处理 upload/ 下所有角色目录
python scripts/build_pet.py upload/my_pet --display-name "咪咪" --author yourname
```

详见项目根目录的 `upload/README.md` 与 [README.md](../README.md)「上传图片 → 一键生成」章节。

**方式二：手动放置**

把已经处理好的 PNG 直接放进 `pets/<name>/<state>/`，再补一个 `manifest.json` 即可。

制作完成后重启桌宠，右键菜单里就会出现"切换角色"。

## 内置角色包

项目已内置 7 个 **CC0 公共领域**像素动物角色包（小鹿 / 小熊 / 小狼 / 小狐狸 / 小野猪 / 小兔子 / 小马），
素材来自 [OpenGameArt](https://opengameart.org) 的 ScratchIO 作品，开箱即用。
可用 `python scripts/build_packs_from_oga.py --src <素材目录>` 复现生成。
