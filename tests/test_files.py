import textwrap
from pathlib import Path

import pytest

from myver.files import FileUpdater


@pytest.fixture
def updating_file(tmp_path) -> Path:
    path = tmp_path / 'updating_file.md'
    config = textwrap.dedent("""\
        We are currently at version 1.0, although we want to get to 3.8
        soon. We depend on Something 1.0. Support OurProject 1.0!
    """)
    with open(path, 'w') as file:
        file.write(config)

    return path


def test_file_updater_update(updating_file):
    updater = FileUpdater(path=str(updating_file.absolute()))
    updater.update('1.0', '2.2')
    with open(updating_file, 'r') as file:
        assert file.read() == textwrap.dedent("""\
            We are currently at version 2.2, although we want to get to 3.8
            soon. We depend on Something 2.2. Support OurProject 2.2!
        """)


def test_file_updater_update_with_pattern(updating_file):
    updater = FileUpdater(
        path=str(updating_file.absolute()),
        patterns=[
            'We are currently at version {{ version }}',
            'OurP.*{{ version }}',
        ]
    )
    updater.update('1.0', '2.2')
    with open(updating_file, 'r') as file:
        assert file.read() == textwrap.dedent("""\
            We are currently at version 2.2, although we want to get to 3.8
            soon. We depend on Something 1.0. Support OurProject 2.2!
        """)
