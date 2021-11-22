from __future__ import annotations

from myver.error import ConfigError
from myver.part import Part


class Version:
    """Represents the version itself.

    This is the top level class for a version. It contains the groups
    of parts and this is where the version operations are performed.

    :param parts: The list of parts in the version.
    """

    def __init__(self, parts: list[Part] = None):
        self._parts: list[Part] = parts or list()
        self.parts = parts or list()

    @property
    def parts(self) -> list[Part]:
        return self._parts

    @parts.setter
    def parts(self, new_parts: list[Part]):
        """Sets the parts list.

        :param new_parts: The parts to set.
        :raise KeyConflictError: A part key appears 2 or more times in
            the list.
        """
        validate_keys(new_parts)
        validate_requires(new_parts)
        self._parts = new_parts
        set_relationships(self._parts)

    def bump(self, keys: list[str]):
        """Bump the version based on part keys.

        :param keys: The list of part keys to bump.
        """
        for key in keys:
            self.part(key).bump(keys)

    def part(self, key: str) -> Part:
        """Gets a part based on its key.

        :param key: The key of the part you are getting.
        :raise KeyError: If no part has the key provided.
        """
        for part in self._parts:
            if part.key == key:
                return part
        raise KeyError(key)

    def __eq__(self, other: Version):
        for this_part, other_part in zip(self.parts, other.parts):
            if not this_part == other_part:
                return False
        return True

    def __str__(self):
        version_str = ''

        for part in self._parts:
            if part.is_set():
                version_str += str(part)

        return version_str


def validate_requires(parts: list[Part]):
    """Validates that parts require other valid parts.

    :raise ConfigError: If a part requires itself or a part that does
        not exist.
    """
    keys = [p.key for p in parts] or []
    for part in parts:
        if not part.requires:
            continue

        if part.requires == part.key:
            raise ConfigError(
                f'Part `{part.key}` has a `requires` key that is'
                f'referencing itself, it must reference another part')
        if part.requires not in keys:
            raise ConfigError(
                f'Part `{part.key}` has a `requires` key '
                f'"{part.requires}" that does not exist, it must be a '
                f'valid key of another part')


def validate_keys(parts: list[Part]):
    """Validates that they keys are unique.

    :raise ConfigError: If two or more parts with the same key.
    """
    keys = [p.key for p in parts] or []
    for key in keys:
        if keys.count(key) > 1:
            raise ConfigError(
                f'Key "{key}" is configured on more than one part, all '
                f'parts must have a unique key')


def set_relationships(parts: list[Part]):
    """Sets the parent-child relationships between a list of parts.

    :param parts: The parts to set the relationships for.
    """
    for i in range(len(parts)):
        if i < len(parts) - 1:
            parts[i].child = parts[i + 1]
