from langchain_openai_limiter.limit_await_chat_openai import LimitAwaitChatOpenAI
from langchain_openai_limiter.choose_key_chat_openai import ChooseKeyChatOpenAI
from langchain_openai_limiter.limit_info import reset_limit_info
from langchain_openai_limiter.capture_headers import attach_session_hooks
from .utils import load_env
from langchain_openai_limiter.limit_info import get_limit_info
import os
import pytest
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
import random
from asyncio import gather


RANDOM_SEED = 42


def test_choose_key_chat_openai_sync(load_env):
    reset_limit_info()
    api_keys = [
        os.environ["OPENAI_API_KEY0"],
        os.environ["OPENAI_API_KEY1"],
    ]
    for key in api_keys:
        assert get_limit_info("gpt-4-0613", key) is None
    chat_model = ChooseKeyChatOpenAI(
        chat_openai=LimitAwaitChatOpenAI(
            chat_openai=ChatOpenAI(
                model_name="gpt-4-0613",
            )
        ),
        openai_api_keys=api_keys
    )
    assert isinstance(chat_model.chat_openai, LimitAwaitChatOpenAI)
    history = [
        SystemMessage(
            content="You are a helpful assistant that translates English to French."
        ),
        HumanMessage(
            content="Translate this sentence from English to French. I love programming."
        ),
    ]
    random.seed(RANDOM_SEED)
    for _ in range(4):
        chat_model.generate([history])
    for key in api_keys:
        assert get_limit_info("gpt-4-0613", key) is not None
    


@pytest.mark.asyncio
async def test_limitawait_chat_openai_async(load_env):
    reset_limit_info()
    api_keys = [
        os.environ["OPENAI_API_KEY0"],
        os.environ["OPENAI_API_KEY1"],
    ]
    for key in api_keys:
        assert get_limit_info("gpt-4-0613", key) is None
    chat_model = ChooseKeyChatOpenAI(
        chat_openai=LimitAwaitChatOpenAI(
            chat_openai=ChatOpenAI(
                model_name="gpt-4-0613",
            )
        ),
        openai_api_keys=api_keys
    )
    assert isinstance(chat_model.chat_openai, LimitAwaitChatOpenAI)
    history = [
        SystemMessage(
            content="You are a helpful assistant that translates English to French."
        ),
        HumanMessage(
            content="Translate this sentence from English to French. I love programming."
        ),
    ]
    random.seed(RANDOM_SEED)
    await gather(
        chat_model.agenerate([history]),
        chat_model.agenerate([history]),
        chat_model.agenerate([history]),
        chat_model.agenerate([history]),
    )
    for key in api_keys:
        assert get_limit_info("gpt-4-0613", key) is not None


def test_choose_key_chat_openai_stream_sync(load_env):
    reset_limit_info()
    api_keys = [
        os.environ["OPENAI_API_KEY0"],
        os.environ["OPENAI_API_KEY1"],
    ]
    for key in api_keys:
        assert get_limit_info("gpt-4-0613", key) is None
    chat_model = ChooseKeyChatOpenAI(
        chat_openai=LimitAwaitChatOpenAI(
            chat_openai=ChatOpenAI(
                model_name="gpt-4-0613",
            )
        ),
        openai_api_keys=api_keys
    )
    assert isinstance(chat_model.chat_openai, LimitAwaitChatOpenAI)
    history = [
        SystemMessage(
            content="You are a helpful assistant that translates English to French."
        ),
        HumanMessage(
            content="Translate this sentence from English to French. I love programming."
        ),
    ]
    random.seed(RANDOM_SEED)
    for _ in range(4):
        for item in chat_model.stream(history):
            pass
    for key in api_keys:
        assert get_limit_info("gpt-4-0613", key) is not None


@pytest.mark.asyncio
async def test_choose_key_chat_openai_astream_async(load_env):
    async def _iter(chat_model, history):
        async for item in chat_model.astream(history):
            pass

    reset_limit_info()
    api_keys = [
        os.environ["OPENAI_API_KEY0"],
        os.environ["OPENAI_API_KEY1"],
    ]
    for key in api_keys:
        assert get_limit_info("gpt-4-0613", key) is None
    chat_model = ChooseKeyChatOpenAI(
        chat_openai=LimitAwaitChatOpenAI(
            chat_openai=ChatOpenAI(
                model_name="gpt-4-0613",
            )
        ),
        openai_api_keys=api_keys
    )
    assert isinstance(chat_model.chat_openai, LimitAwaitChatOpenAI)
    history = [
        SystemMessage(
            content="You are a helpful assistant that translates English to French."
        ),
        HumanMessage(
            content="Translate this sentence from English to French. I love programming."
        ),
    ]
    random.seed(RANDOM_SEED)
    await gather(
        _iter(chat_model, history),
        _iter(chat_model, history),
        _iter(chat_model, history),
        _iter(chat_model, history),
    )
    for key in api_keys:
        assert get_limit_info("gpt-4-0613", key) is not None