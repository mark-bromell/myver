from myver.part import NumberPart, IdentifierPart
from myver.version import Version


def test_version_str():
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
            strings=['alpha', 'beta', 'rc']
        ),
        NumberPart(
            key='prenum',
            value=1,
            prefix='.',
        ),
    ]

    version = Version(parts)
    assert str(version) == '3.9.2-alpha.1'
