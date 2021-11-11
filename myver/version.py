from __future__ import annotations

from typing import Union

from myver.group import Group


class Version:
    """Represents the version itself.

    This is the top level class for a version. It contains the groups
    of parts and this is where the version operations are performed.

    :param groups: The configs of each of the groups of the
        version. This is used for helping operations on the actual
        version values.
    """

    def __init__(self, groups: dict[str, Group] = None):
        self.groups: dict[str, Group] = groups or dict()

    @property
    def parts_raw(self) -> dict[str, Union[str, int]]:
        values: dict[str, Union[str, int]] = dict()
        for group in self.groups.values():
            values = values | group.parts_raw
        return values

    def bump(self, keys: list[str]):
        """Bump the version based on part keys.

        :param keys: The list of part keys to bump.
        """
        for group in self.groups.values():
            group.bump(keys)

    def __str__(self):
        version_str = ''
        first = True

        for group in sorted(list(self.groups.values())):
            if group.has_values():
                if first:
                    version_str += f'{group}'
                    first = False
                else:
                    version_str += f'{group.prefix}{group}'

        return version_str
