from __future__ import annotations

import sys

from myver.cli import main
from logging import getLogger

from myver.error import MyverError

log = getLogger(__name__)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(1)
    except MyverError as e:
        log.error(e.message)
        sys.exit(1)
    except Exception as e:
        log.error('MyVer failed', exc_info=e)
        sys.exit(1)

