import argparse
import sys
import textwrap

from myver.config import version_from_file, version_to_file


def main(input_args=None):
    """Entry point for the command line utility."""
    args = _parse_args(input_args)

    if args.help:
        print(textwrap.dedent('''\
        usage: myver [-h] [-c] [-b ARG [...]] [-r PART [...]] [--config PATH]

          -h, --help               Show this help message and exit
          -c, --current            Get the current version
          -b, --bump ARG [...]     Bump version parts
          -r, --reset PART [...]   Reset version parts
          --config PATH            Config file path
        '''))
        sys.exit(0)
    if args.current:
        version = version_from_file(args.config)
        print(version)
    if args.bump:
        version = version_from_file(args.config)
        old_version_str = str(version)
        version.bump(args.bump)
        new_version_str = str(version)
        version_to_file(args.config, version)
        print(f'{old_version_str}  >>  {new_version_str}')
    if args.reset:
        version = version_from_file(args.config)
        old_version_str = str(version)
        version.reset(args.reset)
        new_version_str = str(version)
        version_to_file(args.config, version)
        print(f'{old_version_str}  >>  {new_version_str}')


def _parse_args(args):
    parser = argparse.ArgumentParser(
        prog='myver',
        add_help=False,
    )
    parser.add_argument(
        '-h', '--help',
        required=False,
        action='store_true',
    )
    parser.add_argument(
        '-c', '--current',
        required=False,
        action='store_true',
    )
    parser.add_argument(
        '-b', '--bump',
        required=False,
        action='extend',
        nargs='+',
        type=str,
    )
    parser.add_argument(
        '-r', '--reset',
        required=False,
        action='extend',
        nargs='+',
        type=str,
    )
    parser.add_argument(
        '--config',
        required=False,
        default='myver.yml',
        type=str,
    )
    return parser.parse_args(args)
