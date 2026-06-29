from __future__ import annotations

from dataclasses import dataclass

import pygame
from pytmx import TiledObjectGroup


@dataclass
class ObjectRecord:
    """Normalized Tiled object record using world coordinates."""

    id: str
    type: str
    name: str
    layer_name: str
    rect: pygame.Rect
    properties: dict


class ObjectLoader:
    """Parses Tiled object layers into typed records without hardcoded coordinates."""

    LAYER_OBJECT_TYPES = {
        "trigger_points": {
            "spawn",
            "scene_exit",
            "return_point",
            "task_trigger",
            "shadow_fragment_trigger",
        },
        "transition": {
            "spawn",
            "scene_exit",
            "return_point",
            "task_trigger",
            "shadow_fragment_trigger",
        },
        "npc_points": {"npc"},
        "npc": {"npc"},
        "object_points": {
            "item",
            "repair_table",
            "display_table",
            "silver_part_display",
            "hidden_collectible",
            "shadow_fragment_trigger",
            "shadow_spirit_spawn",
            "shadow_route_point",
        },
        "interaction": {
            "item",
            "repair_table",
            "display_table",
            "silver_part_display",
            "hidden_collectible",
            "task_trigger",
            "shadow_fragment_trigger",
            "shadow_spirit_spawn",
            "shadow_route_point",
        },
        "pattern_points": {"pattern_source"},
        "clue_points": {"clue"},
        "checkpoint_points": {"pattern_checkpoint"},
        "collision": {"collision"},
    }

    def __init__(self, tmx_data) -> None:
        self.tmx_data = tmx_data

    def load(self) -> list[ObjectRecord]:
        records: list[ObjectRecord] = []
        if self.tmx_data is None:
            return records

        for layer in self.tmx_data.layers:
            if not isinstance(layer, TiledObjectGroup):
                continue
            layer_name = layer.name.strip().lower()
            supported_types = self.LAYER_OBJECT_TYPES.get(layer_name)
            if supported_types is None:
                print(f"[ObjectLoader] 跳过未注册对象层: {layer.name}")
                continue

            layer_count = 0
            for obj in layer:
                record = self._build_record(obj, layer.name, supported_types)
                if record is None:
                    continue
                records.append(record)
                layer_count += 1
            print(f"[ObjectLoader] {layer.name} 读取对象数量: {layer_count}")

        self._print_type_counts(records)
        return records

    def _build_record(self, obj, layer_name: str, supported_types: set[str]) -> ObjectRecord | None:
        properties = dict(getattr(obj, "properties", {}) or {})
        layer_key = layer_name.strip().lower()
        object_type = str(properties.get("type") or getattr(obj, "type", "") or "").strip()
        if not object_type and layer_key in {"npc", "npc_points"}:
            object_type = "npc"
        elif not object_type and layer_key == "collision":
            object_type = "collision"
        object_name = str(getattr(obj, "name", "") or "")
        object_id = str(properties.get("id") or object_name or getattr(obj, "id", "") or "")

        if not object_type:
            print(f"[ObjectLoader] warning: 对象缺少 type，已跳过: layer={layer_name}, id={object_id or '(none)'}")
            return None
        if not object_id:
            object_id = f"{object_type}_{int(round(getattr(obj, 'x', 0)))}_{int(round(getattr(obj, 'y', 0)))}"
            print(f"[ObjectLoader] warning: 对象缺少 id，使用临时 id: {object_id}")

        normalized_type = object_type.strip().lower()
        if normalized_type not in supported_types:
            print(
                f"[ObjectLoader] warning: 对象类型不属于图层约定，仍保留: "
                f"layer={layer_name}, id={object_id}, type={normalized_type}"
            )

        rect = pygame.Rect(
            int(round(getattr(obj, "x", 0))),
            int(round(getattr(obj, "y", 0))),
            int(round(getattr(obj, "width", 0) or 32)),
            int(round(getattr(obj, "height", 0) or 32)),
        )
        return ObjectRecord(
            id=object_id,
            type=normalized_type,
            name=object_name or object_id,
            layer_name=layer_name,
            rect=rect,
            properties=properties,
        )

    def _print_type_counts(self, records: list[ObjectRecord]) -> None:
        target_types = (
            "spawn",
            "scene_exit",
            "npc",
            "item",
            "collision",
            "pattern_source",
            "pattern_checkpoint",
            "repair_table",
            "display_table",
            "shadow_spirit_spawn",
            "shadow_route_point",
            "shadow_fragment_trigger",
        )
        for object_type in target_types:
            count = sum(1 for record in records if record.type == object_type)
            print(f"[ObjectLoader] {object_type} 数量: {count}")
