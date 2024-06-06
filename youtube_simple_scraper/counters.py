import re

import regex


def comment_counter_to_int(c: str) -> int:
    """
    Convert comment counter string to integer.

    :param c: Comment counter string.
    :return: Converted integer value.

    Example:
    >>> comment_counter_to_int("12 Views")
    12
    >>> comment_counter_to_int("1K Views")
    1000
    >>> comment_counter_to_int("1.2K Views")
    1200
    >>> comment_counter_to_int("12.3K Views")
    12300
    >>> comment_counter_to_int("123.4K Views")
    123400
    >>> comment_counter_to_int("123K Views")
    123000
    >>> comment_counter_to_int("1.23K Views")
    1230
    >>> comment_counter_to_int("1.234M Views")
    1234000
    >>> comment_counter_to_int("12M Likes")
    12000000
    >>> comment_counter_to_int("12.34M Likes")
    12340000
    """
    try:
        c = c.upper()
        r = re.compile(r'(?P<number>[\d.,]+)\s*(?P<mult>[MK])?.*')
        match = r.match(c)
        if not match:
            return 0
        number = match.group('number')
        mult_char = match.group('mult')
        mult = 1
        if mult_char == 'K':
            mult = 1000
        elif mult_char == 'M':
            mult = 1000000
        else:
            number = number.replace(',', '').replace('.', '')
        return int(float(number) * mult)
    except:
        return 0
