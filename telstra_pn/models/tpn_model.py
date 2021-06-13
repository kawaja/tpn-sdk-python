from typing import Any


class TPNModel:
    def __getattr__(self, name: str) -> Any:
        d = self.data
        if name in d:
            return d[name]
