from __future__ import annotations

from myver.part import Part


class Version:
    """Represents the version itself.

    This is the top level class for a version. It contains the groups
    of parts and this is where the version operations are performed.

    :param parts:
    """

    def __init__(self, parts: list[Part] = None):
        self._parts: list[Part] = parts or list()
        self.parts = parts

    @property
    def parts(self) -> list[Part]:
        return self._parts

    @parts.setter
    def parts(self, value: list[Part]):
        self._parts = value
        # Set the relationships for each part.
        for i in range(len(self._parts)):
            if i < len(self._parts) - 1:
                self._parts[i].child = self._parts[i + 1]
                self._parts[i + 1].parent = self._parts[i]

    def bump(self, keys: list[str]):
        """Bump the version based on part keys.

        :param keys: The list of part keys to bump.
        """
        pass

    def __str__(self):
        version_str = ''

        for part in self._parts:
            if part.is_set():
                version_str += str(part)

        return version_str
