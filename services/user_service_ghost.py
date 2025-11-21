class UserServiceGhost:
    def __init__(self):
        self.items = []
        self.auto_id = 1

    def list(self):
        return self.items

    def get(self, item_id: int):
        for item in self.items:
            if item["id"] == item_id:
                return item
        return {"error": "Item not found"}    

    def create(self, item):
        obj = item.dict()
        obj["id"] = self.auto_id
        self.auto_id += 1

        self.items.append(obj)
        return obj

    def update(self, item_id: int, item):
        for idx, existing in enumerate(self.items):
            if existing["id"] == item_id:
                updated = {**existing, **item.dict()}
                self.items[idx] = updated
                return updated
        return {"error": "Item not found"}

    def delete(self, item_id: int):
        for idx, existing in enumerate(self.items):
            if existing["id"] == item_id:
                deleted = self.items.pop(idx)
                return deleted
        return {"error": "Item not found"}