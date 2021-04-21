import pytest

from nsist import InputError, split_entry_point

def test_split_entry_point():
    assert split_entry_point('mod:func') == ('mod', 'func')
    assert split_entry_point('mod.submod:func') == ('mod.submod', 'func')

    with pytest.raises(InputError):
        split_entry_point('.\\src\\main:tf2_discord')  # Github issue 205

    with pytest.raises(InputError):
        split_entry_point('mod:1func')  # Identifier can't start with number
