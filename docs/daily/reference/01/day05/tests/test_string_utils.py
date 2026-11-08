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
