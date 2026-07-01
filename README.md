# 《银纹秘境：彝饰守护者》

《银纹秘境：彝饰守护者》是一个基于 **Python + Pygame + Tiled + PyTMX + JSON** 的 2D 民族文化探索 RPG Demo。玩家在村寨、集市、河谷和节庆广场中推进课程演示主线，通过对话、收集、净化和守护完成一条可运行的文化探索流程。

当前版本重点是课程演示版本，已完成三关卡主线和基本系统。后续可继续扩展工坊修复小游戏、图鉴、更多语音和存档系统。

## 核心玩法

- 村寨长者对话
- 集市寻源收集
- 河谷影纹净化
- 节庆广场守护
- 背包收集状态
- Ending 结尾评价

当前主线流程：

```text
村寨长者对话 -> 集市寻源 -> 河谷影纹净化 -> 节庆广场守护 -> Ending
```

## 运行方式

安装依赖：

```powershell
pip install -r requirements.txt
```

运行游戏：

```powershell
python main.py
```

Windows 本地如果 `python` 没有指向项目环境，可使用：

```powershell
.\.venv\Scripts\python.exe main.py
```

## 操作说明

- WASD / 方向键：移动
- E / Enter：交互
- Space：银光净化
- B：背包
- F3：Debug 面板
- F4/F5/F6：演示调试关卡
- Esc：关闭面板 / 返回

## 项目结构

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

`src/` 根目录早期单文件入口已迁移到 `src/legacy/compat/`。当前核心演示逻辑以 `src/core`、`src/scenes`、`src/maps`、`src/entities`、`src/systems`、`src/ui` 为准。

## 模块状态说明

- `src/ui/simple_inventory_panel.py`：当前演示使用的小型背包/进度面板。
- `src/ui/inventory_panel.py`：预留的完整背包 UI 占位，不参与当前主线。
- `src/scenes/ending_scene.py`：预留场景壳。
- `src/ui/ending_panel.py`：当前 Ending 结算面板。
- `src/systems/main_quest_manager.py`：当前三关卡主线状态管理。
- `src/systems/task_manager.py`：早期轻量任务状态，仍被影纹追逐相关旧逻辑引用，暂保留。
- `src/minigames/repair_minigame.py`、`src/scenes/repair_scene.py`：工坊修复小游戏预留模块，当前课程演示主线不依赖。

## AI 协作开发说明

本项目采用 AI 辅助开发，但不是一次性生成。开发过程按需求拆解、模块实现、运行验收、局部修复推进。AI 主要辅助代码生成和问题排查，项目主题、功能取舍、模块拆分、验收判断由开发者完成。

### AI 辅助开发过程

1. 前期由开发者确定主题、需求和关卡结构。
2. AI 提供初始框架和模块实现建议。
3. 开发者根据课程要求提出修改意见，例如模块化、Tiled 对象层、三关卡顺序、战斗特效、背包小型化、节庆真实入口。
4. 每次 AI 修改后，开发者本地运行、截图、查看日志并验收。
5. 最终形成“需求拆解 -> AI 辅助实现 -> 人工验收修正”的开发流程。

## 当前状态

当前版本已跑通主菜单、Tiled 地图加载、玩家移动与碰撞、NPC 对话、集市收集、河谷影纹净化、节庆广场守护、背包状态面板和 Ending 结尾评价。完整工坊修复小游戏、完整图鉴、更多语音和存档系统属于后续扩展。
