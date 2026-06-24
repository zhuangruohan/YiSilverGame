# Task 02：Tiled 地图加载与摄像机

## 目标

实现基础地图系统，能读取 `maps/village.tmx`，绘制 Tiled 地图，并让摄像机跟随占位玩家。

本任务只做地图加载和摄像机。  
不要实现完整玩家移动碰撞、NPC 对话、物品拾取、任务系统。

## 前置条件

已经完成 Task 01。

项目中建议准备：

- `maps/village.tmx`

如果 `maps/village.tmx` 暂时不存在，不要让程序崩溃。  
可以显示占位提示：

```text
未找到 maps/village.tmx，请先使用 Tiled 创建测试地图。
```

## 允许修改或创建的文件

允许创建：

- `src/scene.py`
- `src/tilemap.py`
- `src/camera.py`
- `src/player.py`

允许修改：

- `requirements.txt`
- `settings.py`
- `src/game.py`

不允许创建大量无关模块。

## 给 Codex 的提示词

请根据当前项目文档，实现 Task 02：Tiled 地图加载与摄像机。

本任务只实现地图加载与摄像机，不要实现 NPC 对话、物品拾取、背包、任务系统、纹样寻源、工坊修复、图鉴和结局。

请严格遵守：

1. 在 `requirements.txt` 中加入：
   - `pygame`
   - `pytmx`
2. 创建 `TileMap` 类，负责：
   - 加载 TMX 文件；
   - 读取地图宽高；
   - 读取瓦片大小；
   - 绘制可见图层。
3. 支持绘制以下 Tile Layer：
   - `background`
   - `ground`
   - `decoration`
   - `foreground`
4. 如果某些图层不存在，不要崩溃，输出调试提示即可。
5. 创建 `Camera` 类，负责：
   - 记录摄像机偏移；
   - 跟随玩家；
   - 限制摄像机不越过地图边界；
   - 提供世界坐标到屏幕坐标的转换方法。
6. 创建基础 `Scene` 类，负责：
   - 加载地图；
   - 持有玩家占位对象；
   - 更新摄像机；
   - 绘制地图和玩家。
7. 玩家此阶段可以先使用 32x32 纯色矩形表示。
8. 视窗固定为 800x600。
9. 瓦片大小按 TMX 文件读取，默认要求为 32x32。
10. 摄像机边界计算规则：
    - `0 <= camera_x <= map_width - SCREEN_WIDTH`
    - `0 <= camera_y <= map_height - SCREEN_HEIGHT`
11. 如果地图尺寸小于视窗，摄像机偏移保持为 0，不要报错。
12. 保留 Task 01 的主菜单和退出功能。
13. 按 Enter 进入 PLAYING 后显示地图。
14. 如果地图不存在，进入 PLAYING 后显示缺少地图的提示文字。

完成后请说明：

1. 修改了哪些文件；
2. 每个文件做了什么；
3. 新增了哪些类和函数；
4. 如何运行；
5. 如何测试；
6. 已知未完成点；
7. 是否影响上一阶段功能。

## 推荐类职责

### `TileMap`

负责：

- 加载 `maps/village.tmx`；
- 保存地图宽度、高度、瓦片宽度、瓦片高度；
- 绘制地图图层；
- 后续为 Task 03/04 提供碰撞层和对象层读取接口。

### `Camera`

负责：

- 根据玩家世界坐标更新摄像机位置；
- 防止摄像机越界；
- 提供 `apply_rect()` 或类似方法，将世界坐标转换为屏幕坐标。

### `Scene`

负责：

- 管理当前地图；
- 管理占位玩家；
- 调用 `TileMap.draw()`；
- 调用 `Camera.update()`。

## 禁止

- 不要实现 NPC 交互。
- 不要实现物品拾取。
- 不要实现背包。
- 不要实现任务系统。
- 不要实现完整场景切换。
- 不要实现纹样寻源。
- 不要实现工坊修复。
- 不要一次性读取所有地图。
- 不要硬编码大量地图对象坐标。

## 运行方式

```bash
pip install -r requirements.txt
python main.py
```

## 测试方法

请自测并说明：

1. 没有 `maps/village.tmx` 时，程序是否不崩溃；
2. 存在 `maps/village.tmx` 时，地图是否能显示；
3. 摄像机是否会根据占位玩家位置更新；
4. 摄像机是否不会显示地图外黑边；
5. 主菜单、开始、退出功能是否仍然正常。

## 完成标准

- Tiled 地图能加载；
- 视窗为 800x600；
- 地图大于视窗时摄像机能跟随；
- 摄像机不会越界；
- 缺少地图时程序不崩溃；
- 不破坏 Task 01 功能。

## 建议提交信息

```bash
git add .
git commit -m "feat(map): load tiled map and add camera"
```

## 通过后下一步

完成并测试通过后，再执行：

```text
tasks/task_03_player_collision.md
```
