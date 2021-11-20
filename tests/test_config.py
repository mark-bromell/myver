import pytest

from myver.config import part_from_dict
from myver.part import NumberPart


@pytest.mark.parametrize('part_key, part_dict, expected_part', [
    (
            'major',
            {
                'value': 3,
            },
            NumberPart(key='major', value=3)
    )
])
def test_part_from_dict(part_key, part_dict, expected_part):
    # TODO: better equality checks
    assert part_from_dict(part_key, part_dict) == expected_part
