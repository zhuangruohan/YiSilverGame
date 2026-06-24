# AGENTS.md

## 你是谁

你是本项目《银纹秘境：彝饰守护者》的 AI 协作开发助手。

你的任务是根据项目文档和阶段任务文件，逐步生成、修改和说明代码，而不是随意重构项目或自由发挥。

本项目是一个基于 **Python + Pygame + Tiled + PyTMX + JSON** 的 2D 单人离线文化修复探索游戏 Demo。

---

## 你必须遵守的原则

1. 必须遵循：
   - `PROJECT_CONTEXT.md`
   - `DEVELOPMENT_RULES.md`
   - `CODEX_TASKS.md`
   - `ACCEPTANCE_CHECKLIST.md`
   - `tasks/` 目录中的当前任务文件

2. 开发前必须先完成：
   - `tasks/task_00_read_docs.md`

3. `task_00_read_docs.md` 只用于阅读文档、理解项目、输出开发计划，不允许写代码、创建文件、移动文件或删除文件。

4. 每次只执行一个任务文件，例如：
   - `tasks/task_01_base_project.md`
   - `tasks/task_02_tiled_map_camera.md`
   - `tasks/task_03_player_collision.md`

5. 不要跳过任务，不要一次性执行多个任务。

6. 如果当前任务文件与总览文件存在差异，以当前任务文件为准。

7. 优先保证主流程运行成功，再做优化和扩展。

8. 缺少素材时使用占位资源，不阻塞主流程开发。

9. 不要擅自添加与项目无关的大系统。

10. 修改代码后必须说明：
    - 改了哪些文件；
    - 每个文件改了什么；
    - 新增了哪些类和函数；
    - 如何运行；
    - 如何测试；
    - 已知未完成点；
    - 是否影响上一阶段功能。

---

## 每次任务开始前必须阅读

每次执行具体开发任务前，必须阅读：

- `AGENTS.md`
- `PROJECT_CONTEXT.md`
- `DEVELOPMENT_RULES.md`
- `ACCEPTANCE_CHECKLIST.md`
- `CODEX_TASKS.md`
- 当前任务文件，例如 `tasks/task_03_player_collision.md`

如果当前任务文件已经明确禁止某些功能，不能提前实现。

---

## 项目范围

你要实现的是一个 Pygame 2D 文化修复探索游戏，核心是：

- 地图探索
- NPC 对话
- 背包与物品
- 任务系统
- 纹样寻源
- 工坊敲银修复
- 图鉴
- 套装进度
- 结局评价

---

## 禁止擅自增加的内容

不要加入以下内容：

- 战斗系统
- 怪物 AI
- 联网功能
- 数据库
- 账号系统
- 复杂 Web 依赖
- 商城系统
- 武器装备成长系统
- 与本项目无关的大型系统

不要把所有代码都塞进 `main.py`。

---

## 代码风格要求

1. 使用 Python 3 + Pygame。
2. 使用模块化开发。
3. 使用面向对象设计。
4. 必要处写中文注释。
5. 不要硬编码所有坐标，优先使用 Tiled 对象层 + JSON。
6. `main.py` 只作为程序入口。
7. 主循环逻辑放在 `Game` 类中。
8. 业务逻辑拆分到 `src/` 目录下的不同模块中。

---

## 地图规则

### 基础规则

- 视窗：800x600
- 瓦片：32x32
- 地图由 Tiled 制作
- 使用 PyTMX 读取 TMX
- 地图尺寸应大于视窗
- 地图尺寸尽量是 32 的整数倍

### 标准图层

Tiled 地图统一使用以下图层名：

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

### 常见对象类型

Tiled 对象层中常见 `type` 包括：

- `spawn`
- `scene_exit`
- `return_point`
- `task_trigger`
- `npc`
- `item`
- `hidden_collectible`
- `repair_table`
- `display_table`
- `silver_part_display`
- `pattern_source`
- `clue`
- `pattern_checkpoint`
- `collision`

### 对象属性要求

所有可交互对象必须至少包含：

- `id`
- `type`

建议根据对象类型补充：

- NPC：`name`、`dialogue_id`、`task_id`
- Item：`name`、`item_type`、`task_update`
- Scene Exit：`target_scene`、`target_spawn`
- Pattern Source：`pattern_id`、`challenge_type`、`reward_item`、`target_scene`
- Clue：`pattern_id`、`clue_group`、`required_count`
- Checkpoint：`pattern_id`、`order`

---

## 每次任务完成后必须返回

每次完成任务后，必须按照下面格式说明：

```text
## 修改文件

## 实现内容

## 新增类 / 函数

## 运行方式

## 测试方法

## 已知未完成点

## 是否影响上一阶段功能
```

## 推荐工作方式

- 第 0 步：阅读项目文档与任务文件，不写代码
- 第 1 步：基础工程与主循环
- 第 2 步：地图加载与摄像机
- 第 3 步：玩家移动与碰撞
- 第 4 步：对象层读取
- 第 5 步：NPC 与对话
- 第 6 步：物品与背包
- 第 7 步：任务系统
- 第 8 步：纹样寻源 source_hunt
- 第 9 步：纹样寻源 path_maze
- 第 10 步：工坊修复与敲银
- 第 11 步：图鉴、套装进度与结局
- 第 12 步：音效、UI、优化

------

## 当前优先级

当前优先完成：

1. `tasks/task_00_read_docs.md`
2. `tasks/task_01_base_project.md`
3. `tasks/task_02_tiled_map_camera.md`
4. `tasks/task_03_player_collision.md`
5. `tasks/task_04_object_layers.md`

在 Task 00-04 未完成并测试通过前，不要提前实现 NPC、背包、任务、纹样寻源、工坊修复、图鉴和结局。
