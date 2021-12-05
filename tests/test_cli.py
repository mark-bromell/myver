import textwrap

from myver.cli import cli_entry


def test_help_option(semver_config, capsys):
    cli_entry(['--config', str(semver_config.absolute()),
               '--help'])
    captured = capsys.readouterr()
    assert captured.out == textwrap.dedent('''\
    usage: myver [-h] [-c] [-b ARG [...]] [-r PART [...]] [--config PATH]

      -h, --help               Show this help message and exit
      -b, --bump ARG [...]     Bump version parts
      --config PATH            Config file path
      -c, --current            Get the current version
      -r, --reset PART [...]   Reset version parts
      -v, --verbose            Log more details\n''')


def test_current_option(semver_config, capsys):
    cli_entry(['--config', str(semver_config.absolute()), '--current'])
    captured = capsys.readouterr()
    assert captured.out == '3.9.2-alpha.1\n'


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
