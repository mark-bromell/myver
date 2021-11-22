from __future__ import annotations

import argparse
import sys

from myver.config import version_from_file, version_to_file
from myver.version import Version


def main(input_args=None):
    """Entry point for the command line utility."""
    args = _parse_args(input_args)

    if args.current:
        version = _current_version(args.config)
        print(version)
    if args.bump:
        version = _current_version(args.config)
        old_version_str = str(version)
        version.bump(args.bump)
        new_version_str = str(version)
        _save_version(version, args.config)
        print(f'{old_version_str}  >>  {new_version_str}')


def _parse_args(args):
    parser = argparse.ArgumentParser(prog='myver')
    parser.add_argument(
        '-b', '--bump',
        help='bump version parts',
        required=False,
        action='extend',
        nargs='+',
        type=str,
    )
    parser.add_argument(
        '-c', '--current',
        help='get the current version',
        required=False,
        action='store_true',
    )
    parser.add_argument(
        '--config',
        help='config file path',
        required=False,
        default='myver.yml',
        type=str,
    )
    return parser.parse_args(args)


def _current_version(config_path: str):
    try:
        return version_from_file(config_path)
    except FileNotFoundError:
        print(f'File {config_path} not found, it is needed for version '
              f'configuration')
        sys.exit(1)
    except OSError as os_error:
        print(f'OS error occurred trying to open {config_path}')
        print(os_error.strerror)
        sys.exit(1)


def _save_version(version: Version, config_path: str):
    try:
        return version_to_file(config_path, version)
    except FileNotFoundError:
        print(f'File {config_path} not found, it is needed for version '
              f'configuration')
        sys.exit(1)
    except OSError as os_error:
        print(f'OS error occurred trying to open {config_path}')
        print(os_error.strerror)
        sys.exit(1)
