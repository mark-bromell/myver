import pytest

from myver.error import ConfigError
from myver.part import NumberPart, IdentifierPart


def test_part_eq():
    part1 = NumberPart(
        key='one',
        value=5)
    part2 = NumberPart(
        key='one',
        value=5)
    assert part1 == part2


def test_part_is_set():
    part = NumberPart(
        key='one',
        value=5)
    assert part.is_set() is True
    part.value = None
    assert part.is_set() is False


def test_prefix_setter():
    part = NumberPart(
        key='one',
        value=5,
        prefix='-')
    assert str(part) == '-5'
    part.prefix = '+'
    assert str(part) == '+5'


def test_part_bump_with_required_child():
    part1 = NumberPart(
        key='one',
        value=5,
        requires='two')
    part2 = NumberPart(
        key='two',
        value=4,
        parent=part1)
    part3 = NumberPart(
        key='three',
        value=3,
        parent=part2)
    part1.bump()
    assert part2.value is part2.start
    assert part3.value is None


def test_part_bump_with_optional_children():
    part1 = NumberPart(
        key='one',
        value=5)
    part2 = NumberPart(
        key='two',
        value=4,
        parent=part1)
    part3 = NumberPart(
        key='three',
        value=3,
        parent=part2)
    part1.bump()
    assert part2.value is None
    assert part3.value is None


def test_identifier_part_bump_from_none():
    part = IdentifierPart(
        key='one',
        value=None,
        strings=['alpha', 'beta', 'rc'])
    part.bump()
    assert part.value == 'alpha'


def test_identifier_part_bump():
    part = IdentifierPart(
        key='one',
        value='alpha',
        strings=['alpha', 'beta', 'rc'])
    part.bump()
    assert part.value == 'beta'


def test_identifier_part_bump_last_one():
    part = IdentifierPart(
        key='one',
        value='rc',
        strings=['alpha', 'beta', 'rc'])
    part.bump()
    assert part.value is None


def test_number_part_bump_from_none():
    part = NumberPart(
        key='one',
        value=None)
    part.bump()
    assert part.value == part.start


def test_part_is_required():
    part1 = NumberPart(
        key='one',
        value=5,
        requires='three')
    part2 = NumberPart(
        key='two',
        value=4,
        parent=part1)
    part3 = NumberPart(
        key='three',
        value=3,
        parent=part2)
    assert part3.is_required() is True


def test_part_is_not_required():
    part1 = NumberPart(
        key='one',
        value=5)
    part2 = NumberPart(
        key='two',
        value=4,
        parent=part1)
    part3 = NumberPart(
        key='three',
        value=3,
        parent=part2)
    assert part3.is_required() is False


def test_part_set_child():
    part = NumberPart(
        key='one',
        value=5)
    part.child = NumberPart(
        key='two',
        value=4)
    assert part.child.key == 'two'
    assert part.child.parent.key == 'one'


def test_part_set_parent():
    part = NumberPart(
        key='two',
        value=4)
    part.parent = NumberPart(
        key='one',
        value=5)
    assert part.parent.key == 'one'
    assert part.parent.child.key == 'two'


def test_identifier_part_str():
    part = IdentifierPart(
        key='one',
        value='rc',
        prefix='-',
        strings=['alpha', 'beta', 'rc'])
    assert str(part) == '-rc'


def test_identifier_set_bad_start():
    part = IdentifierPart(
        key='one',
        value=None,
        strings=['alpha', 'beta', 'rc'])
    with pytest.raises(ConfigError):
        part.start = 'bad'

    with pytest.raises(ConfigError):
        IdentifierPart(
            key='one',
            value=None,
            strings=['alpha', 'beta', 'rc'],
            start='bad')


def test_identifier_set_empty_strings():
    part = IdentifierPart(
        key='one',
        value=None,
        strings=['alpha', 'beta', 'rc'])
    with pytest.raises(ConfigError):
        part.strings = []

    with pytest.raises(ConfigError):
        IdentifierPart(
            key='one',
            value=None,
            strings=[])


def test_number_part_str():
    part = NumberPart(
        key='one',
        value=5,
        prefix='-')
    assert str(part) == '-5'
    part.label = 'dev'
    assert str(part) == '-dev5'
    part.label_suffix = '.'
    assert str(part) == '-dev.5'
    part.value = 1
    part.start = part.value
    part.show_start = False
    assert str(part) == '-dev'


def test_number_set_string_start():
    part = NumberPart(
        key='one',
        value=None)
    with pytest.raises(ConfigError):
        part.start = 'bad'

    with pytest.raises(ConfigError):
        NumberPart(
            key='one',
            value=None,
            start='bad')  # noqa


def test_number_set_negative_start():
    part = NumberPart(
        key='one',
        value=None)
    with pytest.raises(ConfigError):
        part.start = -1

    with pytest.raises(ConfigError):
        NumberPart(
            key='one',
            value=None,
            start=-1)
