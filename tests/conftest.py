import pytest

from simbump.part import NumericPartConfig, Part, StringPartConfig
from simbump.version import VersionConfig


@pytest.fixture
def prenum_config() -> NumericPartConfig:
    return NumericPartConfig(
        order=5,
        required=True,
        prefix='.',
        start_value=1
    )


@pytest.fixture
def pre_config() -> StringPartConfig:
    return StringPartConfig(
        order=4,
        required=False,
        prefix='-',
        value_list=['alpha', 'beta', 'rc']
    )


@pytest.fixture
def micro_config() -> NumericPartConfig:
    return NumericPartConfig(
        order=3,
        required=True,
        prefix='.',
    )


@pytest.fixture
def minor_config(micro_config) -> NumericPartConfig:
    return NumericPartConfig(
        order=2,
        required=True,
        prefix='.',
        children=[micro_config],
    )


@pytest.fixture
def major_config(minor_config) -> NumericPartConfig:
    return NumericPartConfig(
        order=1,
        children=[minor_config],
    )


@pytest.fixture
def version_config(major_config, minor_config, micro_config) -> VersionConfig:
    return VersionConfig({
        'major': major_config,
        'minor': minor_config,
        'micro': micro_config,
    })


@pytest.fixture
def part_values() -> dict:
    return {
        'major': 3,
        'minor': 9,
        'micro': 1,
    }


@pytest.fixture
def micro(micro_config) -> Part:
    return Part(micro_config, 1)


@pytest.fixture
def minor(minor_config, micro) -> Part:
    return Part(minor_config, 9, micro)


@pytest.fixture
def major(major_config, minor) -> Part:
    return Part(major_config, 3, minor)


@pytest.fixture
def part_list(major, minor, micro) -> list[Part]:
    return [major, minor, micro]
