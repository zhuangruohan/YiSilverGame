# CODEX_TASKS.md

## 使用方法

本文件是《银纹秘境：彝饰守护者》的 Codex 总任务路线。  
具体任务细节请查看 `tasks/` 目录中的单任务文件。

## 基本原则

1. 严格按任务编号顺序推进，不要跳步。
2. 每次只执行一个 Task。
3. 每次执行前先阅读：
   - `AGENTS.md`
   - `PROJECT_CONTEXT.md`
   - `DEVELOPMENT_RULES.md`
   - `ACCEPTANCE_CHECKLIST.md`
   - 当前 Task 文件
4. 不允许一次性重写整个项目。
5. 不允许擅自加入战斗、怪物 AI、联网、数据库、账号系统、复杂 Web 依赖。
6. 缺少正式素材时使用占位图形或占位文字，不阻塞功能开发。
7. 每次完成后必须说明：
   - 修改了哪些文件；
   - 新增了哪些类和函数；
   - 如何运行；
   - 如何测试；
   - 已知未完成点；
   - 是否影响上一阶段功能。

## 任务路线

| 阶段 | 文件 | 目标 |
|---|---|---|
| Task 00 | `tasks/task_00_read_docs.md` | 阅读项目文档，输出理解与开发计划，不写代码 |
| Task 01 | `tasks/task_01_base_project.md` | 创建基础工程、主循环、主菜单占位 |
| Task 02 | `tasks/task_02_tiled_map_camera.md` | 读取 Tiled 地图，实现摄像机跟随 |
| Task 03 | `tasks/task_03_player_collision.md` | 实现玩家移动、碰撞、地图边界限制 |
| Task 04 | `tasks/task_04_object_layers.md` | 读取 Tiled 对象层，生成基础对象 |
| Task 05 | 后续细化 | NPC 与对话 |
| Task 06 | 后续细化 | 物品与背包 |
| Task 07 | 后续细化 | 任务系统 |
| Task 08 | 后续细化 | 纹样寻源 source_hunt |
| Task 09 | 后续细化 | 纹样寻源 path_maze |
| Task 10 | 后续细化 | 工坊修复与敲银 |
| Task 11 | 后续细化 | 图鉴、套装进度与结局 |

## 当前优先级

当前优先完成 Task 00 - Task 04。

原因：

1. 先让 Codex 对齐项目文档，避免跑偏。
2. 先建立可运行工程，保证后续功能有基础。
3. 先跑通 Tiled + PyTMX + Pygame 的地图链路。
4. 先完成玩家移动、碰撞和对象层读取，再继续做 NPC、背包、任务和纹样系统。

## 推荐执行方式

每次复制一个单独 Task 文件的内容给 Codex。  
不要一次把所有 Task 都交给 Codex。
