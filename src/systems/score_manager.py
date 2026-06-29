class ScoreManager:
    """Score owner for silver light and final rating."""

    def __init__(self) -> None:
        self.silver_light = 0

    def add_silver_light(self, amount: int) -> None:
        self.silver_light += amount
        print(f"[ScoreManager] silver_light={self.silver_light}")
