# DEVELOPMENT_RULES.md

## 1. 总体原则

1. 先保证当前演示主线可启动、可交互、可验收，再做扩展。
2. 修改必须保持项目可运行，不破坏上一阶段功能。
3. 当前核心结构以 `src/core`、`src/scenes`、`src/maps`、`src/entities`、`src/systems`、`src/ui` 为准。
4. `main.py` 只作为启动入口，不承载业务逻辑。
5. 不要把逻辑回退到 `src/` 根目录单文件结构。
6. 不要移动或删除 `assets/maps`、`assets/tilesets`、`assets/sprites`、`assets/audio`、`data`、`tools` 中运行所需文件。

## 2. 当前主线

```text
村寨长者对话 -> 集市寻源 -> 河谷影纹净化 -> 节庆广场守护 -> Ending
```

清理、文档同步或局部修复任务不得改变上述流程，不得改动地图跳转、NPC 对话、影纹战斗、背包、Ending、音效和语音系统逻辑。

## 3. 代码结构规范

- `src/core/game.py`：游戏主循环、窗口、顶层状态和场景切换。
- `src/scenes/`：菜单、开场、主游戏、预留结尾/修复场景。
- `src/maps/`：Tiled 地图读取、摄像机、碰撞、对象加载。
- `src/entities/`：玩家、NPC、影纹、物品和交互实体。
- `src/systems/`：主线、收集、影纹、节庆守护、音频、评分等系统。
- `src/ui/`：HUD、对话框、背包状态、任务箭头、Ending 面板。
- `src/resources/`：字体和资源加载辅助。
- `src/minigames/`：预留小游戏模块。
- `src/legacy/`：早期遗留或兼容文件，不作为当前主流程入口。

## 4. 地图与数据规范

- 当前 TMX 地图位于 `assets/maps/`。
- tileset 资源位于 `assets/tilesets/`。
- 场景、对话、物品、任务等配置位于 `data/`。
- Tiled 对象层命名保持：`collision`、`object_points`、`npc_points`、`pattern_points`、`clue_points`、`checkpoint_points`、`trigger_points`。
- 可交互对象至少包含 `id` 和 `type`。

## 5. 预留功能说明

以下内容可以保留代码或文档入口，但不得在未明确任务时扩展主线：

- 完整工坊敲银修复小游戏；
- 完整图鉴；
- 本地存档；
- 更多语音和音效；
- 多结局和支线任务。

## 6. AI / Codex 协作规范

1. 开发前先阅读当前任务要求和项目文档。
2. 一次只处理一个明确任务。
3. 不做无关重构。
4. 缺少素材时使用占位或保留预留入口，不阻塞主流程。
5. 完成后说明修改文件、运行方式、测试方法、已知未完成点和是否影响上一阶段功能。

## 7. 验证规范

基础验证至少包括：

```powershell
python -m py_compile main.py
python -m py_compile src/core/game.py
python -m py_compile src/scenes/playing_scene.py
python -m py_compile src/systems/main_quest_manager.py
python -m py_compile src/systems/shadow_chase_manager.py
python -m py_compile src/systems/festival_defense_manager.py
python -m compileall src
python main.py
```

真实窗口验收重点：

- 游戏能启动；
- 菜单能进入游戏；
- `village_hub` 背景正常显示；
- NPC 对话正常；
- B 背包正常；
- 影纹净化不受影响；
- 节庆守护不受影响；
- Ending 不受影响。
