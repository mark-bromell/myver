class KeyConflictError(Exception):
    """Same key is used more than once for version parts."""
    def __init__(self, key: str):
        self.key: str = key
        super().__init__()

    def __str__(self):
        return f'Another part has the same key "{self.key}"'


class ConfigError(Exception):
    """Configuration is invalid."""
    def __init__(self, message: str):
        self.message: str = message
        super().__init__()

    def __str__(self):
        return self.message
