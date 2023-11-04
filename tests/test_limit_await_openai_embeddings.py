import os
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain_openai_limiter.limit_await_openai_embeddings import LimitAwaitOpenAIEmbeddings
from langchain_openai_limiter.limit_info import reset_limit_info
import numpy as np
import pytest
from .utils import load_env


def calc_similarity(query: np.ndarray, docs: np.ndarray) -> np.ndarray:
    query_norm = np.linalg.norm(query)
    docs_norm = np.linalg.norm(docs, axis=1)
    dot_product = query.dot(docs.T)
    cosine_similarities = dot_product / (query_norm * docs_norm)
    return cosine_similarities


def test_limitawait_openai_embeddings(load_env):
    reset_limit_info()
    api_key = os.environ["OPENAI_API_KEY"]
    embedder = LimitAwaitOpenAIEmbeddings(
        openai_embeddings=OpenAIEmbeddings(
            model="text-embedding-ada-002",
            openai_api_key=api_key,
        )
    )
    docs = np.array(embedder.embed_documents([
        "Markdown is a lightweight markup language",
        "Brainfuck is an esoteric programming language"
    ]))
    query = np.array(embedder.embed_query("What is Markdown?"))
    similarity = calc_similarity(query, docs)
    assert similarity[0] > 0.9
    assert similarity[1] < 0.8


@pytest.mark.asyncio
async def test_limitawait_openai_embeddings_async(load_env):
    reset_limit_info()
    api_key = os.environ["OPENAI_API_KEY"]
    embedder = LimitAwaitOpenAIEmbeddings(
        openai_embeddings=OpenAIEmbeddings(
            model="text-embedding-ada-002",
            openai_api_key=api_key,
        )
    )
    docs = np.array(await embedder.aembed_documents([
        "Markdown is a lightweight markup language",
        "Brainfuck is an esoteric programming language"
    ]))
    query = np.array(await embedder.aembed_query("What is Markdown?"))
    similarity = calc_similarity(query, docs)
    assert similarity[0] > 0.9
    assert similarity[1] < 0.8