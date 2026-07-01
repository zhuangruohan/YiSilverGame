# Legacy

`legacy` 目录保存早期开发阶段遗留或兼容文件，避免直接删除后影响回溯。

当前核心演示逻辑以以下目录为准：

- `src/core`
- `src/scenes`
- `src/maps`
- `src/entities`
- `src/systems`
- `src/ui`

`src/legacy/compat/` 保存早期 `src/*.py` 单文件入口的兼容 wrapper。当前主流程不从 `legacy` 导入这些文件。
