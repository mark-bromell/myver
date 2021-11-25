import argparse

from myver.config import version_from_file, version_to_file


def main(input_args=None):
    """Entry point for the command line utility."""
    args = _parse_args(input_args)

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
    parser = argparse.ArgumentParser(prog='myver')
    parser.add_argument(
        '-c', '--current',
        help='get the current version',
        required=False,
        action='store_true',
    )
    parser.add_argument(
        '-b', '--bump',
        help='bump version parts',
        metavar='ARG',
        required=False,
        action='extend',
        nargs='+',
        type=str,
    )
    parser.add_argument(
        '-r', '--reset',
        help='reset version parts',
        metavar='PART',
        required=False,
        action='extend',
        nargs='+',
        type=str,
    )
    parser.add_argument(
        '--config',
        help='config file path',
        required=False,
        default='myver.yml',
        type=str,
    )
    return parser.parse_args(args)
