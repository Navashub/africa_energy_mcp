"""
Async HTTP client for Africa Energy API.
Features: retry logic, timeout, in-memory caching, exponential backoff.
"""

import httpx
import logging
import asyncio
from typing import Any, Optional
from datetime import datetime, timedelta
from config import API_BASE_URL, API_KEY, REQUEST_TIMEOUT, RETRY_MAX_ATTEMPTS, RETRY_BACKOFF_FACTOR, CACHE_TTL_SECONDS

logger = logging.getLogger(__name__)


class APIError(Exception):
    """Custom exception for API-related errors."""
    pass


class CachedResponse:
    """Wrapper for cached API responses with TTL."""
    def __init__(self, data: Any, ttl_seconds: int):
        self.data = data
        self.created_at = datetime.now()
        self.ttl = timedelta(seconds=ttl_seconds)

    def is_expired(self) -> bool:
        """Check if cached response has expired."""
        return datetime.now() > self.created_at + self.ttl


class APIClient:
    """Async HTTP client with retry logic and caching."""

    def __init__(self):
        self._client: Optional[httpx.AsyncClient] = None
        self._cache: dict[tuple, CachedResponse] = {}
        logger.debug(f"APIClient initialized with base URL: {API_BASE_URL}")

    async def __aenter__(self):
        """Async context manager entry."""
        self._client = httpx.AsyncClient(
            timeout=REQUEST_TIMEOUT,
            headers={"x-rapidapi-key": API_KEY, "Content-Type": "application/json"},
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._client:
            await self._client.aclose()
            self._client = None

    def _get_cache_key(self, endpoint: str, params: dict) -> tuple:
        """Generate a cache key from endpoint and params."""
        # Create a frozenset of params to make them hashable
        params_tuple = frozenset((k, v) for k, v in params.items() if v is not None)
        return (endpoint, params_tuple)

    def _get_from_cache(self, cache_key: tuple) -> Optional[Any]:
        """Retrieve data from cache if valid."""
        if cache_key in self._cache:
            cached = self._cache[cache_key]
            if not cached.is_expired():
                logger.debug(f"Cache hit for {cache_key[0]}")
                return cached.data
            else:
                logger.debug(f"Cache expired for {cache_key[0]}")
                del self._cache[cache_key]
        return None

    def _set_cache(self, cache_key: tuple, data: Any) -> None:
        """Store data in cache."""
        self._cache[cache_key] = CachedResponse(data, CACHE_TTL_SECONDS)
        logger.debug(f"Cached response for {cache_key[0]}")

    async def get(self, endpoint: str, params: Optional[dict] = None) -> Any:
        """
        Make a GET request with retry logic and caching.
        
        Args:
            endpoint: API endpoint path (e.g., '/api/v1/electricity')
            params: Query parameters dict
            
        Returns:
            Parsed JSON response as dict/list
            
        Raises:
            APIError: On all non-transient errors or exhausted retries
        """
        if not self._client:
            raise APIError("APIClient not initialized. Use 'async with APIClient() as client:'")

        params = params or {}
        # Remove None values to avoid sending empty params
        clean_params = {k: v for k, v in params.items() if v is not None}

        # Check cache first
        cache_key = self._get_cache_key(endpoint, clean_params)
        cached_data = self._get_from_cache(cache_key)
        if cached_data is not None:
            return cached_data

        url = f"{API_BASE_URL}{endpoint}"
        last_error: Optional[Exception] = None

        # Retry loop with exponential backoff
        for attempt in range(RETRY_MAX_ATTEMPTS):
            try:
                logger.debug(f"Attempt {attempt + 1}/{RETRY_MAX_ATTEMPTS}: GET {endpoint} with params {clean_params}")
                response = await self._client.get(url, params=clean_params)
                response.raise_for_status()
                data = response.json()
                
                # Cache successful response
                self._set_cache(cache_key, data)
                logger.info(f"API call successful: GET {endpoint}")
                return data

            except httpx.HTTPStatusError as e:
                # Only retry on 5xx errors and timeouts
                if 500 <= e.response.status_code < 600:
                    logger.warning(
                        f"Server error ({e.response.status_code}) on attempt {attempt + 1}/{RETRY_MAX_ATTEMPTS}"
                    )
                    last_error = e
                    if attempt < RETRY_MAX_ATTEMPTS - 1:
                        wait_time = RETRY_BACKOFF_FACTOR ** attempt
                        logger.debug(f"Waiting {wait_time}s before retry...")
                        await asyncio.sleep(wait_time)
                        continue
                else:
                    # Don't retry on 4xx errors
                    logger.error(f"Client error ({e.response.status_code}): {e.response.text}")
                    raise APIError(f"HTTP {e.response.status_code}: {e.response.text}") from e

            except httpx.TimeoutException as e:
                logger.warning(f"Timeout on attempt {attempt + 1}/{RETRY_MAX_ATTEMPTS}")
                last_error = e
                if attempt < RETRY_MAX_ATTEMPTS - 1:
                    wait_time = RETRY_BACKOFF_FACTOR ** attempt
                    logger.debug(f"Waiting {wait_time}s before retry...")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    raise APIError(f"Request timeout after {RETRY_MAX_ATTEMPTS} attempts") from e

            except httpx.RequestError as e:
                logger.error(f"Request error: {str(e)}")
                raise APIError(f"Request failed: {str(e)}") from e

            except Exception as e:
                logger.error(f"Unexpected error: {str(e)}")
                raise APIError(f"Unexpected error: {str(e)}") from e

        # If we exhausted retries on a 5xx error
        if last_error:
            raise APIError(f"Max retries ({RETRY_MAX_ATTEMPTS}) exceeded") from last_error

        raise APIError("Unknown error occurred")

    def clear_cache(self) -> None:
        """Clear the in-memory cache."""
        self._cache.clear()
        logger.info("Cache cleared")
