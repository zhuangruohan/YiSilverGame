# 银纹秘境：彝饰守护者

《银纹秘境：彝饰守护者》是一个基于 **Python + Pygame + Tiled + PyTMX + JSON** 的 2D 单人离线文化修复探索游戏 Demo。

玩家扮演“银纹守护者”，在村寨、山地、集市、工坊和节庆广场中探索，通过 **纹样寻源** 获得拓片，再在工坊中进行 **敲银修复**，逐步修复节庆银饰套装，并获得结局评价。

本项目不是战斗 RPG，而是一个以 **探索、观察、收集、拓片、修复、展示** 为核心的文化修复探索游戏。

---

## 1. 项目定位

本项目定位为：

* Python + Pygame 2D 游戏项目
* 单人离线文化探索游戏 Demo
* 彝族银饰文化主题互动游戏
* AI / Codex 辅助开发实践项目
* 高标准验收导向的课程项目

核心目标不是堆功能，而是跑通一条完整主流程：

```text
开始游戏
→ 地图探索
→ NPC 对话
→ 拾取物品
→ 纹样寻源
→ 获得拓片
→ 工坊修复
→ 图鉴解锁
→ 节庆展示
→ 结局评价
```

---

## 2. 当前开发状态

当前项目处于 **基础工程阶段**。

已完成：

* 项目文档整理
* Codex 协作规则整理
* Task 00 + Task 01 合并执行
* Pygame 基础工程
* 800x600 游戏窗口
* 主菜单占位界面
* Enter 开始游戏
* Esc 退出游戏
* PLAYING 占位界面
* requirements.txt 依赖文件
* Git / GitHub 仓库初始化

当前下一步：

1. 使用 Tiled 制作 `maps/village.tmx`
2. 提交 Tiled 测试地图
3. 让 Codex 执行 `tasks/task_02_tiled_map_camera.md`
4. 实现 Tiled 地图加载与摄像机跟随

---

## 3. 核心玩法规划

标准版本规划包含以下玩法：

* 地图探索
* NPC 对话与任务推进
* 物品拾取与背包
* 纹样寻源

  * `source_hunt`：自然场景寻源
  * `path_maze`：走纹样迷宫
* 工坊敲银修复
* 图鉴解锁
* 套装进度与银光值
* 节庆展示与结局评价

当前阶段暂不实现完整玩法，先完成基础工程与地图链路。

---

## 4. 技术栈

* Python 3.x
* Pygame
* Tiled Map Editor
* PyTMX
* JSON
* Git / GitHub
* Codex / ChatGPT 辅助开发

---

## 5. 项目结构

当前推荐结构如下：

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
│   └── task_04_object_layers.md
├── assets/
│   ├── images/
│   ├── tilesets/
│   ├── sounds/
│   └── music/
├── maps/
├── data/
└── src/
    ├── __init__.py
    ├── game.py
    └── ...
```

说明：

* 当前已细化任务为 Task 00-04。
* Task 05-11 暂不作为当前可执行任务。
* 后续会在 Task 00-04 跑通后继续细化 NPC、背包、任务、纹样、修复、图鉴和结局系统。
* `maps/` 目录用于保存 Tiled 导出的 `.tmx` 地图。
* `assets/tilesets/` 用于保存 Tiled 使用的 tileset 图片。
* `data/` 用于保存 JSON 配置数据。
* `src/` 用于保存 Pygame 代码模块。

---

## 6. 快速开始

### 6.1 安装依赖

推荐使用虚拟环境。

如果已经创建 `.venv`，在 Windows PowerShell 中可以执行：

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

如果已经激活虚拟环境，也可以执行：

```powershell
pip install -r requirements.txt
```

### 6.2 运行项目

如果未激活虚拟环境，推荐使用：

```powershell
.\.venv\Scripts\python.exe main.py
```

如果已经激活虚拟环境，可以使用：

```powershell
python main.py
```

注意：

如果直接执行 `python main.py` 出现 Microsoft Store 相关提示，说明当前终端没有使用项目虚拟环境。请改用：

```powershell
.\.venv\Scripts\python.exe main.py
```

---

## 7. 当前基础工程验收

当前 Task 00 + Task 01 阶段需要满足：

* [x] 项目能启动
* [x] 创建 800x600 游戏窗口
* [x] 显示主菜单
* [x] 按 Enter 进入 PLAYING 占位界面
* [x] 按 Esc 退出游戏
* [x] `main.py` 只作为程序入口
* [x] `Game` 类负责主循环
* [x] 主循环拆分为 `handle_events()`、`update()`、`draw()`
* [ ] Tiled 地图加载，后续 Task 02 实现
* [ ] 玩家移动与碰撞，后续 Task 03 实现
* [ ] Tiled 对象层读取，后续 Task 04 实现

---

## 8. Codex 协作方式

本项目使用 Codex / ChatGPT 辅助开发，但 AI 不直接自由生成完整项目。

开发原则：

1. 先读文档，再写代码。
2. 每次只执行一个任务。
3. 不跳过任务。
4. 不一次性重写整个项目。
5. 不提前实现后续复杂系统。
6. 缺少素材时使用占位图形或文字。
7. 每次完成后必须运行测试。
8. 每次完成后必须说明修改文件、运行方式、测试方法和已知未完成点。

当前可执行任务：

```text
Task 00：文档理解与开发计划确认
Task 01：基础工程与主循环
Task 02：Tiled 地图加载与摄像机
Task 03：玩家移动与碰撞
Task 04：Tiled 对象层读取
```

目前 Task 00 和 Task 01 已合并执行。
下一步应先制作 `maps/village.tmx`，然后执行 Task 02。

---

## 9. 当前开发路线

### 第一阶段：基础工程

目标：

```text
能启动
有窗口
有主菜单
能进入占位游戏界面
能退出
```

状态：已完成。

### 第二阶段：Tiled 地图链路

目标：

```text
制作 village.tmx
读取 Tiled 地图
绘制地图图层
摄像机跟随
缺少地图时不崩溃
```

状态：下一步。

### 第三阶段：玩家移动与碰撞

目标：

```text
玩家能移动
不能穿墙
不能走出地图边界
摄像机继续跟随
```

状态：待执行。

### 第四阶段：对象层读取

目标：

```text
读取 npc_points
读取 object_points
读取 trigger_points
读取 pattern_points
读取 clue_points
读取 checkpoint_points
输出对象加载数量
```

状态：待执行。

### 后续阶段

待 Task 00-04 跑通后，再继续细化：

```text
NPC 与对话
物品与背包
任务系统
纹样寻源
工坊修复
图鉴与结局
```

---

## 10. Tiled 地图制作规范

### 10.1 基础设置

使用 Tiled 新建地图：

* 地图方向：Orthogonal
* 瓦片尺寸：32x32
* 测试地图推荐尺寸：60 x 40 tiles
* 测试地图像素尺寸：1920 x 1280
* 保存路径：`maps/village.tmx`

### 10.2 标准图层

主地图建议创建以下图层：

```text
background
ground
decoration
collision
object_points
npc_points
pattern_points
clue_points
checkpoint_points
trigger_points
foreground
```

说明：

* `background`：背景层
* `ground`：地面层
* `decoration`：装饰层
* `collision`：碰撞对象层
* `object_points`：物品、修复台、展示台等对象
* `npc_points`：NPC 点位
* `pattern_points`：纹样寻源入口
* `clue_points`：自然线索点
* `checkpoint_points`：纹样空间检查点
* `trigger_points`：出生点、出口、触发区
* `foreground`：前景遮挡层

### 10.3 第一张 village.tmx 最低对象要求

第一张测试地图至少放置：

#### 出生点

对象层：`trigger_points`

```text
id: village_spawn_start
type: spawn
spawn_id: start
```

#### 村寨长者

对象层：`npc_points`

```text
id: elder
type: npc
name: 村寨长者
dialogue_id: elder_dialogue
task_id: main_01
```

#### 第一块银饰碎片

对象层：`object_points`

```text
id: silver_fragment_01
type: item
name: 银饰碎片
item_type: fragment
task_update: main_02
```

#### 工坊出口

对象层：`trigger_points`

```text
id: exit_to_workshop
type: scene_exit
target_scene: workshop
target_spawn: workshop_entry
required_task: main_02
locked_message: 先找到银饰碎片，再去工坊。
```

#### 碰撞区域

对象层：`collision`

```text
id: house_collision_01
type: collision
```

---

## 11. 素材建议

当前阶段不要求完整正式素材。

可以先使用：

* 纯色矩形作为玩家
* 简单 tileset 作为地图
* 简单图标作为物品
* 简单文字作为 UI
* 简化几何图形作为纹样提示

后续再逐步替换为正式素材。

推荐素材目录：

```text
assets/
├── images/
│   ├── characters/
│   ├── items/
│   ├── ui/
│   └── effects/
├── tilesets/
├── sounds/
└── music/
```

---

## 12. 开发提交建议

基础工程提交：

```powershell
git add .
git commit -m "feat(core): create pygame base project"
git push github main
```

修复字体或运行问题：

```powershell
git add .
git commit -m "fix(core): fix pygame font loading"
git push github main
```

添加 Tiled 测试地图：

```powershell
git add maps/ assets/tilesets/
git commit -m "feat(map): add village tiled test map"
git push github main
```

如果需要同步 Gitee：

```powershell
git push gitee main
```

当前建议：

* GitHub 作为主仓库
* Gitee 作为备份仓库

---

## 13. 后续验收目标

最低可运行版本需要实现：

* 能启动游戏
* 有主菜单
* 能加载 Tiled 地图
* 玩家能在地图中移动
* 玩家不能穿墙
* 玩家不能走出地图边界
* 能读取 Tiled 对象层
* 能识别 NPC、Item、Trigger 等基础对象
* 能与 NPC 对话
* 能拾取物品
* 能打开背包
* 能推进基础任务
* 能完成至少 1 个纹样寻源
* 能获得 1 个纹样拓片
* 能完成 1 次工坊修复
* 能进入基础结局评价

---

## 14. 文化表达原则

本项目涉及彝族银饰文化表达，应遵守以下原则：

1. 不猎奇化。
2. 不滥编复杂民俗细节。
3. 不把民族文化奇幻化、神秘化。
4. 不用大段文字堆砌知识。
5. 每个文化知识点尽量绑定一个游戏行为。
6. 对缺少明确出处的纹样寓意，使用“游戏化转译”表达。
7. 推荐使用“本游戏将……抽象为……”等表达方式。
8. 让玩家通过探索、收集、修复和展示自然理解文化内容。

---

## 15. 项目目标总结

本项目最终希望完成一个可运行、可展示、可验收的 2D 文化修复探索游戏 Demo。

短期目标：

```text
基础工程 → Tiled 地图 → 玩家移动 → 对象层读取
```

中期目标：

```text
NPC 对话 → 物品背包 → 任务系统 → 纹样寻源
```

最终目标：

```text
工坊修复 → 图鉴解锁 → 套装进度 → 节庆展示 → 结局评价
```
