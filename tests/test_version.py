import pytest

from myver.config import (
    PartConfig, IdentifierConfig, NumberConfig,
    VersionConfig,
)
from myver.part import NumberPart, IdentifierPart
from myver.version import Version


@pytest.fixture
def semver() -> Version:
    part_configs = [
        PartConfig(
            key='major',
            value=3,
            requires='minor',
        ),
        PartConfig(
            key='minor',
            value=9,
            prefix='.',
            requires='patch',
        ),
        PartConfig(
            key='patch',
            value=2,
            prefix='.',
        ),
        PartConfig(
            key='pre',
            value='alpha',
            prefix='-',
            identifier=IdentifierConfig(
                strings=['alpha', 'beta', 'rc'],
            ),
        ),
        PartConfig(
            key='prenum',
            value=1,
            prefix='.',
        ),
        PartConfig(
            key='dev',
            value=None,
            prefix='+',
            number=NumberConfig(
                label='dev',
                label_suffix='.',
                start=1,
                show_start=False,
            ),
        ),
    ]
    version_config = VersionConfig(part_configs)
    return Version(version_config)


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
    part_configs = [
        PartConfig(key='one', value=3),
        PartConfig(key='two', value=9),
    ]
    version = Version(VersionConfig(part_configs))
    assert len(version.parts) == 2
    assert version.parts[0].child.key == part_configs[1].key
    assert version.parts[1].parent.key == part_configs[0].key


def test_get_part():
    part_configs = [
        PartConfig(key='one', value=3),
        PartConfig(key='two', value=9),
    ]
    version = Version(VersionConfig(part_configs))
    assert version.part('one') == NumberPart(part_configs[0])


def test_get_part_key_error():
    part_configs = [
        PartConfig(key='one', value=3),
        PartConfig(key='two', value=9),
    ]
    version = Version(VersionConfig(part_configs))
    with pytest.raises(KeyError):
        version.part('three')
