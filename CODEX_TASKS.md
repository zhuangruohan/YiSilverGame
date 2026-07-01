# CODEX_TASKS.md

## 当前任务

当前任务：`project-structure-cleanup-doc-sync`

目标：清理旧版遗留代码入口、统一当前模块化结构说明，并同步 README / docs 中与当前项目不符的内容。

## 当前真实结构

```text
src/core
src/scenes
src/maps
src/entities
src/systems
src/ui
src/resources
src/minigames
src/legacy
tools
assets
data
docs
puml
```

旧 `src/*.py` 单文件入口如果未被运行时代码引用，应移动到 `src/legacy/compat/` 保留；如果仍被引用，应保留原位并注明兼容 wrapper。

## 当前主线

```text
村寨长者对话 -> 集市寻源 -> 河谷影纹净化 -> 节庆广场守护 -> Ending
```

## 禁止事项

- 不要修改游戏主线流程。
- 不要修改地图跳转逻辑。
- 不要修改 NPC 对话逻辑。
- 不要修改影纹战斗逻辑。
- 不要修改背包、Ending、音效、语音系统逻辑。
- 不要修改 Tiled 地图、tileset 和源资源。
- 不要删除 `data/scenes.json`、`dialogues.json`、`items.json`、`tasks.json`。
- 不要删除 `tools/` 下生成脚本。
- 不要新增新玩法。

## 后续可选扩展

- 工坊修复小游戏；
- 完整图鉴；
- 更多语音；
- 存档系统；
- 更多支线与多结局。
