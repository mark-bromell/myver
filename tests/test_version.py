from simbump.version import Version


def test_version_part_values(version_config, part_values):
    version = Version(version_config, part_values)
    assert version.part_values == part_values


def test_version_part_values_setter(version_config, part_values):
    version = Version(version_config, part_values)
    part_values['major'] = 4
    version.part_values = part_values
    assert version.part_values == part_values


def test_version_str(version_config, part_values,
                     major, minor, micro, pre, prenum):
    part_values['pre'] = pre.value
    part_values['prenum'] = prenum.value
    version = Version(version_config, part_values)
    expected = '3.9.1-alpha.1'
    actual = str(version)
    assert actual == expected


def test_version_bump_minor_with_children(version_config, part_values,
                                          major, minor, micro, pre, prenum):
    part_values['pre'] = pre.value
    part_values['prenum'] = prenum.value
    version = Version(version_config, part_values)
    version.bump('minor', ['pre'])
    assert str(version) == '3.10.0-alpha.1'


def test_version_bump_minor_without_children(version_config, part_values,
                                             major, minor, micro, pre, prenum):
    part_values['pre'] = pre.value
    part_values['prenum'] = prenum.value
    version = Version(version_config, part_values)
    version.bump('minor')
    assert str(version) == '3.10.0'
