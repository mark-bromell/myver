import pytest

from myver.error import ConfigError
from myver.part import NumberPart, IdentifierPart
from myver.version import (
    Version, validate_requires, validate_keys,
    set_relationships,
)


@pytest.fixture
def semver() -> Version:
    parts = [
        NumberPart(
            key='major',
            value=3,
            requires='minor',
        ),
        NumberPart(
            key='minor',
            value=9,
            prefix='.',
            requires='patch',
        ),
        NumberPart(
            key='patch',
            value=2,
            prefix='.',
        ),
        IdentifierPart(
            key='pre',
            value='alpha',
            prefix='-',
            strings=['alpha', 'beta', 'rc'],
        ),
        NumberPart(
            key='prenum',
            value=1,
            prefix='.',
        ),
        NumberPart(
            key='dev',
            value=None,
            prefix='+',
            label='dev',
            label_suffix='.',
            start=1,
            show_start=False,
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
    semver.bump(['minor', 'patch'])
    assert str(semver) == '3.11.0'
    semver.bump(['patch', 'dev'])
    assert str(semver) == '3.11.1+dev'
    semver.bump(['dev'])
    assert str(semver) == '3.11.1+dev.2'


def test_equality():
    parts1 = [
        NumberPart(key='one', value=3),
        NumberPart(key='two', value=9),
    ]
    version1 = Version(parts1)
    parts2 = [
        NumberPart(key='one', value=3),
        NumberPart(key='two', value=9),
    ]
    version2 = Version(parts2)
    assert version1 == version2

    parts2 = [
        NumberPart(key='one', value=3),
        NumberPart(key='two', value=10),
    ]
    version2 = Version(parts2)
    assert not version1 == version2


def test_get_part():
    parts = [
        NumberPart(key='one', value=3),
        NumberPart(key='two', value=9),
    ]
    version = Version(parts)
    assert version.part('one') == parts[0]


def test_get_parts():
    parts = [
        NumberPart(key='one', value=3),
        NumberPart(key='two', value=9),
    ]
    version = Version(parts)
    assert version.parts == parts


def test_get_part_key_error():
    parts = [
        NumberPart(key='one', value=3),
        NumberPart(key='two', value=9),
    ]
    version = Version(parts)
    with pytest.raises(KeyError):
        version.part('three')


def test_validate_requires():
    parts = [
        NumberPart(key='one', value=3),
        NumberPart(key='two', value=9),
        NumberPart(key='three', value=2),
    ]
    validate_requires(parts)


def test_validate_requires_self_reference():
    parts = [
        NumberPart(key='one', value=3, requires='one'),
        NumberPart(key='two', value=9),
        NumberPart(key='three', value=2),
    ]
    with pytest.raises(ConfigError):
        validate_requires(parts)


def test_validate_requires_invalid_key():
    parts = [
        NumberPart(key='one', value=3, requires='bad'),
        NumberPart(key='two', value=9),
        NumberPart(key='three', value=2),
    ]
    with pytest.raises(ConfigError):
        validate_requires(parts)


def test_validate_keys():
    parts = [
        NumberPart(key='one', value=3),
        NumberPart(key='two', value=9),
        NumberPart(key='three', value=2),
    ]
    validate_keys(parts)


def test_validate_keys_duplicate_keys():
    parts = [
        NumberPart(key='one', value=3),
        NumberPart(key='two', value=9),
        NumberPart(key='two', value=2),
    ]
    with pytest.raises(ConfigError):
        validate_keys(parts)


def test_set_relationships():
    parts = [
        NumberPart(key='one', value=3),
        NumberPart(key='two', value=9),
        NumberPart(key='three', value=2),
    ]
    assert parts[0].child is None
    assert parts[1].child is None
    assert parts[2].child is None
    assert parts[0].parent is None
    assert parts[1].parent is None
    assert parts[2].parent is None
    set_relationships(parts)
    assert parts[0].child == parts[1]
    assert parts[1].child == parts[2]
    assert parts[2].child is None
    assert parts[0].parent is None
    assert parts[1].parent == parts[0]
    assert parts[2].parent == parts[1]
