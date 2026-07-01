# Legacy Compatibility Wrappers

本目录保存早期 `src/` 根目录下的兼容 wrapper：

- `camera.py`
- `game.py`
- `npc.py`
- `player.py`
- `scene.py`
- `tilemap.py`

这些文件只做旧导入路径的转发留档。当前运行时代码没有引用它们，核心实现已迁移到 `src/core`、`src/scenes`、`src/maps`、`src/entities`。
