import pytest

from myver.error import KeyConflictError
from myver.part import NumberPart, IdentifierPart
from myver.version import Version


@pytest.fixture
def semver() -> Version:
    parts = [
        NumberPart(key='major', value=3, requires='minor'),
        NumberPart(key='minor', value=9, prefix='.', requires='patch'),
        NumberPart(key='patch', value=2, prefix='.'),
        IdentifierPart(
            key='pre', value='alpha', prefix='-',
            strings=['alpha', 'beta', 'rc']
        ),
        NumberPart(key='prenum', value=1, prefix='.'),
        NumberPart(
            key='dev', value=None, prefix='+', label='dev',
            label_suffix='.', start=1, show_start=False
        ),
    ]
    return Version(parts)


def test_version_str(semver):
    assert str(semver) == '3.9.2-alpha.1'


def test_version_bump(semver):
    semver.bump(['prenum'])
    assert str(semver) == '3.9.2-alpha.2'
    semver.bump(['minor'])
    assert str(semver) == '3.10.0'
    semver.bump(['patch', 'dev'])
    assert str(semver) == '3.10.1+dev'
    semver.bump(['dev'])
    assert str(semver) == '3.10.1+dev.2'


def test_set_parts():
    parts = [
        NumberPart(key='one', value=3),
        NumberPart(key='two', value=9),
    ]
    version = Version()
    version.parts = parts
    assert len(version.parts) == 2
    assert version.parts[0].child.key == parts[1].key
    assert version.parts[1].parent.key == parts[0].key


def test_set_parts_key_conflict():
    parts = [
        NumberPart(key='one', value=3),
        NumberPart(key='one', value=9),
    ]
    with pytest.raises(KeyConflictError):
        Version(parts)
    with pytest.raises(KeyConflictError):
        version = Version()
        version.parts = parts


def test_get_part():
    parts = [
        NumberPart(key='one', value=3),
        NumberPart(key='two', value=9),
    ]
    version = Version(parts)
    assert version.part('one') == NumberPart(key='one', value=3)


def test_get_part_key_error():
    parts = [
        NumberPart(key='one', value=3),
        NumberPart(key='two', value=9),
    ]
    version = Version(parts)
    with pytest.raises(KeyError):
        version.part('three')
