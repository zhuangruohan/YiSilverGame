# Legacy

旧实现如果后续需要整体保留，可以放入本目录。

当前整改没有删除旧入口文件，而是把 `src/game.py`、`src/scene.py`、`src/tilemap.py`、
`src/camera.py`、`src/player.py`、`src/npc.py` 改为兼容包装，主流程不从 `legacy` 导入。
