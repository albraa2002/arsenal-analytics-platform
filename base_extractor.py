"""
Base extractor class providing HTTP utilities, caching, rate limiting, and retry logic.
All source-specific extractors inherit from this.
"""

import json
import time
import hashlib
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config.config import config
from config.logging_config import get_logger


class BaseExtractor(ABC):
    """Abstract base for all data extractors."""

    def __init__(self, source_name: str, cache_ttl: int = 3600):
        self.source_name = source_name
        self.cache_ttl = cache_ttl
        self.logger = get_logger(f"extractor.{source_name}")
        self.session = self._build_session()

        self.raw_dir = config.paths.raw / source_name.lower()
        self.raw_dir.mkdir(parents=True, exist_ok=True)

    def _build_session(self) -> requests.Session:
        session = requests.Session()
        retries = Retry(
            total=config.MAX_RETRIES,
            backoff_factor=config.BACKOFF_FACTOR,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
        )
        adapter = HTTPAdapter(max_retries=retries)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/json,*/*",
            "Accept-Language": "en-US,en;q=0.9",
        })
        return session

    def _request(self, url: str, params: Optional[Dict] = None) -> requests.Response:
        self.logger.debug(f"GET {url}")
        time.sleep(config.REQUEST_DELAY)
        resp = self.session.get(url, params=params, timeout=30)
        resp.raise_for_status()
        return resp

    def _request_json(self, url: str, params: Optional[Dict] = None) -> Any:
        return self._request(url, params).json()

    def _request_soup(self, url: str, params: Optional[Dict] = None) -> BeautifulSoup:
        return BeautifulSoup(self._request(url, params).text, "html.parser")

    def _cache_path(self, key: str) -> Path:
        h = hashlib.md5(key.encode()).hexdigest()
        return self.raw_dir / f"{h}.json"

    def _read_cache(self, key: str) -> Optional[Any]:
        path = self._cache_path(key)
        if path.exists():
            age = time.time() - path.stat().st_mtime
            if age < self.cache_ttl:
                self.logger.debug(f"Cache HIT for {key[:60]}")
                return json.loads(path.read_text(encoding="utf-8"))
        self.logger.debug(f"Cache MISS for {key[:60]}")
        return None

    def _write_cache(self, key: str, data: Any):
        path = self._cache_path(key)
        path.write_text(json.dumps(data, default=str, ensure_ascii=False), encoding="utf-8")

    def _cached_request_json(self, url: str, params: Optional[Dict] = None) -> Any:
        cache_key = f"{url}:{json.dumps(params or {}, sort_keys=True)}"
        cached = self._read_cache(cache_key)
        if cached is not None:
            return cached
        data = self._request_json(url, params)
        self._write_cache(cache_key, data)
        return data

    def save_dataframe(self, df: pd.DataFrame, name: str, subdir: Optional[str] = None) -> Path:
        dest = self.raw_dir
        if subdir:
            dest = dest / subdir
            dest.mkdir(parents=True, exist_ok=True)
        path = dest / f"{name}.parquet"
        df.to_parquet(path, index=False)
        self.logger.info(f"Saved {len(df)} rows → {path}")
        return path

    @abstractmethod
    def extract(self, **kwargs) -> Dict[str, pd.DataFrame]:
        ...

    def run(self, **kwargs) -> Dict[str, pd.DataFrame]:
        self.logger.info(f"Starting extraction: {self.source_name}")
        result = self.extract(**kwargs)
        self.logger.info(f"Extraction complete: {self.source_name}")
        return result
