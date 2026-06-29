from __future__ import annotations


class MainQuestManager:
    """In-memory main quest state for the three demo levels."""

    STAGE_OBJECTIVES = {
        "intro": (
            "\u4e0e\u6751\u5be8\u957f\u8005\u5bf9\u8bdd",
            "\u4e86\u89e3\u94f6\u9970\u5931\u5149\u7684\u539f\u56e0",
        ),
        "go_market": (
            "\u524d\u5f80\u5c71\u5730\u96c6\u5e02",
            "\u5bfb\u627e\u94f6\u4e1d\u6750\u6599\u548c\u7eb9\u6837\u7ebf\u7d22",
        ),
        "market_collect": (
            "\u6536\u96c6\u96c6\u5e02\u7ebf\u7d22",
            "\u9760\u8fd1\u6750\u6599\u6216\u7eb9\u6837\u70b9\uff0c\u6309 E \u6536\u96c6",
        ),
        "go_river": (
            "\u524d\u5f80\u6cb3\u8c37",
            "\u51c0\u5316\u6df7\u4e71\u5f71\u7eb9\uff0c\u83b7\u5f97\u5c71\u7eb9\u7ebf\u7d22",
        ),
        "shadow_challenge": (
            "\u51c0\u5316\u5f71\u7eb9",
            "\u9760\u8fd1\u5f71\u7eb9\u540e\u6309 Space \u91ca\u653e\u94f6\u5149",
        ),
        "go_festival": (
            "\u524d\u5f80\u8282\u5e86\u5e7f\u573a",
            "\u5b88\u62a4\u4fee\u590d\u540e\u7684\u94f6\u9970",
        ),
        "festival_defense": (
            "\u5b88\u62a4\u94f6\u9970\u5c55\u793a\u53f0",
            "\u51c0\u5316\u9760\u8fd1\u5c55\u793a\u53f0\u7684\u5f71\u7eb9",
        ),
        "ending": (
            "\u8282\u5e86\u5c55\u793a\u5b8c\u6210",
            "\u94f6\u9970\u91cd\u65b0\u6062\u590d\u5149\u8292",
        ),
    }

    VALID_STAGES = tuple(STAGE_OBJECTIVES.keys())
    REQUIRED_LEVELS = ("market_collect", "shadow_challenge", "festival_defense")
    ENDING_COLLECT_ITEMS = (
        "silver_thread",
        "flower_bird_pattern_clue",
        "pattern_wooden_plaque",
        "mountain_pattern_clue",
    )
    ITEM_ALIASES = {
        "bird_pattern_clue": "flower_bird_pattern_clue",
        "market_pattern_board": "pattern_wooden_plaque",
    }

    def __init__(self) -> None:
        self.stage = "intro"
        self.items: set[str] = set()
        self.completed_levels: set[str] = set()
        self.player_light = 3
        self.max_player_light = 3

    def get_objective(self) -> tuple[str, str]:
        return self.STAGE_OBJECTIVES.get(self.stage, self.STAGE_OBJECTIVES["intro"])

    def advance_to(self, stage: str) -> None:
        if stage not in self.STAGE_OBJECTIVES:
            print(f"[QUEST][WARN] unknown stage={stage}")
            return
        if stage == self.stage:
            return
        old_stage = self.stage
        self.stage = stage
        print(f"[QUEST] {old_stage} -> {stage}")

    def force_stage(self, stage: str) -> None:
        if stage not in self.STAGE_OBJECTIVES:
            print(f"[QUEST][WARN] unknown debug stage={stage}")
            return
        self.stage = stage
        print(f"[QUEST][DEBUG] force stage={stage}")

    def add_item(self, item_id: str) -> None:
        if not item_id:
            return
        item_id = self.ITEM_ALIASES.get(item_id, item_id)
        if item_id not in self.items:
            self.items.add(item_id)
            print(f"[QUEST] item added={item_id}")

    def has_item(self, item_id: str) -> bool:
        item_id = self.ITEM_ALIASES.get(item_id, item_id)
        return item_id in self.items

    def get_items(self) -> set[str]:
        return set(self.items)

    def get_completed_levels(self) -> set[str]:
        return set(self.completed_levels)

    def complete_level(self, level_id: str) -> None:
        if not level_id:
            return
        if level_id not in self.completed_levels:
            self.completed_levels.add(level_id)
            print(f"[QUEST] {level_id} complete")

    def all_required_levels_completed(self) -> bool:
        return all(level_id in self.completed_levels for level_id in self.REQUIRED_LEVELS)

    def collected_count_for_ending(self) -> int:
        return sum(1 for item_id in self.ENDING_COLLECT_ITEMS if item_id in self.items)

    def restore_light(self) -> None:
        self.player_light = self.max_player_light

    def damage_light(self, amount: int = 1) -> int:
        self.player_light = max(0, self.player_light - max(0, amount))
        return self.player_light
