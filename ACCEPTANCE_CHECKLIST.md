# ACCEPTANCE_CHECKLIST.md

## 一、结构清理验收

- [ ] 已审计 `src/camera.py`、`src/game.py`、`src/npc.py`、`src/player.py`、`src/scene.py`、`src/tilemap.py` 是否仍被引用。
- [ ] 未被运行时代码引用的旧 wrapper 已移动到 `src/legacy/compat/`。
- [ ] `src/legacy/README.md` 已说明 legacy 目录用途。
- [ ] README 已同步当前模块化结构。
- [ ] docs 已同步当前主线和预留功能说明。
- [ ] 未修改 Tiled 地图、tileset、图片、音频、字体资源。

## 二、当前主线验收

- [ ] 游戏能启动。
- [ ] 菜单能进入游戏。
- [ ] `village_hub` 背景正常显示。
- [ ] 玩家可以移动。
- [ ] NPC 对话正常。
- [ ] B 背包正常。
- [ ] 集市寻源收集正常。
- [ ] Space 银光净化正常。
- [ ] 节庆守护正常。
- [ ] Ending 结尾评价正常。

## 三、编译验证

```powershell
python -m py_compile main.py
python -m py_compile src/core/game.py
python -m py_compile src/scenes/playing_scene.py
python -m py_compile src/systems/main_quest_manager.py
python -m py_compile src/systems/shadow_chase_manager.py
python -m py_compile src/systems/festival_defense_manager.py
python -m compileall src
```

## 四、项目结构验收

- [ ] `main.py` 只作为启动入口。
- [ ] 当前核心逻辑位于 `src/core`、`src/scenes`、`src/maps`、`src/entities`、`src/systems`、`src/ui`。
- [ ] 早期兼容文件不再混在 `src/` 根目录。
- [ ] 预留模块已说明用途，不误写成当前完整实现。
