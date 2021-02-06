from __future__ import annotations

from typing import Union

from simbump.part import Part, PartConfig


class VersionConfig:
    def __init__(self,
                 part_configs: dict[str, PartConfig] = None):
        self.part_configs: dict[str, PartConfig] = part_configs or []


class Version:
    """Represents a version.

    Fundamentally, a version is a collection of `Part` objects. You can
    perform operations on part objects within the version, most notably
    is the `bump()` operation.

    :param config: The version config. Stores all the part configs
        so that any part operation can perform necessary side effects
        on other related version parts.
    """

    def __init__(self,
                 config: VersionConfig,
                 part_values: dict[str, Union[str, int]] = None):
        self.config: VersionConfig = config

        # This is publicly exposed through properties. Changing part
        # values in this dict should not be done with this attribute.
        self._part_values: dict[str, Union[str, int]] = part_values or dict()

        # Use this instead to change the version parts.
        self._parts: dict[str, Part] = dict()
        self._reset_parts()

    @property
    def part_values(self) -> dict[str, Union[str, int]]:
        """Gets the part values for the version.

        :return: Part values for the version
        """
        self._reset_part_values()
        return self._part_values

    @part_values.setter
    def part_values(self, part_values: dict[str, Union[str, int]]):
        """Sets the part values for the version.

        :param part_values: New part values.
        """
        self._part_values = part_values
        self._reset_parts()

    def bump(self, part_key: str, child_parts: list[str] = None):
        """Bump the version based on the part key.

        :param part_key: The key of the part to bump.
        :param child_parts: Keys of non-required child parts that you
            want to set with the bumping of this part. For example, if
            you have a version of `3.9.1` and you bump `1`, it will
            become `3.9.2`. But if you want to have `3.9.1+dev` and
            `dev` is non-required child, then you need to bump `1` and
            specify `dev` within `child_parts`, otherwise the `1` part
            will have a child of `None`.
        """
        self._parts[part_key].bump(child_parts)

        # Remove non-required child parts which are also not specified.
        pop_keys = []
        for key in self.config.part_configs:
            if child_parts is None or key not in child_parts:
                if self.config.part_configs[key].required is False:
                    pop_keys.append(key)

        for key in pop_keys:
            child_key = self._parts[key].child_key
            self._parts.pop(child_key)
            self._parts.pop(key)

    def _reset_parts(self):
        """Gets the version parts in a dict.

        :return: Dict with the parts of the version. The keys of the
            dict is the name of the part.
        """
        for key in self._part_values:
            if self._part_values[key] is not None:
                part = Part(config=self.config.part_configs[key],
                            value=self._part_values[key])
                self._parts[key] = part

        # We need to set the parts references to their children.
        for key in self._parts:
            self._parts[key].set_child(self._parts)

    def _reset_part_values(self):
        """Gets the version parts in a dict.

        :return: Dict with the parts of the version. The keys of the
            dict is the name of the part.
        """
        self._part_values.clear()
        for key in self._parts:
            self._part_values[key] = self._parts[key].value

    def _sorted_part_list(self) -> list[Part]:
        """Gets the version parts in their proper order.

        :return: List of parts in order.
        """
        part_list = list(self._parts.values())
        return sorted(part_list)

    def __str__(self):
        version_str = ''
        for part in self._sorted_part_list():
            version_str += str(part)
        return version_str
