from myver.config import PartConfig, IdentifierConfig
from myver.part import NumberPart, IdentifierPart


def test_part_eq():
    part1 = NumberPart(
        config=PartConfig(
            key='one',
            value=5,
        )
    )
    part2 = NumberPart(
        config=PartConfig(
            key='one',
            value=5,
        ),
    )
    assert part1 == part2


def test_part_is_set():
    part = NumberPart(
        config=PartConfig(
            key='one',
            value=5,
        ),
    )
    assert part.is_set() is True
    part.value = None
    assert part.is_set() is False


def test_part_bump_with_required_child():
    part1 = NumberPart(
        config=PartConfig(
            key='one',
            value=5,
            requires='two',
        ),
    )
    part2 = NumberPart(
        config=PartConfig(
            key='two',
            value=4,
        ),
        parent=part1,
    )
    part3 = NumberPart(
        config=PartConfig(
            key='three',
            value=3,
        ),
        parent=part2,
    )
    part1.bump()
    assert part2.value is part2.start
    assert part3.value is None


def test_part_bump_with_optional_children():
    part1 = NumberPart(
        config=PartConfig(
            key='one',
            value=5,
        ),
    )
    part2 = NumberPart(
        config=PartConfig(
            key='two',
            value=4,
        ),
        parent=part1,
    )
    part3 = NumberPart(
        config=PartConfig(
            key='three',
            value=3,
        ),
        parent=part2,
    )
    part1.bump()
    assert part2.value is None
    assert part3.value is None


def test_identifier_part_bump_from_none():
    part = IdentifierPart(
        config=PartConfig(
            key='one',
            value=None,
            identifier=IdentifierConfig(strings=['alpha', 'beta', 'rc']),
        ),
    )
    part.bump()
    assert part.value == 'alpha'


def test_identifier_part_bump():
    part = IdentifierPart(
        config=PartConfig(
            key='one',
            value='alpha',
            identifier=IdentifierConfig(strings=['alpha', 'beta', 'rc']),
        ),
    )
    part.bump()
    assert part.value == 'beta'


def test_identifier_part_bump_last_one():
    part = IdentifierPart(
        config=PartConfig(
            key='one',
            value='rc',
            identifier=IdentifierConfig(strings=['alpha', 'beta', 'rc']),
        ),
    )
    part.bump()
    assert part.value is None


def test_number_part_bump_from_none():
    part = NumberPart(
        config=PartConfig(
            key='one',
            value=None,
        ),
    )
    part.bump()
    assert part.value == part.start


def test_part_is_required():
    part1 = NumberPart(
        config=PartConfig(
            key='one',
            value=5,
            requires='three',
        ),
    )
    part2 = NumberPart(
        config=PartConfig(
            key='two',
            value=4,
        ),
        parent=part1,
    )
    part3 = NumberPart(
        config=PartConfig(
            key='three',
            value=3,
        ),
        parent=part2,
    )
    assert part3.is_required() is True


def test_part_is_not_required():
    part1 = NumberPart(
        config=PartConfig(
            key='one',
            value=5,
        ),
    )
    part2 = NumberPart(
        config=PartConfig(
            key='two',
            value=4,
        ),
        parent=part1,
    )
    part3 = NumberPart(
        config=PartConfig(
            key='three',
            value=3,
        ),
        parent=part2,
    )
    assert part3.is_required() is False


def test_part_set_child():
    part = NumberPart(
        config=PartConfig(
            key='one',
            value=5,
        ),
    )
    part.child = NumberPart(
        config=PartConfig(
            key='two',
            value=4,
        ),
    )
    assert part.child.key == 'two'
    assert part.child.parent.key == 'one'


def test_part_set_parent():
    part = NumberPart(
        config=PartConfig(
            key='two',
            value=4,
        ),
    )
    part.parent = NumberPart(
        config=PartConfig(
            key='one',
            value=5,
        ),
    )
    assert part.parent.key == 'one'
    assert part.parent.child.key == 'two'


def test_identifier_part_str():
    part = IdentifierPart(
        config=PartConfig(
            key='one',
            value='rc',
            prefix='-',
            identifier=IdentifierConfig(strings=['alpha', 'beta', 'rc']),
        ),
    )
    assert str(part) == '-rc'


def test_number_part_str():
    part = NumberPart(
        config=PartConfig(
            key='one',
            value=5,
            prefix='-',
        ),
    )
    assert str(part) == '-5'
    part.config.number.label = 'dev'
    assert str(part) == '-dev5'
    part.config.number.label_suffix = '.'
    assert str(part) == '-dev.5'
    part.value = 1
    part.config.number.start = part.value
    part.config.number.show_start = False
    assert str(part) == '-dev'
