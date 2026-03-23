# ha-config-mcp

## リリース

依存更新やバグ修正が溜まったら定期的に PyPI に publish する。

```bash
# バージョンを pyproject.toml で上げてから
gh release create v0.x.x --title "v0.x.x" --generate-notes
```

GitHub Release を作ると `.github/workflows/pypi-publish.yaml` が Trusted Publisher 経由で PyPI に自動 publish する。

## スタック

- Python + click (CLI) + mcp SDK (MCP server)
- uv (依存管理・ロック) + uv2nix (Nix パッケージ化)
- lefthook: pre-commit で `uv lock --check`
