class BumpChildArg:
    """Represents the child arguments to set along with a version bump.

    :param part_key: The key of the child part.
    :param part_value: The value that you want the child part to bet
        set at. If this attribute is `None`, then the child part will
        set itself to its starting value.
    """

    def __init__(self,
                 part_key: str,
                 part_value: str = None):
        self.part_key: str = part_key
        self.part_value: str = part_value


class BumpArgs:
    """Represents arguments for bumping a version.

    :param part_key: The key of the part that is being bumped.
    :param child_args: The child args that you want to attach to the
        bump. See `BumpChildArgs` for details on the purpose of this.
    """

    def __init__(self,
                 part_key: str,
                 child_args: list[BumpChildArg] = None):
        self.part_key: str = part_key
        self.child_args: list[BumpChildArg] = child_args or []
