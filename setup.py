from setuptools import setup


NAME = "langchain_openai_limiter"
VERSION = "0.0.1"
DESCRIPTION = """Wrapper for Langchain & OpenAI api calls which use OpenAI headers to deal with TPM & RPM.
Also allow to use multiple keys from different organizations."""
AUTHOR = "Alexander Pozharskii"
AUTHOR_EMAIL = "gaussmake@gmail.com"
PACKAGES = [NAME]
INSTALL_REQUIRES = [
    "aiohttp>=3.8.6",
    "openai>=0.28.1",
    "requests>=2.31.0",
    "langchain>=0.0.329",
    "tiktoken>=0.5.1",
    "transformers>=4.35.0",
]
DEV_REQUIRES = [
    "pytest>=7.4.1",
    "pytest-asyncio>=0.21.1",
    "numpy>=1.26.1"
]


setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    packages=PACKAGES,
    install_requires=INSTALL_REQUIRES,
    extras_require={
        "dev": DEV_REQUIRES,
    }
)