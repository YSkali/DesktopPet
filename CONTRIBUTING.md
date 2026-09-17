# 贡献指南 Contributing

感谢你对 DesktopPet 感兴趣！欢迎通过 Issue 或 Pull Request 参与。

## 开发环境

```bash
git clone https://github.com/yourname/desktoppet.git
cd desktoppet
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt -r requirements-dev.txt
```

## 运行

```bash
python scripts/prepare_assets.py   # 处理素材（生成 assets_processed/）
python run.py                      # 启动桌宠
```

## 测试

```bash
pytest -q
```

## 提交规范

- 请保持代码风格一致，提交前确保 `pytest` 通过。
- 提交信息建议使用 [Conventional Commits](https://www.conventionalcommits.org/)：
  `feat: ...` / `fix: ...` / `docs: ...` / `refactor: ...` / `chore: ...`

## 想贡献新角色/素材？

1. 在 `assets/` 下新建一个角色目录，放入 `idle/`、`walk_left/`、`drag/`、`click/` 各状态图片
   （建议白底、128×128，程序会自动去背）。
2. 运行 `python scripts/prepare_assets.py` 检查效果。
3. 附上截图/GIF 提交 PR。

## 发布流程（维护者）

1. 更新 `desktoppet/version.py` 中的 `__version__`。
2. 在 `CHANGELOG.md` 记录本次变更。
3. 提交后打 tag 并推送：
   ```bash
   git tag v1.1.0
   git push origin v1.1.0
   ```
4. GitHub Actions 会自动构建并创建 Release（见 `.github/workflows/release.yml`）。
