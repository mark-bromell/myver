def test_part_set_child(major, minor, part_list):
    major.child = None
    assert major.set_child(part_list) is True
    assert major.child == minor  # noqa


def test_part_set_child_no_child(major):
    major.child = None
    assert major.set_child([]) is False
    assert major.child is None


def test_part_str(major, minor, micro):
    assert str(major) == '3'
    major.config.prefix = '-'
    major.config.suffix = '+'
    assert str(major) == '-3+'
    assert str(minor) == '.9'
    assert str(micro) == '.1'


def test_numeric_part_config_next(major_config):
    expected = str(5)
    actual = major_config.next_value(current_value=str(4))
    assert actual == expected


def test_string_part_config_next(pre_config):
    expected = 'beta'
    actual = pre_config.next_value(current_value='alpha')
    assert actual == expected


def test_string_part_config_next_end(pre_config):
    actual = pre_config.next_value(current_value='rc')
    assert actual is None


def test_numeric_part_config_start_value_default(minor_config):
    expected = str(0)
    actual = minor_config.start_value
    assert actual == expected


def test_numeric_part_config_start_value_custom_start(prenum_config):
    expected = str(1)
    actual = prenum_config.start_value
    assert actual == expected


def test_string_part_config_start_value(pre_config):
    expected = 'alpha'
    actual = pre_config.start_value
    assert actual == expected
