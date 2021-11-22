class ConfigError(Exception):
    """Configuration is invalid."""
    def __init__(self, message: str):
        self.message: str = message
        super().__init__()

    def __str__(self):
        return self.message
