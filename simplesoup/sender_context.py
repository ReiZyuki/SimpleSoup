class SenderContext:
    def __init__(self, namespace=None):
        self._namespace = namespace if namespace is not None else {}

    def get(self, name):
        if not isinstance(name, str) or not name:
            raise ValueError("Variable name must be a non-empty string.")

        if name not in self._namespace:
            raise NameError(
                f"Sender variable not found: {name}"
            )

        return self._namespace[name]

    def set(self, name, value):
        if not isinstance(name, str) or not name:
            raise ValueError("Variable name must be a non-empty string.")

        self._namespace[name] = value

    def update(self, values):
        if values is None:
            return

        if not hasattr(values, "items"):
            raise TypeError(
                "Sender context must be a mapping."
            )

        self._namespace.update(values)

    def snapshot(self):
        return dict(self._namespace)

    def contains(self, name):
        return name in self._namespace
