import pytest
from src.string_utils import reverse_string


def test_reverse_normal():
    assert reverse_string("hello") == "olleh"


def test_reverse_empty():
    assert reverse_string("") == ""


def test_reverse_rejects_list():
    with pytest.raises(TypeError):
        reverse_string(["a", "b"])

from src.string_utils import is_palindrome, count_vowels


@pytest.mark.parametrize("text,expected", [
    ("Never odd or even", True), ("hello", False), ("", True), ("Abba", True),
], ids=["spaces-case", "not-palindrome", "empty", "mixed-case"])
def test_palindrome(text, expected):
    assert is_palindrome(text) is expected


@pytest.mark.parametrize("text,expected", [("AEiou", 5), ("rhythm", 0), ("", 0)],
                         ids=["all-vowels", "no-vowels", "empty"])
def test_count_vowels(text, expected):
    assert count_vowels(text) == expected


@pytest.mark.parametrize("function", [is_palindrome, count_vowels],
                         ids=["palindrome", "vowels"])
def test_text_functions_reject_non_string(function):
    with pytest.raises(TypeError):
        function(123)

from src.string_utils import truncate


@pytest.mark.parametrize("text,limit,expected", [
    ("hello world", 8, "hello..."), ("hello world", 0, ""),
    ("hello world", 2, ".."), ("hello world", 3, "..."),
    ("hello world", 4, "h..."), ("hello", 5, "hello"), ("hello", 10, "hello"),
], ids=["normal", "zero", "below-suffix", "equal-suffix", "above-suffix", "exact", "no-cut"])
def test_truncate_boundaries(text, limit, expected):
    result = truncate(text, limit)
    assert result == expected
    assert len(result) <= limit


@pytest.mark.parametrize("limit", [True, 2.5, "8"], ids=["bool", "float", "string"])
def test_truncate_invalid_limit_type(limit):
    with pytest.raises(TypeError):
        truncate("hello", limit)


def test_truncate_negative_limit():
    with pytest.raises(ValueError):
        truncate("hello", -1)


def test_truncate_invalid_text():
    with pytest.raises(TypeError):
        truncate(123, 8)


def test_truncate_validates_suffix_before_no_cut():
    with pytest.raises(TypeError):
        truncate("hi", 10, suffix=None)


def test_truncate_custom_suffix():
    assert truncate("abcdef", 4, suffix="~") == "abc~"
