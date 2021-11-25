class MyverError(Exception):
    """Configuration is invalid."""
    def __init__(self, message: str):
        self.message: str = message
        super().__init__()


class ConfigError(MyverError):
    """Configuration is invalid."""


class BumpError(MyverError):
    """Bumping a version or part failed."""
