from asyncio import gather
import random
import os
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain_openai_limiter import LimitAwaitOpenAIEmbeddings, ChooseKeyOpenAIEmbeddings
from langchain_openai_limiter.limit_info import reset_limit_info, get_limit_info
import numpy as np
import pytest
from .utils import load_env


def calc_similarity(query: np.ndarray, docs: np.ndarray) -> np.ndarray:
    query_norm = np.linalg.norm(query)
    docs_norm = np.linalg.norm(docs, axis=1)
    dot_product = query.dot(docs.T)
    cosine_similarities = dot_product / (query_norm * docs_norm)
    return cosine_similarities


RANDOM_STATE = 42


def test_choosekey_openai_embeddings(load_env):
    reset_limit_info()
    api_keys = [
        os.environ["OPENAI_API_KEY0"],
        os.environ["OPENAI_API_KEY1"],
    ]
    for key in api_keys:
        assert get_limit_info("text-embedding-ada-002", key) is None
    embedder = ChooseKeyOpenAIEmbeddings(
        LimitAwaitOpenAIEmbeddings(
            openai_embeddings=OpenAIEmbeddings(
                model="text-embedding-ada-002",
            )
        ),
        openai_api_keys=api_keys,
    )
    random.seed(RANDOM_STATE)
    for i in range(4):
        docs = np.array(embedder.embed_documents([
            "Markdown is a lightweight markup language",
            "Brainfuck is an esoteric programming language"
        ]))
        query = np.array(embedder.embed_query("What is Markdown?"))
        similarity = calc_similarity(query, docs)
        assert similarity[0] > 0.9
        assert similarity[1] < 0.8
    for key in api_keys:
        assert get_limit_info("text-embedding-ada-002", key) is not None


@pytest.mark.asyncio
async def test_choosekey_openai_embeddings_async(load_env):
    async def _run_test(embedder):
        docs = np.array(await embedder.aembed_documents([
            "Markdown is a lightweight markup language",
            "Brainfuck is an esoteric programming language"
        ]))
        query = np.array(await embedder.aembed_query("What is Markdown?"))
        similarity = calc_similarity(query, docs)
        assert similarity[0] > 0.9
        assert similarity[1] < 0.8
        
    reset_limit_info()
    api_keys = [
        os.environ["OPENAI_API_KEY0"],
        os.environ["OPENAI_API_KEY1"],
    ]
    for key in api_keys:
        assert get_limit_info("text-embedding-ada-002", key) is None
    embedder = ChooseKeyOpenAIEmbeddings(
        LimitAwaitOpenAIEmbeddings(
            openai_embeddings=OpenAIEmbeddings(
                model="text-embedding-ada-002",
            )
        ),
        openai_api_keys=api_keys,
    )
    random.seed(RANDOM_STATE)
    await gather(
        _run_test(embedder),
        _run_test(embedder),
        _run_test(embedder),
        _run_test(embedder),
    )
    for key in api_keys:
        assert get_limit_info("text-embedding-ada-002", key) is not None