# Task 04：Tiled 对象层读取

## 目标

从 Tiled 对象层读取 NPC、Item、Trigger、Pattern Source、Clue、Checkpoint 等对象数据，为后续交互系统做准备。

本任务只读取和生成基础对象。  
不要实现完整对话、背包、任务推进、场景切换和小游戏。

## 前置条件

已经完成 Task 03。

`maps/village.tmx` 中建议至少包含：

- `trigger_points`
- `npc_points`
- `object_points`
- `pattern_points`
- `clue_points`
- `checkpoint_points`

如果部分图层不存在，不要崩溃，输出调试提示。

## 允许修改或创建的文件

允许创建：

- `src/interactable.py`
- `src/npc.py`
- `src/item.py`
- `src/pattern_source.py`

允许修改：

- `src/tilemap.py`
- `src/scene.py`
- `src/game.py`

不允许创建大量无关模块。

## 给 Codex 的提示词

请根据当前项目文档，实现 Task 04：Tiled 对象层读取。

本任务只读取 Tiled 对象层并生成基础对象。  
不要实现 NPC 对话框、物品进入背包、任务系统、场景切换、纹样小游戏、工坊修复、图鉴和结局。

请严格遵守：

1. 从 `trigger_points` 读取：
   - `spawn`
   - `scene_exit`
   - `return_point`
   - `task_trigger`
2. 从 `npc_points` 读取：
   - `npc`
3. 从 `object_points` 读取：
   - `item`
   - `repair_table`
   - `display_table`
   - `silver_part_display`
   - `hidden_collectible`
4. 从 `pattern_points` 读取：
   - `pattern_source`
5. 从 `clue_points` 读取：
   - `clue`
6. 从 `checkpoint_points` 读取：
   - `pattern_checkpoint`
7. 每个对象必须读取：
   - `id`
   - `type`
   - `x`
   - `y`
   - `width`
   - `height`
   - `properties`
8. 如果对象缺少 `id` 或 `type`，输出警告，但不要让程序崩溃。
9. 根据 `type` 创建基础对象实例。
10. 暂时可以用简单矩形或文字标记显示 NPC、Item、Trigger。
11. 输出调试信息，例如：
    - 加载 NPC 数量；
    - 加载 Item 数量；
    - 加载 Trigger 数量；
    - 加载 Pattern Source 数量；
    - 加载 Clue 数量；
    - 加载 Checkpoint 数量。
12. 不要硬编码对象坐标。
13. 所有对象位置使用 Tiled 世界坐标。
14. 绘制时通过 Camera 转换为屏幕坐标。
15. 保留 Task 01 的菜单和退出功能。
16. 保留 Task 02 的地图加载与摄像机功能。
17. 保留 Task 03 的玩家移动与碰撞功能。

完成后请说明：

1. 修改了哪些文件；
2. 每个文件做了什么；
3. 新增了哪些类和函数；
4. 如何运行；
5. 如何测试；
6. 已知未完成点；
7. 是否影响上一阶段功能。

## 推荐基础对象结构

可以先建立一个通用 `Interactable` 类：

```text
Interactable
├── id
├── type
├── name
├── rect
├── properties
├── draw()
```

然后让以下对象继承或复用：

```text
NPC
Item
PatternSourcePoint
CluePoint
Trigger
```

当前阶段不要求实现完整交互逻辑，只要能读取、保存、显示和调试。

## 对象层读取要求

### `trigger_points`

支持：

```text
spawn
scene_exit
return_point
task_trigger
```

### `npc_points`

支持：

```text
npc
```

### `object_points`

支持：

```text
item
repair_table
display_table
silver_part_display
hidden_collectible
```

### `pattern_points`

支持：

```text
pattern_source
```

### `clue_points`

支持：

```text
clue
```

### `checkpoint_points`

支持：

```text
pattern_checkpoint
```

## 禁止

- 不要实现 NPC 对话框。
- 不要实现物品进入背包。
- 不要实现任务系统。
- 不要实现场景切换逻辑。
- 不要实现纹样寻源小游戏。
- 不要实现工坊修复。
- 不要实现图鉴和结局。
- 不要因为某一类对象缺失就崩溃。
- 不要硬编码 NPC、物品、纹样点、线索点、检查点坐标。

## 运行方式

```bash
pip install -r requirements.txt
python main.py
```

## 测试方法

请自测并说明：

1. 控制台是否输出各类对象加载数量；
2. `npc_points` 中的 NPC 是否被读取；
3. `object_points` 中的 item 是否被读取；
4. `trigger_points` 中的 spawn 和 scene_exit 是否被读取；
5. `pattern_points` 中的 pattern_source 是否被读取；
6. `clue_points` 中的 clue 是否被读取；
7. `checkpoint_points` 中的 pattern_checkpoint 是否被读取；
8. 缺少某个对象层时程序是否不崩溃；
9. 对象是否显示在正确位置；
10. 玩家移动和碰撞是否仍然正常；
11. 主菜单和退出功能是否仍然正常。

## 完成标准

- NPC 能按对象层读取；
- Item 能按对象层读取；
- Trigger 能按对象层读取；
- Repair Table 能按对象层读取；
- Display Table 能按对象层读取；
- Pattern Source / Clue / Checkpoint 能按对象层读取；
- 对象坐标不硬编码；
- 对象属性缺失时有调试提示；
- 不破坏前面任务功能。

## 建议提交信息

```bash
git add .
git commit -m "feat(map): read tiled object layers"
```

## 通过后下一步

完成并测试通过后，再继续细化：

```text
Task 05：NPC 与对话
```
