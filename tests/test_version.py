from simbump.version import Version


def test_version_parts(version_config, part_values, part_list):
    version = Version(version_config, part_values)
    expected = part_list
    actual = version.parts
    assert actual == expected


def test_version_str(version_config, part_values, part_list):
    version = Version(version_config, part_values)
    expected = '3.9.1'
    actual = str(version)
    assert actual == expected
