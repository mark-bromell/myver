from __future__ import annotations

from typing import Union, Optional

from myver.part import Part


class Group:
    """Group of version parts.

    """

    def __init__(self,
                 key: str,
                 order: int,
                 parts: dict[str, Part],
                 prefix: str = None,
                 child: Optional[Part] = None):
        self.key: str = key
        self.order: int = order
        self.parts: dict[str, Part] = parts
        self.prefix: str = prefix or ''
        self.child: Optional[Group] = child

    @property
    def parts_raw(self) -> dict[str, Union[str, int]]:
        values: dict[str, str] = dict()
        for part in self.parts.values():
            values[part.key] = part.value
        return values

    def has_values(self) -> bool:
        """Checks if any parts have a value set."""
        for part in self.parts.values():
            if part.value is not None:
                return True
        return False

    def bump(self, keys: list[str]):
        pass

    def _reset_parts(self):
        for key in self.parts:
            self.parts[key].set_child(self.parts)

    def _sanitize_keys(self, parts_raw: dict[str, Union[str, int]]) -> dict:
        """Sanitizes invalid keys for this group.

        We may want to set the values of this group based on a dict.
        Although we do not want to have invalid keys sneak into this
        group, so we will remove keys that are not configured to be
        part of this group.

        :param parts_raw: The dict to sanitize the keys from.
        :return: A new dict with the invalid keys removed.
        """
        valid_keys = self.parts.keys()
        delete_keys = list()

        for key in parts_raw.keys():
            if key not in valid_keys:
                delete_keys.append(key)

        for key in delete_keys:
            del parts_raw[key]

        return parts_raw

    def __eq__(self, other: Group) -> bool:
        """Checks if this group is equal to another group.

        The group equality is compared on the following attributes:
        * Group's order
        * All parts are equal

        :param other: The other group to compare for equality.
        :return: True if the groups are equal.
        """
        return (self.order == other.order) and (self._parts == other._parts)

    def __lt__(self, other: Part) -> bool:
        """This is used as a component of sorting parts.

        Compares group's order to see if one is less than another.

        :param other: The other group to compare.
        :return: True if this group is less than the other group.
        """
        return self.order < other.order

    def __str__(self):
        group_str = ''
        first = True

        for part in sorted(list(self.parts.values())):
            if part.value is not None:
                if first:
                    group_str += f'{part}'
                    first = False
                else:
                    group_str += f'{part.prefix}{part}'

        return group_str
