from __future__ import annotations

from myver.config import VersionConfig
from myver.part import Part, IdentifierPart, NumberPart


class Version:
    """Represents the version itself.

    This is the top level class for a version. It contains the groups
    of parts and this is where the version operations are performed.

    :param config: Configuration for the version
    """

    def __init__(self, config: VersionConfig):
        self.config: VersionConfig = config
        self._parts: list[Part] = []
        self._set_parts()

    @property
    def parts(self) -> list[Part]:
        return self._parts

    def _set_parts(self):
        """Sets the part objects based on `self.config`."""
        for part_config in self.config.part_configs:
            if part_config.identifier:
                self._parts.append(IdentifierPart(config=part_config))
            if part_config.number:
                self._parts.append(NumberPart(config=part_config))

        self._set_part_relationships()

    def _set_part_relationships(self):
        """Sets the relationships for `self._parts`."""
        for i in range(len(self._parts)):
            if i < len(self._parts) - 1:
                self._parts[i].child = self._parts[i + 1]

    def bump(self, keys: list[str]):
        """Bump the version based on part keys.

        :param keys: The list of part keys to bump.
        """
        for key in keys:
            self.part(key).bump()

    def part(self, key: str) -> Part:
        """Gets a part based on its key.

        :param key: The key of the part you are getting.
        :raise KeyError: If no part has the key provided.
        """
        for part in self._parts:
            if part.key == key:
                return part
        raise KeyError

    def __str__(self):
        version_str = ''

        for part in self._parts:
            if part.is_set():
                version_str += str(part)

        return version_str
