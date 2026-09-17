# 上传目录 Upload

把要做成桌宠的图片放到这里，然后运行流水线即可自动生成角色包。

## 用法

```bash
python scripts/build_pet.py           # 处理 upload/ 下所有角色目录
python scripts/build_pet.py upload/cat   # 只处理某一个
```

或在 Windows 双击 `build_pet.bat`。

## 目录组织（三种方式，可混用）

```
upload/
└── cat/                     ← 一个子目录 = 一只桌宠（目录名即角色标识）
    ├── idle/01.png          ← ① 用「状态子目录」分类
    ├── idle/02.png
    ├── walk_left/01.png
    ├── click/01.png
    └── drag/01.png
```

```
upload/
└── dog/
    ├── idle_01.png          ← ② 用「文件名前缀」分类
    ├── idle_02.png
    ├── walk_01.png
    └── click.png
```

```
upload/
└── plain/
    ├── 01.png               ← ③ 无提示 → 全部当作 idle（但帧宠物）
    └── 02.png
```

## 状态关键字（英文 / 中文都认）

| 状态 | 可用关键字 |
|------|-----------|
| 待机 idle | `idle`、`stand`、`wait`、`待机`、`静止`、`站立` |
| 走路 walk_left | `walk`、`walk_left`、`left`、`走`、`行走`、`向左走`、`移动` |
| 点击 click | `click`、`tap`、`点击`、`被点击`、`戳` |
| 拖拽 drag | `drag`、`拖拽`、`拖`、`被拖拽`、`拎起` |
| 抚摸 pet | `pet`、`pat`、`抚摸`、`摸头`、`摸摸` |

> 只有 `idle` 是必需的；其余状态缺失时会自动回退。
> 图片建议**白底**，程序会自动去背并统一为 128×128。

## 会发生什么

1. 自动去白底、统一尺寸；
2. 按状态分类，输出到 `pets/<角色名>/<状态>/NN.png`；
3. 生成 `pets/<角色名>/manifest.json`；
4. 重启桌宠 → 右键菜单 → 切换角色。
