class TaskManager:
    """Minimal task state owner for current lightweight main-flow events."""

    def __init__(self) -> None:
        self.current_task_id = "main_intro"
        self.task_status: dict[str, str] = {
            "main_intro": "active",
            "main_shadow_chase": "not_started",
        }

    def start_shadow_chase(self) -> None:
        self.current_task_id = "main_shadow_chase"
        self.task_status["main_shadow_chase"] = "active"
        print("[TaskManager] current task: 追回被影纹带走的银饰碎片")

    def complete_shadow_chase(self, next_task_id: str | None = None) -> None:
        self.task_status["main_shadow_chase"] = "completed"
        if next_task_id:
            self.current_task_id = next_task_id
            self.task_status.setdefault(next_task_id, "active")
        print(f"[TaskManager] main_shadow_chase completed, next={self.current_task_id}")

    def is_completed(self, task_id: str) -> bool:
        return self.task_status.get(task_id) == "completed"
