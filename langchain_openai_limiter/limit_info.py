"""
Module for limit processing itself
"""
from datetime import datetime
from dataclasses import dataclass
from typing import Dict, Union, List
import time
import asyncio
import threading
import random


@dataclass
class OrganizationLimitInfo:
    """
    Organization-level limit information
    """
    tpm_total: int # Token per minute total (depends on model and tier)
    tpm_remain: int # Token per minute remain (total - used in some time frame)
    rpm_total: int # Request per minute total (depends on model and tier)
    rpm_remain: int # Request per minute remain (total - used in some time frame)
    rpm_reset_time: datetime # When will RPM limit reset
    tpm_reset_time: datetime # When will TPM limit reset

# Type helpers
ApiKey = str
ModelName = str

# Limit info store
_LIMIT_INFO_STORE: Dict[ModelName, Dict[ApiKey, OrganizationLimitInfo]] = {}
# Locks - threading based for synchronyous code, async to use in pair with it for async functions
_SYNC_LIMIT_INFO_LOCK = threading.Lock()
_ASYNC_LIMIT_INFO_LOCK = asyncio.Lock()


def set_limit_info(model_name: ModelName, api_key: ApiKey,
                   limit_info: OrganizationLimitInfo) -> None:
    """
    Update model limit information for given API key
    """
    with _SYNC_LIMIT_INFO_LOCK:
        if model_name not in _LIMIT_INFO_STORE:
            _LIMIT_INFO_STORE[model_name] = {}
        _LIMIT_INFO_STORE[model_name][api_key] = limit_info

async def aset_limit_info(model_name: ModelName, api_key: ApiKey,
                   limit_info: OrganizationLimitInfo) -> None:
    """
    Update model limit information for given API key
    """
    async with _ASYNC_LIMIT_INFO_LOCK:
        set_limit_info(model_name, api_key, limit_info)

def _get_limit_info(model_name: ModelName, api_key: ApiKey) \
    -> Union[OrganizationLimitInfo, None]:
    """
    (INNER VERSION) Extract limit info from storage (and reset TPM and RPM if the time has code)
    :return: OrganizationLimitInfo if limits are known or None if the model was never 
      called with the given API key
    """
    current_time = datetime.now()
    result = _LIMIT_INFO_STORE.get(model_name, {}).get(api_key)
    if result is not None:
        if result.rpm_reset_time < current_time:
            result.rpm_remain = result.rpm_total
        if result.tpm_reset_time < current_time:
            result.tpm_remain = result.tpm_total
    return result

def get_limit_info(model_name: ModelName, api_key: ApiKey) \
    -> Union[OrganizationLimitInfo, None]:
    """
    Extract limit info from storage (and reset TPM and RPM if the time has code)
    :return: OrganizationLimitInfo if limits are known or None if the model was never 
      called with the given API key
    """
    with _SYNC_LIMIT_INFO_LOCK:
        return _get_limit_info(model_name, api_key)

async def aget_limit_info(model_name: ModelName, api_key: ApiKey) \
    -> Union[OrganizationLimitInfo, None]:
    """
    Extract limit info from storage (and reset TPM and RPM if the time has code)
    :return: OrganizationLimitInfo if limits are known or None if the model was never 
      called with the given API key
    """
    async with _ASYNC_LIMIT_INFO_LOCK:
        return get_limit_info(model_name, api_key)

def _get_and_decrease_limit(model_name: ModelName, api_key: ApiKey, token_count: int) -> bool:
    """
    Check if has 1 in RPM limit and not least than `token_count` in TPM limit
    """
    with _SYNC_LIMIT_INFO_LOCK:
        limit_info = _get_limit_info(model_name, api_key)
        run = False
        if limit_info is None or (
                limit_info.rpm_remain > 0
                and
                limit_info.tpm_remain > token_count
        ):
            if limit_info:
                limit_info.rpm_remain -= 1
                limit_info.tpm_remain -= token_count
            run = True
        return run

async def _aget_and_decrease_limit(model_name: ModelName, api_key: ApiKey, token_count: int) \
    -> bool:
    """
    Check if has 1 in RPM limit and not least than `token_count` in TPM limit
    """
    async with _ASYNC_LIMIT_INFO_LOCK:
        return _get_and_decrease_limit(model_name, api_key, token_count)

def wait_for_limit(model_name: ModelName, api_key: ApiKey, token_count: int,
                   limit_await_timeout: float, limit_await_sleep: float) -> None:
    """
    Wait up to `limit_await_timeout` seconds timeout (splitted to `limit_await_sleep` chunks).
    If during this timeout model got `token_count` tokens free TPM and 1 RPM - continue, else fail.
    """
    max_await_count = int(limit_await_timeout / limit_await_sleep)
    for _ in range(max_await_count):
        run = _get_and_decrease_limit(model_name, api_key, token_count)
        if run:
            return
        time.sleep(limit_await_sleep)
    raise TimeoutError()

async def await_for_limit(model_name: ModelName, api_key: ApiKey, token_count: int,
                   limit_await_timeout: float, limit_await_sleep: float) -> None:
    """
    Wait up to `limit_await_timeout` seconds timeout (splitted to `limit_await_sleep` chunks).
    If during this timeout model got `token_count` tokens free TPM and 1 RPM - continue, else fail.
    """
    max_await_count = int(limit_await_timeout / limit_await_sleep)
    for _ in range(max_await_count):
        run = await _aget_and_decrease_limit(model_name, api_key, token_count)
        if run:
            return
        await asyncio.sleep(limit_await_sleep)
    raise TimeoutError()

def choose_key(model_name: ModelName, api_keys: List[ApiKey], token_count: int) -> ApiKey:
    """
    Choose one API key from known.
    """
    with _SYNC_LIMIT_INFO_LOCK:
        assert len(api_keys) > 0, "Should have passed API keys"
        limit_infos = [
            _get_limit_info(model_name, api_key)
            for api_key in api_keys
        ]
        # Check which limits allow us to place corresponding amount of tokens
        clearly_possible_keys = []
        api_key: ApiKey
        for api_key, limit in zip(api_keys, limit_infos):
            if limit is None:
                clearly_possible_keys.append(api_key)
            elif (limit.rpm_remain > 0) and (limit.tpm_remain > token_count):
                clearly_possible_keys.append(api_key)
        # Than choose one of them
        if len(clearly_possible_keys) > 0:
            return random.choice(clearly_possible_keys)
        # Or choose one of default and hope it will soon be available
        return random.choice(api_key)

async def achoose_key(model_name: ModelName, api_keys: List[ApiKey], token_count: int) -> ApiKey:
    """
    Choose one API key from known.
    """
    async with _ASYNC_LIMIT_INFO_LOCK:
        return choose_key(model_name, api_keys, token_count)

def reset_limit_info() -> None:
    """
    Reset collected limit info for testing purpose
    """
    _LIMIT_INFO_STORE.clear()
