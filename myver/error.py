class Error(Exception):
    """Configuration is invalid."""
    def __init__(self, message: str):
        self.message: str = message
        super().__init__()

    def __str__(self):
        return self.message


class ConfigError(Error):
    """Configuration is invalid."""


class BumpError(Error):
    """Bumping a version or part failed."""
