# Codex 任务文件拆分包使用说明

## 文件结构

```text
CODEX_TASKS.md
tasks/
├── task_00_read_docs.md
├── task_01_base_project.md
├── task_02_tiled_map_camera.md
├── task_03_player_collision.md
└── task_04_object_layers.md
```

## 使用方式

1. 将 `CODEX_TASKS.md` 放到项目根目录，作为总任务路线。
2. 将 `tasks/` 文件夹放到项目根目录。
3. 每次只复制一个 `tasks/task_xx_xxx.md` 的内容给 Codex。
4. 严格按照 Task 00 → Task 01 → Task 02 → Task 03 → Task 04 的顺序推进。
5. 每次任务完成后，先运行测试，再进入下一个任务。
