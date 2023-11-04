import os
from dotenv import load_dotenv
import pytest


ROOT_DIR = os.path.dirname(os.path.dirname(__file__))


@pytest.fixture
def load_env():
    env_file = os.path.join(ROOT_DIR, ".env")
    if os.path.exists(env_file):
        load_dotenv(env_file)
