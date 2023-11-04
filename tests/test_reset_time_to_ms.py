from langchain_openai_limiter.reset_time_parser import reset_time_to_ms


def test_reset_time_to_ms():
    time = "10s2ms"
    assert reset_time_to_ms(time) == 10002