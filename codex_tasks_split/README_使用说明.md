# Codex 任务文件拆分包使用说明

本目录保存早期 Task 00-04 的拆分任务文档，主要用于追溯项目从基础工程到地图、碰撞、对象层读取的开发过程。

当前真实项目已经进入模块化演示版本，核心结构以以下目录为准：

```text
src/core
src/scenes
src/maps
src/entities
src/systems
src/ui
src/resources
src/minigames
```

当前演示主线为：

```text
村寨长者对话 -> 集市寻源 -> 河谷影纹净化 -> 节庆广场守护 -> Ending
```

如果继续使用本目录下的早期任务文档，请注意：

1. 文档中的 `src/game.py`、`src/scene.py`、`src/tilemap.py` 等旧路径是历史阶段说明。
2. 当前实现应优先修改 `src/core`、`src/scenes`、`src/maps`、`src/entities`、`src/systems`、`src/ui` 下的模块。
3. 不要按早期文档把逻辑重新写回 `src/` 根目录单文件结构。
4. 不要移动或修改 `assets/maps`、`assets/tilesets`、`assets/tiled`、`assets/sprites` 等资源。
