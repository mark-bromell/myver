from myver.cli import main


def test_current_option(semver_config, capsys):
    main(['--config', str(semver_config.absolute()), '--current'])
    captured = capsys.readouterr()
    assert captured.out == '3.9.2-alpha.1\n'


def test_bump_option(semver_config, capsys):
    main(['--config', str(semver_config.absolute()),
          '--bump', 'major'])
    captured = capsys.readouterr()
    assert captured.out == '3.9.2-alpha.1  >>  4.0.0\n'


def test_reset_option(semver_config, capsys):

    main(['--config', str(semver_config.absolute()),
          '--reset', 'pre'])
    captured = capsys.readouterr()
    assert captured.out == '3.9.2-alpha.1  >>  3.9.2\n'
