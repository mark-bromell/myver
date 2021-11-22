from __future__ import annotations

import ruamel.yaml

from myver.error import ConfigError
from myver.part import Part, IdentifierPart, NumberPart
from myver.version import Version


def dict_from_file(path: str) -> dict:
    """Gets the dict config from a file.

    The default file path is `myver.yml`, which is a relative path. This
    path can be overridden by using the `path` arg.

    :param path: The path to the myver config file.
    :raise FileNotFoundError: If the file does not exist.
    :raise OSError: For other errors when accessing the file.
    """
    with open(path, 'r') as file:
        yaml = ruamel.yaml.YAML(typ='safe')
        config_dict = yaml.load(file)
    return config_dict


def version_to_file(path: str, version: Version):
    """Syncs a version to a yaml file.

    This will only sync the part values to the file, no other
    configuration of the file will change. This will mean that the parts
    in the version will need to have perfect 1:1 corresponding keys for
    each part and within the yaml file and in the `version` param. This
    also means that the yaml file must have existing configuration
    details for each part in the `version` param.

    :param path: The path of the yaml file.
    :param version: The version to sync to the yaml file.
    :raise FileNotFoundError: If the file does not exist.
    :raise OSError: For other errors when accessing the file.
    :raise ConfigError: When the yaml file does not have a 1:1 of keys
        for parts compared to the `version` param.
    """
    try:
        config_dict = dict_from_file(path)
        for key, part_dict in config_dict['parts'].items():
            config_dict['parts'][key]['value'] = version.part(key).value

        yaml = ruamel.yaml.YAML()
        with open(path, 'w') as file:
            yaml.dump(config_dict, file)
    except KeyError as key_error:
        key = key_error.args[0]
        raise ConfigError(
            f'You must have the required attribute `{key}` configured')


def version_from_file(path: str) -> Version:
    """Construct version from a config dict.

    :param path: The path of the yaml file.
    :raise ConfigError: If the configuration is invalid.
    :return: The version.
    """
    config_dict = dict_from_file(path)
    return version_from_dict(config_dict)


def version_from_dict(config_dict: dict) -> Version:
    """Construct version from a config dict.

    :param config_dict: The dict with raw version config data.
    :raise ConfigError: If the configuration dict is invalid.
    :return: The version.
    """
    try:
        parts: list[Part] = []
        for part_key, part_dict in config_dict['parts'].items():
            parts.append(part_from_dict(part_key, part_dict))
        return Version(parts)
    except KeyError as key_error:
        key = key_error.args[0]
        raise ConfigError(
            f'You must have the required attribute `{key}` configured')


def part_from_dict(key: str, config_dict: dict) -> Part:
    """Construct part from a config dict.

    :param key: The part's key.
    :param config_dict: The dict with raw part config data.
    :raise ConfigError: If the configuration dict is invalid.
    :raise KeyError: If the config is missing required attributes.
    :return: The version part.
    """
    if config_dict.get('identifier') and config_dict.get('number'):
        raise ConfigError(
            f'Part `{key}` cannot be an identifier and number at the '
            f'same time. Configure either `number` or `identifier` '
            f'attribute')
    elif config_dict.get('identifier'):
        return IdentifierPart(
            key=key,
            value=config_dict['value'],
            strings=config_dict['identifier']['strings'],
            requires=config_dict.get('requires'),
            prefix=config_dict.get('prefix'),
            start=config_dict['identifier'].get('start'))
    elif config_dict.get('number'):
        return NumberPart(
            key=key,
            value=config_dict['value'],
            requires=config_dict.get('requires'),
            prefix=config_dict.get('prefix'),
            label=config_dict['number'].get('label'),
            label_suffix=config_dict['number'].get('label-suffix'),
            start=config_dict['number'].get('start'),
            show_start=config_dict['number'].get('show-start'))
    else:
        # Default if no type configuration is specified.
        return NumberPart(
            key=key,
            value=config_dict['value'],
            requires=config_dict.get('requires'),
            prefix=config_dict.get('prefix'))
