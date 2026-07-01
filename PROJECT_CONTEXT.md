# PROJECT_CONTEXT.md

## 项目名称

《银纹秘境：彝饰守护者》

## 项目定位

这是一个基于 **Python + Pygame + Tiled + PyTMX + JSON** 的 2D 单人离线民族文化探索 RPG Demo。当前版本服务于课程演示，重点是跑通一条可展示、可验收的主线流程。

## 当前主线流程

```text
村寨长者对话 -> 集市寻源 -> 河谷影纹净化 -> 节庆广场守护 -> Ending
```

当前已完成的核心演示内容：

1. 主菜单进入游戏；
2. Tiled 地图读取、摄像机和碰撞；
3. 玩家移动与对象层交互；
4. NPC 对话；
5. 集市寻源收集；
6. 河谷影纹净化；
7. 节庆广场守护；
8. 背包收集状态面板；
9. Ending 结尾评价。

## 技术约束

1. 必须使用 Python + Pygame。
2. 地图使用 Tiled 制作，使用 PyTMX 读取 TMX。
3. 视窗为 800x600，瓦片标准为 32x32。
4. `main.py` 只作为启动入口。
5. 核心逻辑必须保持模块化，不允许回退到 `src/` 根目录单文件结构。
6. 不要移动或删除 Tiled 地图、tileset、图片、音频、字体和工具脚本。
7. 当前清理类任务不得修改主线、地图跳转、NPC 对话、影纹战斗、背包、Ending、音效或语音逻辑。

## 当前目录结构

```text
main.py                  启动入口
settings.py              全局配置
data/                    场景、对话、物品、任务配置
assets/                  地图、角色、音频、UI 等资源
src/core/                游戏主循环、状态、事件
src/scenes/              菜单、开场、主游戏、结尾等场景
src/maps/                Tiled 地图读取、摄像机、碰撞、对象加载
src/entities/            玩家、NPC、影纹、物品实体
src/systems/             主线、收集、战斗、节庆守护、音频、评分等系统
src/ui/                  HUD、对话框、背包、任务箭头、Ending 面板
src/resources/           字体、图片等资源加载辅助
src/minigames/           预留小游戏模块
src/legacy/              早期遗留或兼容文件
tools/                   音效、BGM、语音生成工具脚本
docs/                    设计文档和阶段任务
puml/                    用例图 / UML 辅助文档
```

早期 `src/game.py`、`src/scene.py`、`src/tilemap.py`、`src/camera.py`、`src/player.py`、`src/npc.py` 这类根目录兼容入口已迁移到 `src/legacy/compat/`，当前主流程不依赖它们。

## 当前模块说明

- `src/core/game.py`：游戏窗口、主循环、顶层场景切换。
- `src/scenes/playing_scene.py`：当前主游戏场景，负责地图、玩家、交互和演示主线调度。
- `src/maps/tilemap.py`：Tiled 地图、对象层、碰撞、出口读取。
- `src/entities/`：玩家、NPC、影纹和可交互物体。
- `src/systems/main_quest_manager.py`：当前三关卡主线状态。
- `src/systems/task_manager.py`：早期轻量任务状态，仍被影纹追逐相关旧逻辑引用，暂保留。
- `src/ui/simple_inventory_panel.py`：当前使用的小型背包/进度面板。
- `src/ui/inventory_panel.py`：预留完整背包 UI，占位保留。
- `src/ui/ending_panel.py`：当前 Ending 结算面板。
- `src/scenes/ending_scene.py`：预留 Ending 场景壳。
- `src/minigames/repair_minigame.py`、`src/scenes/repair_scene.py`：工坊修复小游戏预留模块。

## 后续扩展

后续可扩展但当前不作为已完整实现内容：

- 完整工坊敲银修复小游戏；
- 完整图鉴系统；
- 更多语音和音效；
- 本地存档；
- 更丰富的支线任务和多结局。

## AI 辅助开发过程

1. 前期由开发者确定主题、需求和关卡结构。
2. AI 提供初始框架和模块实现建议。
3. 开发者根据课程要求提出修改意见，例如模块化、Tiled 对象层、三关卡顺序、战斗特效、背包小型化、节庆真实入口。
4. 每次 AI 修改后，开发者本地运行、截图、查看日志并验收。
5. 最终形成“需求拆解 -> AI 辅助实现 -> 人工验收修正”的开发流程。

## 文化表达原则

- 不猎奇化、不滥编复杂民俗细节。
- 对缺乏确定来源的纹样寓意，使用“游戏化转译”表达。
- 用探索、收集、净化、守护和结尾评价承载文化主题。
