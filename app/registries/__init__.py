class Registry:
    def __init__(self):
        self._registry = {}

    def register(self, name: str, item):
        existing = self._registry.get(name)
        if existing is not None:
            if existing is item:
                return
            raise KeyError(f"{name} already registered")
        self._registry[name] = item

    def get(self, name: str):
        return self._registry.get(name)

    def all(self):
        return dict(self._registry)
