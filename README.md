# Langchain OpenAI limiter

## Goal

By default langchain only do retries if OpenAI queries hit limits. Which could lead to spending many resources in some cases.

Moreover, OpenAI have *very* different tiers for different users.

Like by default for GPT-4 it's something like 10 000 TPM (token per minute) and 1000 RPM (request per minute) - and up to something like 10 000 RPM and 150 000 TPM (in my personal case).

Fortunately, they provide response headers with all the required info, so we don't have to monitor it ourselves.

Unfortunately, neither OpenAI python library nor LangChain built on top of that do not provide easy built-in access to them.

So I made this package

## Installation

You should be able to install it via pip, like
```bash
pip install langchain_openai_limiter
```

## Examples
You could see `example.ipynb` notebook for examples. However:

### Chat completion

```python
# LangChain built-in model
chat_model = ChatOpenAI(
    model_name="gpt-4-0613",
    streaming=True,
)
# Thing which will await for rate/token limits
chat_model_limit_await = LimitAwaitChatOpenAI(
    chat_openai=chat_model,
    limit_await_timeout=60.0,
    limit_await_sleep=0.1,
)
# Thing which will do key rotation
chat_model_key_choose = ChooseKeyChatOpenAI(
    chat_openai=chat_model_limit_await,
    openai_api_keys=[
        os.environ["OPENAI_API_KEY0"],
        os.environ["OPENAI_API_KEY1"],
    ]
)
```
all three things is compatible with LangChain's ChatModel, so:
```python
history = [
    SystemMessage(
        content="You are a helpful assistant that translates English to French."
    ),
    HumanMessage(
        content="Translate this sentence from English to French. I love programming."
    ),
]
print(chat_model_key_choose.invoke(history).content)
```
> J'aime la programmation.

Async and streaming methods implemented as well.

### Embeddings

Pretty often we do not only need chat models - we need embeddings (for RAG, for instance) too:

```python
# LangChain built-in model
embedder_model = OpenAIEmbeddings(
    model="text-embedding-ada-002",
)
# Thing which will await for rate/token limits
embedder_model_limit_await = LimitAwaitOpenAIEmbeddings(
    openai_embeddings=embedder_model,
    limit_await_timeout=60.0,
    limit_await_sleep=0.1,
)
# Thing which will do key rotation
embedder_model_key_choose = ChooseKeyOpenAIEmbeddings(
    openai_embeddings=embedder_model_limit_await,
    openai_api_keys=[
        os.environ["OPENAI_API_KEY0"],
        os.environ["OPENAI_API_KEY1"],
    ]
)
```

```python
docs = embedder_model_key_choose.embed_documents([
    "Markdown is a lightweight markup language",
    "Brainfuck is an esoteric programming language",
])
query = embedder_model_key_choose.embed_query("What is Markdown?")
```

> `-0.01  0.03 -0.00 -0.00  0.00 ...`
> `-0.02  0.00 -0.01 -0.00 -0.00 ...`
> `-0.01  0.01  0.00 -0.01  0.00 ...`
