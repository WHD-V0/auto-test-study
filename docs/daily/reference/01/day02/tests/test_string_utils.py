import pytest
from src.string_utils import reverse_string


def test_reverse_normal():
    assert reverse_string("hello") == "olleh"


def test_reverse_empty():
    assert reverse_string("") == ""


def test_reverse_rejects_list():
    with pytest.raises(TypeError):
        reverse_string(["a", "b"])
