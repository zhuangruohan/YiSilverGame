class Inventory:
    """Minimal inventory container used by lightweight event rewards."""

    def __init__(self) -> None:
        self.items: list[str] = []

    def add(self, item_id: str) -> None:
        if item_id not in self.items:
            self.items.append(item_id)
            print(f"[Inventory] add item: {item_id}")

    def has(self, item_id: str) -> bool:
        return item_id in self.items
