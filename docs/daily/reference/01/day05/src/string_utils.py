def reverse_string(s):
    if not isinstance(s, str):
        raise TypeError("s 必须是字符串")
    return s[::-1]



def is_palindrome(s):
    if not isinstance(s, str):
        raise TypeError("s 必须是字符串")
    normalized = s.lower().replace(" ", "")
    return normalized == normalized[::-1]


def count_vowels(s):
    if not isinstance(s, str):
        raise TypeError("s 必须是字符串")
    return sum(char in "aeiou" for char in s.lower())
