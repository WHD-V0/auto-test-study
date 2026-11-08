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



def truncate(s, max_len, suffix="..."):
    # 所有参数先校验，不能因字符串短就跳过非法参数。
    if not isinstance(s, str):
        raise TypeError("s 必须是字符串")
    if isinstance(max_len, bool) or not isinstance(max_len, int):
        raise TypeError("max_len 必须是非 bool 的整数")
    if max_len < 0:
        raise ValueError("max_len 不能为负数")
    if not isinstance(suffix, str):
        raise TypeError("suffix 必须是字符串")
    if len(s) <= max_len:
        return s
    if max_len <= len(suffix):
        return suffix[:max_len]
    return s[:max_len - len(suffix)] + suffix
