from __future__ import annotations

import ruamel.yaml

from myver.error import ConfigError
from myver.files import FileUpdater
from myver.part import Part, IdentifierPart, NumberPart
from myver.version import Version


class Config:
    def __init__(self,
                 path: str = None,
                 files: list[FileUpdater] = None,
                 version: Version = None):
        self.path: str = path
        self.files: list[FileUpdater] = files
        self.version: Version = version
        if path and not (files or version):
            self.load()

    def load(self):
        """Load the config from `self.path`."""
        self._load_files()
        self._load_version()

    def _load_files(self):
        config_dict = dict_from_yaml(self.path)
        self.files = files_from_dict(config_dict)

    def _load_version(self):
        """Construct version from a config dict.

        :raise ConfigError: If the configuration is invalid.
        :return: The version.
        """
        config_dict = dict_from_yaml(self.path)
        self.version = version_from_dict(config_dict)

    def save(self):
        """Syncs a version to a yaml file.

        This will only sync the part values to the file, no other
        configuration of the file will change. This will mean that the
        parts in the version will need to have perfect 1:1 corresponding
        keys for each part and within the yaml file and in the `version`
        param. This also means that the yaml file must have existing
        configuration details for each part in the `version` param.

        :raise FileNotFoundError: If the file does not exist.
        :raise OSError: For other errors when accessing the file.
        :raise ConfigError: When the yaml file does not have a 1:1 of
            keys for parts compared to the `version` param.
        """
        try:
            self._save_version_values()
        except KeyError as key_error:
            key = key_error.args[0]
            raise ConfigError(
                f'You must have the required attribute `{key}` configured')

    def _save_version_values(self):
        """Update config file part based on `version` object."""
        update_map = self._get_value_update_map()

        with open(self.path, 'r') as file:
            lines = file.readlines()

        with open(self.path, 'w') as file:
            for index, value in update_map.items():
                indent_length = len(lines[index]) - len(lines[index].lstrip())
                lines[index] = f'{" " * indent_length}value: {value}\n'

            file.writelines(lines)

    def _get_value_update_map(self) -> dict[int, str]:
        """Get an update map for version values in a config file.

        :return: A dict with each key in the dict represents the index
            in the lines list to update (based on index counter starting
            at 0). The value of each entry in the dict represents a
            part's value to be updated at the given line index.
        """
        config_dict = dict_from_yaml(self.path)
        update_map = dict()

        with open(self.path, 'r') as file:
            lines = file.readlines()

            for key in config_dict['parts'].keys():
                # We want to start at the part's key so that the next
                # `value` node is guaranteed to be the part's `value` node.
                from_index = config_dict['parts'][key].lc.line
                # Note, it's an index (as related to list indexes) and not
                # a line number.
                line_index = find_value_node_index(lines, from_index)
                part = self.version.part(key)

                if part.value is None:
                    update_map[line_index] = 'null'
                else:
                    update_map[line_index] = part.value

        return update_map


def dict_from_yaml(path: str) -> dict:
    """Gets the dict config from a file.

    The default file path is `myver.yml`, which is a relative path. This
    path can be overridden by using the `path` arg.

    :param path: The path to the myver config file.
    :raise FileNotFoundError: If the file does not exist.
    :raise OSError: For other errors when accessing the file.
    """
    with open(path, 'r') as file:
        yaml = ruamel.yaml.YAML()
        config_dict = yaml.load(file)
    return config_dict


def find_value_node_index(lines: list[str], from_index: int) -> int:
    """Find the line index for the `value` node.

    :param lines: The lines to read from in order to get the index.
    :param from_index: The index to start searching from.
    :return: The index of where the `value` node is.
    """
    for i, line in enumerate(lines[from_index:]):
        if line.lstrip().startswith('value:'):
            return i + from_index


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
            f'You must have the required attribute `{key}` configured in '
            f'`parts`')


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


def files_from_dict(config_dict: dict) -> list[FileUpdater]:
    try:
        file_updaters: list[FileUpdater] = []
        for file_config in config_dict.get('files', []):
            file_updaters.append(FileUpdater(
                path=file_config['path'],
                patterns=file_config.get('patterns')
            ))
        return file_updaters
    except KeyError as key_error:
        key = key_error.args[0]
        raise ConfigError(
            f'You must have the required attribute `{key}` configured in '
            f'`files`')
