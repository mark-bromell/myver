from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Union

import yaml

from myver.error import ConfigError


@dataclass
class VersionConfig:
    part_configs: list[PartConfig]


@dataclass
class PartConfig:
    key: str
    """The unique key of the part. This is used to set dict keys for 
    collections of parts.
    """

    value: Optional[Union[str, int]]
    """The actual value of the part."""

    requires: Optional[str] = None
    """Another part that this part requires. This means that the required part
    will need to be set if this part is set.
    """

    prefix: Optional[str] = None
    """The prefix of the part."""

    identifier: Optional[IdentifierConfig] = None
    """Configuration for identifier part."""

    number: Optional[NumberConfig] = None
    """Configuration for number part."""

    def __post_init__(self):
        if not self.identifier and not self.number:
            self.number = NumberConfig()

    def set_part_type(self, part_raw: dict):
        """Either identifier or number parts only.

        :raise ConfigError: If the part type is ambiguous.
        """
        if part_raw.get('identifier') and part_raw.get('number'):
            raise ConfigError(
                f'Part `{self.key}` cannot be an identifier and number at the '
                f'same time. Configure either `number` or `identifier` '
                f'attribute')
        elif part_raw.get('identifier'):
            identifier_raw: dict = part_raw['identifier']
            self._set_identifier(identifier_raw)
        elif part_raw.get('number'):
            number_raw: dict = part_raw['number']
            self._set_number(number_raw)
        else:
            self.number = NumberConfig()

    def _set_identifier(self, identifier_raw: dict):
        if identifier_raw.get('start'):
            if identifier_raw['start'] not in identifier_raw['strings']:
                raise ConfigError(
                    f'Part `{self.key}` has an `identifier.start` value that '
                    f'is not in the `identifier.strings` list')

        self.identifier = IdentifierConfig(
            strings=identifier_raw['strings'],
            start=identifier_raw.get('start'))

    def _set_number(self, number_raw: dict):
        if number_raw.get('start'):
            try:
                int(number_raw['start'])
            except ValueError:
                raise ConfigError(
                    f'Part `{self.key}` has an invalid value for its '
                    f'`number.start` attribute, it must be an integer')

            if int(number_raw['start']) < 0:
                raise ConfigError(
                    f'Part `{self.key}` has an negative value for its '
                    f'`number.start` attribute, it must be positive')

        self.number = NumberConfig(
            label=number_raw.get('label'),
            label_suffix=number_raw.get('label-suffix'),
            start=number_raw.get('start', 0),
            show_start=number_raw.get('show_start', True))


@dataclass
class IdentifierConfig:
    strings: list[str]
    """List of valid strings that can be used as an
    identifier for this part.
    """

    start: str = None
    """The starting value of the part. This is used when the part goes out of a
    null state, or is reset to its original state. If this is specified it must
    be a string that is in the `self.strings` list.
    """

    def __post_init__(self):
        if len(self.strings) > 0 and self.start is None:
            self.start = self.strings[0]


@dataclass
class NumberConfig:
    label: Optional[str] = None
    """The label for the number part."""

    label_suffix: Optional[str] = None
    """The suffix to use for separating the label and the number."""

    start: int = 0
    """The starting value of the part. This is used when the part goes out of a
    null state, or is reset to its original state.
    """

    show_start: bool = True
    """If true, the start value will be shown in the version. If false, then
    the start value wont be shown although the next value (after a bump) will
    be shown.
    """


def dict_from_file(path: str) -> dict:
    """Gets the dict config from a file.

    The default file path is `myver.yml`, which is a relative path. This
    path can be overridden by using the `path` arg.

    :param path: The path to the myver config file.
    :raise FileNotFoundError: If the file does not exist.
    :raise OSError: For other errors when accessing the file.
    """
    with open(path, 'r') as file:
        config_dict = yaml.safe_load(file)
        return config_dict


def config_from_dict(config_dict: dict) -> VersionConfig:
    """Construct version config from a dict.

    :param config_dict: The dict with raw version config data.
    :return: The version configuration.
    :raise ConfigError: If the configuration dict is invalid.
    :raise KeyError: If the config is missing required attributes.
    """
    part_configs: list[PartConfig] = []
    # Making part config objects
    for key, part_dict in config_dict['parts']:
        part_config = PartConfig(
            key=key,
            value=part_dict['value'],
            requires=part_dict.get('requires'),
            prefix=part_dict.get('prefix'))
        part_config.set_part_type(part_dict)
        part_configs.append(part_config)

    # Ensuring `requires` points to real keys
    keys = [p.key for p in part_configs] or []
    for part_config in part_configs:
        if part_config.requires == part_config.key:
            raise ConfigError(
                f'Part `{part_config.key}` has a `requires` value that is'
                f'referencing itself, it must reference another part')
        if part_config.requires not in keys:
            raise ConfigError(
                f'Part `{part_config.key}` has a `requires` value that does '
                f'not exist, it must be a valid key of another part')

    return VersionConfig(part_configs)
