import argparse
import logging
import textwrap

from myver.config import Config
from myver.error import MyverError


def cli_entry(input_args=None):
    """Entry point for the command line utility."""
    args = _parse_args(input_args)

    if args.help:
        print(textwrap.dedent('''\
        Usage: myver [OPTIONS]
        
        Options:
          -h, --help               Show this help message and exit
          -b, --bump strings       Bump version parts
              --config string      Config file path
          -c, --current [strings]  Get the current version or version parts
          -r, --reset strings      Reset version parts
          -v, --verbose            Log more details
        ''').rstrip())
        return

    # Running these before setting up config so that all logging can
    # be captured effectively.
    _handle_verbose(args)
    _handle_debug(args)

    config = Config(args.config)

    # Most things after here will need the config.
    _handle_current(args, config)
    _handle_bump(args, config)
    _handle_reset(args, config)


def _handle_verbose(args):
    if args.verbose:
        logging.root.setLevel(logging.INFO)


def _handle_debug(args):
    if args.debug:
        logging.root.handlers[0].setFormatter(
            logging.Formatter('[%(levelname)s] [%(module)s] %(message)s')
        )
        logging.root.setLevel(logging.DEBUG)


def _handle_current(args, config: Config):
    if args.current is None:
        return

    if len(args.current) == 0:
        print(config.version)
    else:
        try:
            print(config.version.parse(args.current))
        except KeyError as key_error:
            raise MyverError(f'Failed to parse --current option, contains '
                             f'invalid part key `{key_error.args[0]}`')


def _handle_bump(args, config: Config):
    _do_update(config.version.bump, args.bump, config)


def _handle_reset(args, config: Config):
    _do_update(config.version.reset, args.reset, config)


def _do_update(func, arg, config: Config):
    if arg:
        old_version_str = str(config.version)
        func(arg)
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
        action='extend',
        nargs='*',
        type=str,
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
