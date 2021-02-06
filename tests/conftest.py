import pytest

from simbump.part import NumericPartConfig, Part, StringPartConfig
from simbump.version import VersionConfig


@pytest.fixture
def dev_config() -> StringPartConfig:
    return StringPartConfig(
        order=6,
        required=False,
        prefix='+',
        value_list=['dev']
    )


@pytest.fixture
def prenum_config(dev_config) -> NumericPartConfig:
    return NumericPartConfig(
        order=5,
        prefix='.',
        start_value=1,
        children={'dev': dev_config}
    )


@pytest.fixture
def pre_config(prenum_config) -> StringPartConfig:
    return StringPartConfig(
        order=4,
        required=False,
        prefix='-',
        children={'prenum': prenum_config},
        value_list=['alpha', 'beta', 'rc']
    )


@pytest.fixture
def micro_config(pre_config, dev_config) -> NumericPartConfig:
    return NumericPartConfig(
        order=3,
        prefix='.',
        children={'dev': dev_config, 'pre': pre_config},
    )


@pytest.fixture
def minor_config(micro_config) -> NumericPartConfig:
    return NumericPartConfig(
        order=2,
        prefix='.',
        children={'micro': micro_config},
    )


@pytest.fixture
def major_config(minor_config) -> NumericPartConfig:
    return NumericPartConfig(
        order=1,
        children={'minor': minor_config},
    )


@pytest.fixture
def version_config(major_config, minor_config, micro_config, pre_config,
                   prenum_config) -> VersionConfig:
    return VersionConfig({
        'major': major_config,
        'minor': minor_config,
        'micro': micro_config,
        'pre': pre_config,
        'prenum': prenum_config,
    })


@pytest.fixture
def part_values() -> dict:
    return {
        'major': 3,
        'minor': 9,
        'micro': 1,
        'pre': None,
        'prenum': None,
    }


@pytest.fixture
def dev(dev_config) -> Part:
    return Part(dev_config, 'dev')


@pytest.fixture
def prenum(prenum_config) -> Part:
    return Part(prenum_config, 1)


@pytest.fixture
def pre(pre_config, prenum) -> Part:
    return Part(pre_config, 'alpha', prenum)


@pytest.fixture
def micro(micro_config) -> Part:
    return Part(micro_config, 1)


@pytest.fixture
def minor(minor_config, micro) -> Part:
    return Part(minor_config, 9, micro)


@pytest.fixture
def major(major_config, minor) -> Part:
    return Part(major_config, 3, minor)
