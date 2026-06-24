# DEVELOPMENT_RULES.md

## 1. 总体开发原则

1. 先跑通主流程，再做优化和扩展。
2. 先实现 P0，再做 P1/P2。
3. 一次只实现一个明确功能模块，不要大包大揽。
4. 每次改动后都要保证项目仍然可以运行。
5. 缺少素材时允许使用占位图，不阻塞主流程开发。
6. 当前阶段不追求完整美术，优先保证可运行、可测试、可展示。
7. 任何新功能必须能解释它服务于主流程中的哪一步。

---

## 2. Python / Pygame 代码规范

### 2.1 命名规范

- 文件名：小写 + 下划线，如 `task_manager.py`
- 类名：大驼峰，如 `TaskManager`
- 函数名：小写 + 下划线，如 `load_scene()`
- 常量：全大写，如 `SCREEN_WIDTH`
- JSON key：统一小写下划线，如 `target_scene`

### 2.2 结构规范

- `main.py`：只负责程序入口。
- `Game` 类：负责主循环、状态切换、资源初始化。
- `Scene` 类：负责场景对象容器、地图加载、对象管理与场景切换。
- `TileMap` 类：负责 Tiled / TMX 地图读取与绘制。
- `Camera` 类：负责摄像机跟随和坐标转换。
- `Player` 类：负责玩家移动、碰撞和交互判断。
- 业务逻辑分散到各模块，不允许全部堆在一个文件里。

### 2.3 主循环规范

主循环应分为：

1. `handle_events()`
2. `update()`
3. `draw()`

不要把事件处理、逻辑更新、绘制代码混写。

推荐结构：

```python
while self.running:
    self.handle_events()
    self.update()
    self.draw()
```

## 3. 游戏状态规范

至少包含：

- `MENU`
- `INTRO`（可选）
- `PLAYING`
- `DIALOGUE`
- `INVENTORY`
- `CODEX`
- `PATTERN_REALM`
- `REPAIR_MINIGAME`
- `ENDING`

规则：

1. 非 `PLAYING` 状态下，玩家不能自由移动。
2. `DIALOGUE` 状态下，只处理对话输入。
3. `INVENTORY` 状态下，只处理背包输入。
4. `CODEX` 状态下，只处理图鉴输入。
5. `PATTERN_REALM` 状态下，运行纹样空间逻辑。
6. `REPAIR_MINIGAME` 状态下，运行敲银修复逻辑。
7. `ENDING` 状态下，显示结局评价。

------

## 4. 地图开发规范

### 4.1 Tiled 基础规则

- 视窗：800x600
- 瓦片：32x32
- 地图尺寸尽量是 32 的整数倍
- 地图大于视窗
- 地图文件保存到 `maps/` 目录
- tileset 素材保存到 `assets/tilesets/` 目录
- 不要使用本机绝对路径引用素材

推荐地图尺寸：

```
village.tmx           120 x 80 tiles
workshop.tmx           40 x 30 tiles
market.tmx             80 x 60 tiles
mountain.tmx           80 x 60 tiles
festival.tmx           60 x 40 tiles
pattern_mountain.tmx   40 x 30 tiles
```

测试阶段可以先用较小地图，例如：

```
village.tmx            60 x 40 tiles
```

### 4.2 图层命名规范

统一使用：

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

不要使用：

- `图层1`
- `对象层1`
- `碰撞区域`
- `NPC点`
- `新建图层`

原因：

1. 程序读取依赖图层名。
2. Codex 生成代码时会根据英文图层名读取对象。
3. 中文或随意命名容易导致 PyTMX 读取失败或找不到图层。

### 4.3 对象层规范

所有对象必须至少有：

- `id`
- `type`

常见对象类型：

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

### 4.4 坐标规范

- 所有交互、碰撞、任务判断使用世界坐标。
- 绘制时再转换为屏幕坐标。
- 不要把屏幕坐标当成地图坐标存储。
- Tiled 对象层中的 `x`、`y` 坐标视为世界坐标。

### 4.5 碰撞规范

1. 碰撞层统一命名为 `collision`。
2. 碰撞层使用 Object Layer。
3. 碰撞对象建议使用矩形对象。
4. 碰撞对象的 `type` 建议设置为 `collision`。
5. 玩家移动时先预测位置，再判断碰撞。
6. 玩家不能穿墙，不能走出地图边界。

------

## 5. JSON 数据规范

尽量把可配置内容放到 JSON：

- NPC
- 对话
- 任务
- 物品
- 图鉴
- 纹样配置
- 银饰部件
- 结局评价

推荐文件：

```
data/
├── npcs.json
├── items.json
├── tasks.json
├── dialogues.json
├── codex.json
├── patterns.json
├── silver_parts.json
└── endings.json
```

原则：

1. 新增条目尽量只改 JSON，不改主逻辑。
2. JSON key 使用小写下划线。
3. 缺少 JSON 文件时程序不应直接崩溃，应给出提示或创建最小可用数据。
4. 重要数据缺失时应输出调试信息。

------

## 6. 资源规范

### 6.1 命名规范

使用：

```
场景_对象_编号
```

或：

```
类别_名称_编号
```

示例：

- `village_house_01.png`
- `player_walk_down_01.png`
- `pattern_sun_icon.png`
- `ui_inventory_bg.png`
- `silver_bracelet_icon.png`

### 6.2 占位规则

如果正式资源尚未准备：

- 角色可以先用纯色矩形或简化 sprite
- NPC 可以先用不同颜色矩形
- 物品可以先用单色图标
- 银饰部件可以先用轮廓图
- 纹样可以先用简化几何符号
- UI 可以先用 pygame 绘制矩形和文字

不要因为素材缺失中断开发。

------

## 7. AI / Codex 协作规范

### 7.0 任务文件优先级

Codex 执行开发任务时，文档优先级如下：

1. 当前任务文件，例如 `tasks/task_02_tiled_map_camera.md`
2. `AGENTS.md`
3. `PROJECT_CONTEXT.md`
4. `DEVELOPMENT_RULES.md`
5. `ACCEPTANCE_CHECKLIST.md`
6. `CODEX_TASKS.md`
7. 其他设计文档和说明文档

如果当前任务文件已经明确禁止某些功能，Codex 不得提前实现。

### 7.1 单次任务限制

每次只让 Codex 做一个模块，例如：

- 只做文档理解
- 只做基础工程
- 只做地图加载
- 只做玩家移动与碰撞
- 只做对象层读取
- 只做 NPC 对话
- 只做物品与背包
- 只做一个纹样寻源玩法

每次只复制一个 `tasks/task_xx_xxx.md` 文件内容给 Codex。

Codex 只能完成当前任务文件中允许的内容。

当前任务没有要求的功能，即使后续会用到，也不要提前实现。

如果必须修改当前任务未列出的文件，必须先说明原因。

### 7.2 输出要求

每次让 Codex 完成任务时，必须要求它说明：

1. 修改了哪些文件；
2. 每个文件改了什么；
3. 新增了哪些类/函数；
4. 如何运行；
5. 如何测试；
6. 已知限制或未完成点；
7. 是否影响上一阶段功能；
8. 下一步建议执行哪个任务。

### 7.3 不允许的行为

- 不要跳过 `tasks/task_00_read_docs.md`。
- 不要一次性执行多个 Task。
- 不要让 Codex 一次性重写整个项目。
- 不要让 Codex 在未说明前提下擅自增加战斗、联网、数据库等无关系统。
- 不要在没有确认目录结构的前提下随意创建大量无用文件。
- 不要把 Task 05 之后的功能提前塞进 Task 01-04。
- 不要在基础流程未跑通前实现复杂动画、完整存档、多结局或大量美术替换。
- 不要因为缺少正式素材而中断开发，应使用占位图形或文字。

------

## 8. 提交与版本规范

如果使用 Git，推荐提交格式：

- `feat(core): 创建 pygame 基础工程`
- `feat(map): 实现 tiled 地图加载与摄像机跟随`
- `feat(player): 添加角色移动与碰撞检测`
- `feat(map): 读取 tiled 对象层`
- `feat(dialogue): 添加 NPC 对话系统`
- `feat(inventory): 添加物品拾取与背包`
- `feat(task): 添加基础任务系统`
- `feat(pattern): 实现 source_hunt 纹样寻源`
- `feat(pattern): 实现山纹 path_maze 小关卡`
- `feat(repair): 添加工坊修复小游戏`
- `feat(codex): 添加图鉴与结局评价`
- `fix(task): 修复任务推进卡死问题`
- `docs(readme): 更新运行说明`

------

## 9. 测试规范

每完成一个阶段，至少自测：

1. 程序能启动；
2. 不报错；
3. 本阶段功能能触发；
4. 不破坏上一阶段功能；
5. 关键提示能显示；
6. 控制台调试信息合理；
7. 缺少素材或部分地图对象时不至于崩溃。

每个 Task 完成后都要根据对应任务文件中的测试方法逐项检查。

------

## 10. 验收前禁止事项

在基础流程未跑通前，不优先做：

- 复杂剧情视频
- 大量特效
- 多分支系统
- 本地存档
- 全量美术替换
- 大量 NPC 扩展
- 多结局复杂分支
- 高难度小游戏

先跑通：

```
开始 → 探索 → 纹样寻源 → 修复 → 结局
```

当前阶段优先跑通：

```
Task 00 → Task 01 → Task 02 → Task 03 → Task 04
```

