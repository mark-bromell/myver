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
