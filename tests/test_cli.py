from myver.__main__ import main


def test_bump_option(semver_config, capsys):
    main(['--config', str(semver_config.absolute()), '--bump', 'major'])
    captured = capsys.readouterr()
    assert captured.out == '3.9.2  >>  4.0.0\n'


def test_current_option(semver_config, capsys):
    main(['--config', str(semver_config.absolute()), '--current'])
    captured = capsys.readouterr()
    assert captured.out == '3.9.2\n'
