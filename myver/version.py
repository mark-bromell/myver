from __future__ import annotations

from myver.error import KeyConflictError
from myver.part import Part


class Version:
    """Represents the version itself.

    This is the top level class for a version. It contains the groups
    of parts and this is where the version operations are performed.

    :param parts:
    """

    def __init__(self, parts: list[Part] = None):
        self._parts: list[Part] = parts or list()
        self.parts = parts or list()

    @property
    def parts(self) -> list[Part]:
        return self._parts

    @parts.setter
    def parts(self, parts: list[Part]):
        """Sets the parts list.

        :param parts: The parts to set.
        :raise KeyConflictError: A part key appears 2 or more times in
            the list.
        """
        self._parts = parts

        # Make sure all keys are unique.
        keys = [p.key for p in self._parts]
        if len(keys) > len(set(keys)):
            raise KeyConflictError

        # Set the relationships for each part.
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
