import textwrap
from pathlib import Path

import pytest


@pytest.fixture
def sample_config(tmp_path) -> Path:
    path = tmp_path / 'sample.yml'
    config = textwrap.dedent(f"""\
        # line comment
        files:
            - path: '{tmp_path.absolute()}/setup.py'
            - path: '{tmp_path.absolute()}/my/path/*.md'
              patterns:
                - 'MyVer {{{{ version }}}}'
                - 'Something.*{{{{ version }}}}'
            
        parts:
            core:
                value: 1

            pre:
                value: null
                identifier: # in-line comment
                    strings: [ 'alpha', 'beta' ]

            prenum:
                value: null
                number:
                    start: 1
    """)
    with open(path, 'w') as file:
        file.write(config)

    return path


@pytest.fixture
def semver_config(tmp_path) -> Path:
    path = tmp_path / 'semver.yml'
    config = textwrap.dedent("""\
        parts:
            major:
                value: 3
                requires: minor

            minor:
                value: 9
                prefix: '.'
                requires: patch

            patch:
                value: 2
                prefix: '.'

            pre:
                value: alpha
                prefix: '-'
                requires: prenum
                identifier:
                    strings: [ 'alpha', 'beta', 'rc' ]

            prenum:
                value: 1
                prefix: '.'
                number:
                    start: 1

            build:
                value: null
                prefix: '+'
                number:
                    label: 'build'
                    label-suffix: '.'
                    start: 1

            dev:
                value: null
                prefix: '+'
                number:
                    label: 'dev'
                    label-suffix: '.'
                    start: 1
                    show-start: false
    """)
    with open(path, 'w') as file:
        file.write(config)

    return path
