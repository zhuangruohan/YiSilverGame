#  README.md 

《银纹秘境：彝饰守护者》一个基于 **Python + Pygame + Tiled + PyTMX + JSON** 的 2D 单人离线文化修复探索游戏 Demo。

---

## 1. 项目简介

玩家扮演“银纹守护者”，在村寨、山地、集市、工坊和节庆广场中探索，通过 **纹样寻源** 获得拓片，再在工坊中进行 **敲银修复**，逐步修复节庆银饰套装，并获得结局评价。

本项目不是战斗 RPG，而是一个以“探索、观察、收集、拓片、修复、展示”为核心的文化修复探索游戏。

---

## 2. 核心玩法

- 地图探索
- NPC 对话与任务推进
- 物品拾取与背包
- 纹样寻源
  - `source_hunt`：自然场景寻源
  - `path_maze`：走纹样迷宫
- 工坊敲银修复
- 图鉴解锁
- 套装进度与银光值
- 节庆展示与结局评价

---

## 3. 技术栈

- Python 3.x
- Pygame
- Tiled Map Editor
- PyTMX
- JSON

## 4.项目结构

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
├── tasks/
│   ├── task_00_read_docs.md
│   ├── task_01_base_project.md
│   ├── task_02_tiled_map_camera.md
│   ├── task_03_player_collision.md
│   ├── task_04_object_layers.md
│   └── ...
├── assets/
│   ├── images/
│   ├── tilesets/
│   ├── sounds/
│   └── music/
├── maps/
│   ├── village.tmx
│   ├── workshop.tmx
│   ├── market.tmx
│   ├── mountain.tmx
│   ├── festival.tmx
│   └── pattern_mountain.tmx
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
    ├── dialogue.py
    ├── pattern_source.py
    ├── pattern_realm.py
    ├── repair_minigame.py
    ├── codex.py
    ├── score_manager.py
    └── ui.py
```

## 5. 快速开始

### 5.1 安装依赖

如果项目中已经有 `requirements.txt`：

```
pip install -r requirements.txt
```

如果暂时还没有生成 `requirements.txt`，可以临时执行：

```
pip install pygame pytmx
```

### 5.2 运行项目

```
python main.py
```

------

## 6. 开发顺序建议

严格按照 `tasks/` 目录中的任务文件顺序推进：

1. `task_00_read_docs.md`：文档理解与开发计划确认
2. `task_01_base_project.md`：基础工程与主循环
3. `task_02_tiled_map_camera.md`：Tiled 地图加载与摄像机
4. `task_03_player_collision.md`：玩家移动与碰撞
5. `task_04_object_layers.md`：Tiled 对象层读取
6. `task_05_npc_dialogue.md`：NPC 与对话
7. `task_06_items_inventory.md`：物品拾取与背包
8. `task_07_task_system.md`：基础任务系统
9. `task_08_source_hunt.md`：纹样寻源 source_hunt
10. `task_09_path_maze.md`：纹样寻源 path_maze
11. `task_10_repair_minigame.md`：工坊修复与敲银
12. `task_11_codex_progress_ending.md`：图鉴、套装进度与结局

------

## 7. 如何与 Codex 协作

1. 先让 Codex 阅读 `tasks/task_00_read_docs.md`。
2. Task 00 只输出项目理解和开发计划，不写代码。
3. 确认 Codex 理解没有跑偏后，再执行 `tasks/task_01_base_project.md`。
4. 后续严格按照 `tasks/` 目录中的任务文件顺序推进。
5. 每次只复制一个任务文件给 Codex。
6. 每完成一步，先运行测试，再进入下一步。
7. 如果某一步报错，优先修复当前任务，不要跳到后面的系统。
8. Codex 每次完成任务后必须说明：
   - 修改了哪些文件；
   - 每个文件改了什么；
   - 新增了哪些类和函数；
   - 如何运行；
   - 如何测试；
   - 已知未完成点；
   - 是否影响上一阶段功能。

------

## 8. 如何使用 Tiled

### 8.1 基础设置

1. 打开 Tiled，新建地图；
2. 地图方向选择 Orthogonal；
3. 瓦片尺寸设为 `32x32`；
4. 地图尺寸应大于 `800x600` 视窗；
5. 保存为 `.tmx` 文件，放到 `maps/` 目录。

### 8.2 标准图层

创建以下图层：

- `background`
- `ground`
- `decoration`
- `collision`
- `object_points`
- `npc_points`
- `pattern_points`
- `clue_points`
- `checkpoint_points`
- `trigger_points`
- `foreground`

### 8.3 对象属性

NPC 示例：

```
id: elder
type: npc
name: 村寨长者
dialogue_id: elder_dialogue
task_id: main_01
```

出口示例：

```
id: exit_to_workshop
type: scene_exit
target_scene: workshop
target_spawn: workshop_entry
required_task: main_02
locked_message: 先找到银饰碎片，再去工坊。
```

物品示例：

```
id: silver_fragment_01
type: item
name: 银饰碎片
item_type: fragment
task_update: main_02
```

线索点示例：

```
id: water_clue_01
type: clue
name: 河边水流
pattern_id: water_pattern
clue_group: water_source
required_count: 3
reward_item: water_pattern_rubbing
```

纹样入口示例：

```
id: pattern_mountain
type: pattern_source
name: 山纹寻源点
pattern_id: mountain_pattern
challenge_type: path_maze
reward_item: mountain_pattern_rubbing
target_scene: pattern_mountain
return_scene: mountain
return_spawn: mountain_return_from_pattern
```

检查点示例：

```
id: mountain_checkpoint_01
type: pattern_checkpoint
pattern_id: mountain_pattern
order: 1
next_checkpoint: mountain_checkpoint_02
```

------

## 9. 素材建议

### 9.1 必需图片

#### 角色类

- 主角站立 / 行走，上下左右
- 村寨长者
- 银匠师傅
- 集市阿妈
- 节庆主持人
- 小朋友

#### 地图类

- 村寨 tileset
- 工坊 tileset
- 集市 tileset
- 山地自然场景 tileset
- 节庆广场 tileset
- 通用地面、草地、路面、房屋、树木、栅栏、桌台、摊位

#### 对象类

- 银饰碎片
- 银丝材料
- 修复锤
- 银耳环
- 银手镯
- 银项圈
- 银铃 / 银链
- 纹样拓片图标

#### UI 类

- 主菜单背景
- 按钮
- 背包底图
- 图鉴底图
- 对话框底图
- HUD 图标

#### 特效类

- 银光效果
- 发光检查点
- 修复成功闪光
- 纹样路径发光线条

### 9.2 可后补图片

- 前景遮挡树冠
- 更完整的工坊器具
- 节庆灯笼和舞台装饰
- 支线 NPC 头像
- 更细的纹样插画

------

## 10. 用 GPT 生成素材时怎么说

### 角色示例

```
生成一个 2D 手绘风游戏 NPC 立绘，主题为彝族村寨长者，朴素服饰，温和神情，正面站姿，适合 Pygame 文化探索游戏，透明背景。
```

### 地图素材示例

```
生成一个 2D top-down 游戏 tileset，主题为山地彝族村寨，包含土路、木屋、草地、石阶、树木、围栏，手绘风格，适合 Tiled 地图编辑器。
```

### 物品示例

```
生成一组 2D 游戏道具图标，包含银饰碎片、银丝材料、修复锤、山纹拓片、太阳纹拓片，手绘清晰，透明背景。
```

------

## 11. 当前最推荐的开发策略

当前阶段优先完成：

1. Task 00：文档理解
2. Task 01：基础工程
3. Task 02：Tiled 地图加载与摄像机
4. Task 03：玩家移动与碰撞
5. Task 04：Tiled 对象层读取

在 Task 00-04 没有跑通前，不建议开始 NPC、背包、任务、纹样寻源、工坊修复和结局系统。

开发策略：

- 先做占位图 + 跑通逻辑
- 再逐步替换正式素材
- 先做 `source_hunt` 和 `path_maze`
- `align_rubbing` / `point_trace` 放到后面
- 先实现 P0，再做 P1/P2
- 每完成一个任务都要测试，不要连续堆功能

------

## 12. 验收目标

最少要实现：

- 能跑起来
- 有主菜单
- 能加载 Tiled 地图
- 玩家能移动
- 玩家不能穿墙
- 能读取对象层
- 能与 NPC 对话
- 能拾取物品
- 能打开背包
- 能推进任务
- 能获得 1 个拓片
- 能修复 1 个银饰部件
- 能进入结局评价
