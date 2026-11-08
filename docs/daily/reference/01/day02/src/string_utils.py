def reverse_string(s):
    if not isinstance(s, str):
        raise TypeError("s 必须是字符串")
    return s[::-1]
