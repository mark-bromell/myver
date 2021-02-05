from __future__ import annotations

from simbump.part import PartConfig, Part


class VersionConfig:
    def __init__(self,
                 part_configs: dict[str, PartConfig] = None):
        self.part_configs: dict[str, PartConfig] = part_configs or []


class Version:
    def __init__(self,
                 config: VersionConfig,
                 part_values: dict = None):
        self.config: VersionConfig = config
        self.part_values: dict = part_values or dict()

    @property
    def parts(self) -> list[Part]:
        """Gets the parts in their proper order.

        :return: List of parts in order.
        """
        part_list: list[Part] = []

        for key in self.part_values:
            part = Part(config=self.config.part_configs[key],
                        value=self.part_values[key])
            part_list.append(part)

        # We need to set the parts references to their children.
        for part in part_list:
            part.set_child(part_list)

        return sorted(part_list)

    def __str__(self):
        parts = self.parts
        version_str = ''
        for part in parts:
            version_str += str(part)
        return version_str
