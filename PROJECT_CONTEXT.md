# PROJECT_CONTEXT.md

## 项目名称
《银纹秘境：彝饰守护者》

## 项目定位
这是一个基于 **Python + Pygame + Tiled + PyTMX + JSON** 的 2D 单人离线文化修复探索游戏 Demo。

## 核心目标
玩家扮演“银纹守护者”，在村寨、山地、工坊、集市、节庆广场与纹样空间中探索，完成：
1. 与 NPC 对话获取线索；
2. 拾取银饰碎片与修复材料；
3. 进行“纹样寻源”小关卡，获得纹样拓片；
4. 在工坊完成敲银修复；
5. 修复节庆银饰套装并获得结局评价。

## 核心机制
### 1. 纹样寻源系统
不是简单“按 E 获得拓片”，而是根据纹样来源设计不同的小关卡：
- `source_hunt`：自然场景寻源（找水、找山、找火等）
- `path_maze`：走纹样迷宫（玩家沿纹样形状路径行走）
- `align_rubbing`：纹样对齐（可选优秀扩展）
- `point_trace`：关键点描摹（可选优秀扩展）

### 2. 敲银修复系统
玩家在工坊中消耗/使用拓片与材料，通过时机判定小游戏修复银饰部件。

### 3. 套装进度与银光值
游戏目标不再是修一件银饰，而是修复一套节庆银饰（如银耳环、银手镯、银项圈、银铃/银链），并根据完成度、图鉴、支线、敲银表现获得评价。

## 场景结构
主场景：
- village（村寨入口）
- workshop（银饰工坊）
- market（山地集市）
- mountain（山地自然场景）
- festival（节庆广场）

纹样空间（可选分场景）：
- pattern_sun
- pattern_mountain
- pattern_water
- pattern_flower

## 技术约束
1. 必须使用 Pygame。
2. 地图建议用 Tiled 制作，瓦片 32x32，视窗 800x600。
3. 代码必须模块化，不允许所有逻辑写在 `main.py`。
4. 对象尽量从 Tiled 对象层与 JSON 读取，避免硬编码。
5. 优先完成 P0/P1 核心流程，再做优秀扩展。

## 推荐目录结构
```text
project/
├── README.md
├── AGENTS.md
├── PROJECT_CONTEXT.md
├── DEVELOPMENT_RULES.md
├── CODEX_TASKS.md
├── ACCEPTANCE_CHECKLIST.md
├── requirements.txt
├── main.py
├── settings.py
├── codex_tasks_split/
│   ├── CODEX_TASKS.md
│   ├──  README_使用说明.md
│   └──tasks/
│   ├── task_00_read_docs.md
│   ├── task_01_base_project.md
│   ├── task_02_tiled_map_camera.md
│   ├── task_03_player_collision.md
│   ├── task_04_object_layers.md
│   ├── task_05_npc_dialogue.md
│   ├── task_06_items_inventory.md
│   ├── task_07_task_system.md
│   ├── task_08_source_hunt.md
│   ├── task_09_path_maze.md
│   ├── task_10_repair_minigame.md
│   └── task_11_codex_progress_ending.md
├── assets/
│   ├── images/
│   ├── sounds/
│   └── music/
├── maps/
│   ├── village.tmx
│   ├── workshop.tmx
│   ├── market.tmx
│   ├── mountain.tmx
│   ├── festival.tmx
│   ├── pattern_sun.tmx
│   ├── pattern_mountain.tmx
│   └── pattern_water.tmx
├── data/
│   ├── npcs.json
│   ├── items.json
│   ├── tasks.json
│   ├── dialogues.json
│   ├── codex.json
│   ├── patterns.json
│   ├── silver_parts.json
│   └── endings.json
└── src/
    ├── game.py
    ├── scene.py
    ├── tilemap.py
    ├── camera.py
    ├── player.py
    ├── npc.py
    ├── item.py
    ├── interactable.py
    ├── inventory.py
    ├── task_manager.py
    ├── codex.py
    ├── pattern_source.py
    ├── pattern_realm.py
    ├── repair_minigame.py
    ├── score_manager.py
    ├── dialogue.py
    └── ui.py
```

## 开发优先级
### P0
- 主菜单
- 地图加载
- 玩家移动与碰撞
- NPC 对话
- 任务系统
- 物品与背包
- 至少 1 个纹样寻源关卡
- 至少 1 次工坊修复
- 基础结局

### P1
- 多场景切换
- 至少 2 种纹样寻源玩法
- 至少 2 个银饰部件修复
- 图鉴系统
- 银光值 / 套装进度
- 节庆展示

### P2
- 纹样对齐 / 关键点描摹
- 支线任务
- 多结局
- 本地存档
- 更完整音效/动画/反馈

## 文化表达原则
- 不猎奇化、不滥编复杂民俗细节。
- 对缺乏确定来源的纹样寓意，使用“游戏化转译”表达。
- 用“自然意象 → 纹样关卡 → 修复反馈”的方式把文化内容做成玩法。
