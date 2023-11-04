"""
Module for parsing OpenAI header-mentioned response times, like
`0s100ms`, `3s10ms`, `1m` and so on.
"""
import re


_RATIO = {
    "ms": 1,
    "s": 1000,
    "m": 60 * 1000,
    "h": 60 * 60 * 1000,
    "d": 24 * 60 * 60 * 1000,
}


def reset_time_to_ms(reset_time: str) -> int:
    """
    Convert OpenAI reset time to milisecond count.
    :param reset_time: reset time, like `0s100ms`, `3s10ms`, `1m` and so on.
    :return: Milliseconds amount.
    """
    delimiters = r'(d|h|ms|m|s)'
    parts = [
        part
        for part in re.split(delimiters, reset_time)
        if part
    ]
    assert len(parts) % 2 == 0
    result = 0
    for i in range(len(parts) // 2):
        number = int(parts[i * 2])
        number_type = parts[i * 2 + 1]
        result += number * _RATIO[number_type]
    return result
