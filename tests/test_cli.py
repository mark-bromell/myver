import textwrap

import pytest

from myver.cli import cli_entry
from myver.error import MyverError


def test_help_option(semver_config, capsys):
    cli_entry(['--config', str(semver_config.absolute()),
               '--help'])
    captured = capsys.readouterr()
    assert captured.out == textwrap.dedent('''\
    Usage: myver [OPTIONS]
    
    Options:
      -h, --help               Show this help message and exit
      -b, --bump strings       Bump version parts
          --config string      Config file path
      -c, --current [strings]  Get the current version or version parts
      -r, --reset strings      Reset version parts
      -v, --verbose            Log more details\n''')


def test_current_option(semver_config, capsys):
    cli_entry(['--config', str(semver_config.absolute()),
               '--current'])
    captured = capsys.readouterr()
    assert captured.out == '3.9.2-alpha.1\n'


def test_current_option_special_parse(semver_config, capsys):
    cli_entry(['--config', str(semver_config.absolute()),
               '--current', 'major', 'minor'])
    captured = capsys.readouterr()
    assert captured.out == '3.9\n'


def test_current_option_special_parse_bad(semver_config):
    with pytest.raises(MyverError):
        cli_entry(['--config', str(semver_config.absolute()),
                   '--current', 'major', 'wrong'])


def test_bump_option(semver_config, capsys):
    cli_entry(['--config', str(semver_config.absolute()),
               '--bump', 'major'])
    captured = capsys.readouterr()
    assert captured.out == '3.9.2-alpha.1  >>  4.0.0\n'


def test_reset_option(semver_config, capsys):
    cli_entry(['--config', str(semver_config.absolute()),
               '--reset', 'pre'])
    captured = capsys.readouterr()
    assert captured.out == '3.9.2-alpha.1  >>  3.9.2\n'


def test_verbose_option(semver_config, caplog):
    cli_entry(['--config', str(semver_config.absolute()),
               '--verbose'])
    assert 'INFO ' in caplog.text


def test_debug_option(semver_config, caplog):
    cli_entry(['--config', str(semver_config.absolute()),
               '--debug'])
    assert 'DEBUG ' in caplog.text
