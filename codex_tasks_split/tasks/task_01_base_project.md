# Task 01：基础工程与主循环

## 目标

创建可运行的 Pygame 基础工程，让项目能启动、显示主菜单、开始游戏、退出游戏。

本任务只做基础工程。  
不要实现地图、NPC、背包、任务、纹样寻源、工坊修复、图鉴和结局。

## 前置条件

已经完成 Task 00，确认 Codex 对项目理解正确。

## 允许修改或创建的文件

允许创建：

- `requirements.txt`
- `main.py`
- `settings.py`
- `src/__init__.py`
- `src/game.py`

可选创建：

- `src/ui.py`

不允许创建大量无关模块。

## 给 Codex 的提示词

请根据当前项目文档，为《银纹秘境：彝饰守护者》实现 Task 01：基础工程与主循环。

本任务只实现基础工程，不要实现地图加载、玩家移动、NPC、背包、任务、纹样寻源、工坊修复、图鉴和结局。

请严格遵守：

1. 使用 Python 3 + Pygame。
2. 创建 800x600 游戏窗口。
3. 窗口标题为：`银纹秘境：彝饰守护者`。
4. `main.py` 只作为程序入口。
5. `settings.py` 保存基础常量：
   - `SCREEN_WIDTH = 800`
   - `SCREEN_HEIGHT = 600`
   - `FPS = 60`
   - `TITLE = "银纹秘境：彝饰守护者"`
6. `src/game.py` 中创建 `Game` 类。
7. `Game` 类至少包含：
   - `__init__()`
   - `run()`
   - `handle_events()`
   - `update()`
   - `draw()`
   - `quit()`
8. 主循环必须拆分为：
   - `handle_events()`
   - `update()`
   - `draw()`
9. 初始状态为 `MENU`。
10. 主菜单显示：
    - 游戏标题；
    - `按 Enter 开始游戏`；
    - `按 Esc 退出游戏`。
11. 按 Enter 后进入 `PLAYING` 占位状态。
12. `PLAYING` 占位状态显示：
    - `游戏场景占位，后续将加载 Tiled 地图`。
13. 按 Esc 可以退出。
14. 使用 pygame 默认字体即可。
15. 关键代码写简单中文注释。
16. 项目必须能通过 `python main.py` 启动。

完成后请说明：

1. 修改了哪些文件；
2. 每个文件做了什么；
3. 新增了哪些类和函数；
4. 如何运行；
5. 如何测试；
6. 已知未完成点；
7. 是否影响上一阶段功能。

## 禁止

- 不要实现地图加载。
- 不要实现玩家移动。
- 不要实现 NPC。
- 不要实现背包。
- 不要实现任务系统。
- 不要实现纹样寻源。
- 不要实现工坊修复。
- 不要实现图鉴和结局。
- 不要引入复杂框架。
- 不要把所有逻辑写进 `main.py`。

## 运行方式

```bash
pip install -r requirements.txt
python main.py
```

## 测试方法

请自测并说明结果：

1. 运行 `python main.py` 是否能启动窗口；
2. 主菜单是否显示；
3. 按 Enter 是否进入 PLAYING 占位界面；
4. 按 Esc 是否能退出；
5. 程序关闭时是否无报错。

## 完成标准

- 项目能启动；
- 主菜单可显示；
- 可以开始游戏；
- 可以正常退出；
- 代码结构清晰；
- `main.py` 没有堆大量逻辑；
- 没有提前实现后续复杂功能。

## 建议提交信息

```bash
git add .
git commit -m "feat(core): create pygame base project"
```

## 通过后下一步

完成并测试通过后，再执行：

```text
tasks/task_02_tiled_map_camera.md
```
