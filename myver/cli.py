import argparse
import logging
import sys
import textwrap

from myver.config import Config


def main(input_args=None):
    """Entry point for the command line utility."""
    args = _parse_args(input_args)

    if args.verbose:
        logging.root.setLevel(logging.INFO)
    if args.debug:
        logging.root.handlers[0].setFormatter(
            logging.Formatter('[%(levelname)s] [%(module)s] %(message)s')
        )
        logging.root.setLevel(logging.DEBUG)

    if args.help:
        print(textwrap.dedent('''\
        usage: myver [-h] [-c] [-b ARG [...]] [-r PART [...]] [--config PATH]

          -h, --help               Show this help message and exit
          -b, --bump ARG [...]     Bump version parts
          --config PATH            Config file path
          -c, --current            Get the current version
          -r, --reset PART [...]   Reset version parts
          -v, --verbose            Log more details
        '''))
        sys.exit(0)

    config = Config(args.config)

    if args.current:
        print(config.version)
    if args.bump:
        old_version_str = str(config.version)
        config.version.bump(args.bump)
        new_version_str = str(config.version)
        config.save()
        config.update_files(old_version_str, new_version_str)
        print(f'{old_version_str}  >>  {new_version_str}')
    if args.reset:
        old_version_str = str(config.version)
        config.version.reset(args.reset)
        new_version_str = str(config.version)
        config.save()
        config.update_files(old_version_str, new_version_str)
        print(f'{old_version_str}  >>  {new_version_str}')


def _parse_args(args):
    parser = argparse.ArgumentParser(
        prog='myver',
        add_help=False,
    )
    parser.register('action', 'extend', ExtendAction)
    parser.add_argument(
        '-h', '--help',
        action='store_true',
    )
    parser.add_argument(
        '-b', '--bump',
        action='extend',
        nargs='+',
        type=str,
    )
    parser.add_argument(
        '--config',
        default='myver.yml',
        type=str,
    )
    parser.add_argument(
        '-c', '--current',
        action='store_true',
    )
    parser.add_argument(
        '-r', '--reset',
        action='extend',
        nargs='+',
        type=str,
    )

    # Extra logging
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
    )
    parser.add_argument(
        '--debug',
        action='store_true',
    )
    return parser.parse_args(args)


class ExtendAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        items = getattr(namespace, self.dest) or []
        items.extend(values)
        setattr(namespace, self.dest, items)
