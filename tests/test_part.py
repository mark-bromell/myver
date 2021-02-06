def test_part_set_child(major, minor, micro):
    part_dict = {
        'major': major,
        'minor': minor,
        'micro': micro,
    }
    major.child = None
    assert major.set_child(part_dict) is True
    assert major.child == minor  # noqa


def test_part_set_child_no_part_dict(major):
    major.child = None
    assert major.set_child({}) is False
    assert major.child is None


def test_part_set_child_already_set(major, minor):
    assert major.set_child({}) is False
    assert major.set_child({'minor': minor}) is True


def test_child_key(major):
    assert major.child_key == 'minor'


def test_child_key_none(prenum):
    assert prenum.child_key is None


def test_child_key_multiple_children(micro, pre):
    micro.child = pre
    assert micro.child_key == 'pre'


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


def test_numeric_reset_with_child_parts(major, pre):
    # should be 'beta' now.
    pre.bump()
    major.child.child.child = pre
    major.reset(child_parts=['pre'])
    assert major.value == '0'
    # minor
    assert major.child.value == '0'
    # micro
    assert major.child.child.value == '0'
    # pre
    assert major.child.child.child.value == 'alpha'
    # prenum
    assert major.child.child.child.child.value == '1'


def test_numeric_reset_without_child_parts(major, pre):
    major.child.child.child = pre
    major.reset()
    assert major.value == '0'
    # minor
    assert major.child.value == '0'
    # micro
    assert major.child.child.value == '0'
    # pre
    assert major.child.child.child is None


def test_numeric_bump_with_child_parts(major, pre):
    # should be 'beta' now.
    pre.bump()
    major.child.child.child = pre
    major.bump(child_parts=['pre'])
    assert major.value == '4'
    # minor
    assert major.child.value == '0'
    # micro
    assert major.child.child.value == '0'
    # pre
    assert major.child.child.child.value == 'alpha'
    # prenum
    assert major.child.child.child.child.value == '1'


def test_numeric_bump_without_child_parts(major, pre):
    major.child.child.child = pre
    major.bump()
    assert major.value == '4'
    # minor
    assert major.child.value == '0'
    # micro
    assert major.child.child.value == '0'
    # pre
    assert major.child.child.child is None
