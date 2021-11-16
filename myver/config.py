from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Optional, Union

import yaml

from myver.error import ConfigError
from myver.part import Part, NumberPart, IdentifierPart
from myver.version import Version


@dataclass
class MyverConfig:
    parts: list[PartConfig]

    def as_version(self):
        """Gets the version config as a `Version` object."""
        parts: list[Part] = []
        for part_config in self.parts:
            parts.append(part_config.as_part())
        return Version(parts)


@dataclass
class PartConfig:
    key: str
    value: Optional[Union[str, int]]
    requires: Optional[str] = None
    prefix: Optional[str] = None
    identifier: Optional[IdentifierConfig] = None
    number: Optional[NumberConfig] = None

    def as_part(self) -> Part:
        """Gets the part config as a `Part` object."""
        if self.identifier:
            return IdentifierPart(
                key=self.key,
                value=self.value,
                requires=self.requires,
                prefix=self.prefix,
                strings=self.identifier.strings,
                start=self.identifier.start)
        if self.number:
            return NumberPart(
                key=self.key,
                value=self.value,
                requires=self.requires,
                prefix=self.prefix,
                label=self.number.label,
                label_suffix=self.number.label_suffix,
                start=self.number.start,
                show_start=self.number.show_start)

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
            start=identifier_raw.get('start', identifier_raw['strings'][0]))

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
    start: str = None


@dataclass
class NumberConfig:
    label: Optional[str] = None
    label_suffix: Optional[str] = None
    start: int = 0
    show_start: bool = True


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


def config_from_dict(config_dict: dict) -> MyverConfig:
    """Construct version config from a dict.

    :param config_dict: The dict with raw version config data.
    :return: The version configuration.
    :raise ConfigError: If the configuration dict is invalid.
    :raise KeyError: If the config is missing required attributes.
    """
    parts: list[PartConfig] = []
    # Making part config objects
    for key, part_dict in config_dict['parts']:
        part = PartConfig(
            key=key,
            value=part_dict['value'],
            requires=part_dict.get('requires'),
            prefix=part_dict.get('prefix'))
        part.set_part_type(part_dict)
        parts.append(part)

    # Ensuring `requires` points to real keys
    keys = [p.key for p in parts] or []
    for part in parts:
        if part.requires == part.key:
            raise ConfigError(
                f'Part `{part.key}` has a `requires` value that is'
                f'referencing itself, it must reference another part')
        if part.requires not in keys:
            raise ConfigError(
                f'Part `{part.key}` has a `requires` value that does not'
                f'exist, it must be a valid key of another part')

    return MyverConfig(parts)
