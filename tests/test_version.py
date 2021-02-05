import pytest

from simbump.part import ChildConfig, Part, PartConfig
from simbump.version import Version, VersionConfig


@pytest.fixture
def micro_config():
    return ChildConfig(3, required=True, prefix='.')


@pytest.fixture
def minor_config(micro_config):
    return ChildConfig(2, required=True, prefix='.', children=[micro_config])


@pytest.fixture
def major_config(minor_config):
    return PartConfig(1, children=[minor_config])


@pytest.fixture
def version_config(major_config, minor_config, micro_config):
    return VersionConfig({
        'major': major_config,
        'minor': minor_config,
        'micro': micro_config,
    })


@pytest.fixture
def part_values():
    return {
        'major': 3,
        'minor': 9,
        'micro': 1,
    }


@pytest.fixture
def part_list(major_config, minor_config, micro_config):
    micro = Part(micro_config, 1)
    minor = Part(minor_config, 9, micro)
    major = Part(major_config, 3, minor)

    return [major, minor, micro]


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
