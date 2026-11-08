import pytest
from src.string_utils import reverse_string, is_palindrome, truncate


def test_review_normal():
    assert reverse_string("python") == "nohtyp"


def test_review_empty():
    assert is_palindrome("") is True


def test_review_invalid_type():
    with pytest.raises(TypeError):
        reverse_string(["a", "b"])


def test_review_suffix_boundary():
    assert truncate("abcdef", 3) == "..."
