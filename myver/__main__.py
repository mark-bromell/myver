import logging
import sys
from logging import getLogger

from myver.cli import cli_entry
from myver.error import MyverError


def main():
    logging.basicConfig(
        format='[%(levelname)s] %(message)s',
        level=logging.WARNING
    )
    log = getLogger(__name__)
    try:
        cli_entry()
    except KeyboardInterrupt:
        sys.exit(1)
    except MyverError as e:
        log.error(e.message)
        sys.exit(1)
    except Exception as e:
        log.error('MyVer failed', exc_info=e)
        sys.exit(1)


if __name__ == '__main__':
    main()
