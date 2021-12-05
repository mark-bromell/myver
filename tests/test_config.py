import textwrap

import pytest

from myver.config import (
    part_from_dict, version_from_dict, dict_from_yaml, files_from_dict, Config,
)
from myver.error import ConfigError
from myver.files import FileUpdater
from myver.part import NumberPart, IdentifierPart, Part
from myver.version import Version


@pytest.mark.parametrize('part_key, part_dict, expected_part', [
    (
            'my-key',
            {
                'value': 3,
            },
            NumberPart(
                key='my-key',
                value=3,
            ),
    ), (
            'my-key',
            {
                'value': 'rc',
                'prefix': '-',
                'requires': 'prenum',
                'identifier': {
                    'strings': ['alpha', 'beta', 'rc'],
                    'start': 'beta',
                },
            },
            IdentifierPart(
                key='my-key',
                value='rc',
                prefix='-',
                requires='prenum',
                strings=['alpha', 'beta', 'rc'],
                start='beta',
            ),
    ), (
            'my-key',
            {
                'value': None,
                'prefix': '+',
                'number': {
                    'label': 'dev',
                    'label-suffix': '.',
                    'start': 1,
                    'show-start': False,
                },
            },
            NumberPart(
                key='my-key',
                value=None,
                prefix='+',
                label='dev',
                label_suffix='.',
                start=1,
                show_start=False,
            ),
    )
])
def test_part_from_dict(part_key: str, part_dict: dict, expected_part):
    part: Part = part_from_dict(part_key, part_dict)
    assert part.key == part_key
    assert part.value == part_dict['value']
    assert part.prefix == part_dict.get('prefix', '')
    assert part.requires == part_dict.get('requires')

    if part_dict.get('identifier'):
        part: IdentifierPart
        identifier_dict: dict = part_dict['identifier']
        assert part.strings == identifier_dict['strings']
        assert part.start == identifier_dict.get('start', part.strings[0])

    if part_dict.get('number'):
        part: NumberPart
        number_dict: dict = part_dict['number']
        assert part.label == number_dict.get('label', '')
        assert part.label_suffix == number_dict.get('label-suffix', '')
        assert part.start == number_dict.get('start', 0)
        assert part.show_start == number_dict.get('show-start', True)


def test_part_from_dict_type_conflict():
    with pytest.raises(ConfigError):
        part_from_dict('my-key', {
            'value': None,
            'identifier': {
                'strings': ['alpha', 'beta', 'rc'],
            },
            'number': {
                'start': 1,
            },
        })


def test_part_from_dict_missing_required_attribute():
    with pytest.raises(KeyError):
        part_from_dict('my-key', {
            'number': {
                'start': 1,
            },
        })


def test_version_from_dict():
    version_dict = {
        'parts': {
            'major': {
                'value': 3,
                'requires': 'minor',
            },
            'minor': {
                'value': 9,
                'requires': 'patch',
                'prefix': '.',
            },
            'patch': {
                'value': 1,
                'prefix': '.',
            },
        }
    }
    version = version_from_dict(version_dict)
    assert len(version.parts) == 3


def test_version_from_dict_missing_requires_attribute():
    with pytest.raises(ConfigError):
        version_from_dict({'invalid': True})

    with pytest.raises(ConfigError):
        version_from_dict({
            'parts': {
                'major': {
                    'invalid': True,
                },
            }
        })


def test_dict_from_yaml(sample_config):
    config_dict = dict_from_yaml(str(sample_config.absolute()))
    assert config_dict['files'][0]['path']
    assert config_dict['files'][1]['path']
    assert config_dict['files'][1]['patterns']
    assert config_dict['parts']['core']
    assert config_dict['parts']['pre']['identifier']
    assert config_dict['parts']['prenum']['number']


def test_config_load(tmp_path, sample_config):
    config = Config()
    config.path = str(sample_config.absolute())
    files = [
        FileUpdater(path=f'{tmp_path.absolute()}/setup.py'),
        FileUpdater(path=f'{tmp_path.absolute()}/my/path/*.md', patterns=[
            'MyVer {{ version }}',
            'Something.*{{ version }}',
        ])
    ]
    version = Version([
        NumberPart(key='core', value=1),
        IdentifierPart(key='pre', value=None, strings=['alpha', 'beta']),
        NumberPart(key='prenum', value=None, start=1),
    ])
    config.load()
    assert config.files == files
    assert config.version == version


def test_config_load_in_init(tmp_path, sample_config):
    config = Config(path=str(sample_config.absolute()))
    files = [
        FileUpdater(path=f'{tmp_path.absolute()}/setup.py'),
        FileUpdater(path=f'{tmp_path.absolute()}/my/path/*.md', patterns=[
            'MyVer {{ version }}',
            'Something.*{{ version }}',
        ])
    ]
    version = Version([
        NumberPart(key='core', value=1),
        IdentifierPart(key='pre', value=None, strings=['alpha', 'beta']),
        NumberPart(key='prenum', value=None, start=1),
    ])
    assert config.files == files
    assert config.version == version


def test_config_init_load_override(sample_config):
    files = [
        FileUpdater(path='setup.py'),
    ]
    version = Version([
        NumberPart(key='core', value=1),
    ])
    config = Config(
        path=str(sample_config.absolute()),
        files=files,
        version=version,
    )
    assert config.files == files
    assert config.version == version
    config = Config(
        path=str(sample_config.absolute()),
        version=version,
    )
    assert config.files is None
    assert config.version == version
    config = Config(
        path=str(sample_config.absolute()),
        files=files,
    )
    assert config.files == files
    assert config.version is None


def test_config_save(sample_config):
    version = Version([
        NumberPart(key='core', value=2),
        IdentifierPart(key='pre', value='alpha', strings=['alpha', 'beta']),
        NumberPart(key='prenum', value=1, start=1),
    ])
    config = Config(
        path=str(sample_config.absolute()),
        version=version,
    )
    config.save()
    loaded = Config(path=str(sample_config.absolute()))
    assert version == loaded.version


def test_config_save_preserve_formatting(tmp_path, sample_config):
    config = Config(str(sample_config.absolute()))
    config.save()
    with open(sample_config, 'r') as file:
        assert file.read() == textwrap.dedent(f"""\
            # line comment
            files:
                - path: '{tmp_path.absolute()}/setup.py'
                - path: '{tmp_path.absolute()}/my/path/*.md'
                  patterns:
                    - 'MyVer {{{{ version }}}}'
                    - 'Something.*{{{{ version }}}}'
            
            parts:
                core:
                    value: 1
    
                pre:
                    value: null
                    identifier: # in-line comment
                        strings: [ 'alpha', 'beta' ]
    
                prenum:
                    value: null
                    number:
                        start: 1
        """)


def test_version_to_file_bad_config(sample_config):
    version = Version([
        NumberPart(key='core', value=2),
        IdentifierPart(key='pre', value='alpha', strings=['alpha', 'beta']),
    ])
    with pytest.raises(ConfigError):
        config = Config(
            path=str(sample_config.absolute()),
            version=version,
        )
        config.save()


def test_files_from_dict():
    files_dict = {
        'files': [
            {
                'path': 'some/path.md',
                'patterns': ['pattern {{ version }}', 'another {{ version }}']
            },
            {
                'path': 'another/path.md',
            }
        ]
    }
    files = files_from_dict(files_dict)
    assert files[0].path == 'some/path.md'
    assert files[0].patterns == ['pattern {{ version }}',
                                 'another {{ version }}']
    assert files[1].path == 'another/path.md'


def test_files_from_dict_missing_requires_attribute():
    with pytest.raises(ConfigError):
        files_from_dict({'files': [
            {
                'patterns': ['pattern {{ version }}', 'another {{ version }}']
            }
        ]})


def test_update_files(tmp_path, sample_config):
    with open(tmp_path / 'setup.py', 'w') as file:
        file.write('1')

    config = Config(
        path=str(sample_config.absolute()),
    )
    config.update_files('1', '2.2')

    with open(tmp_path / 'setup.py', 'r') as file:
        assert file.readlines()[0] == '2.2'
