from __future__ import annotations

import argparse
import sys

from myver.config import config_from_dict, dict_from_file


def main(args=None):
    """Entry point for the command line utility."""
    pass


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


def _current_version():
    config_path = 'myver.yaml'
    try:
        config = config_from_dict(dict_from_file(config_path))
        return config.as_version()
    except FileNotFoundError:
        print(f'File {config_path} not found, it is needed for version '
              f'configuration')
        sys.exit(1)
    except OSError as os_error:
        print(f"OS error occurred trying to open {config_path}")
        print(os_error.strerror)
        sys.exit(1)
