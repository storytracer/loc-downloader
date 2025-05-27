import logging
import re
import time
import mimetypes
from typing import List, Optional, Dict, Any, Tuple
from urllib.parse import urlparse, parse_qs
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from requests_ratelimiter import LimiterSession
from pyrate_limiter import Duration, RequestRate, Limiter
from tqdm import tqdm
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type, before_sleep_log

from .models import Item, ItemResponse, SearchResponse, SearchResult, Collection
from .exceptions import LocAPIError, RateLimitError


logger = logging.getLogger(__name__)




class LocAPI:
    BASE_URL = "https://www.loc.gov"
    
    RATE_LIMITS = {
        "newspapers": {
            "per_second": 2,  # 20 per 10 seconds
            "per_minute": 20,
            "burst": 5
        },
        "item": {
            "per_second": 1,  # 10 per 10 seconds
            "per_minute": 200,
            "burst": 10
        },
        "resource": {
            "per_second": 4,  # 40 per 10 seconds
            "per_minute": 200,
            "burst": 20
        },
        "collections": {
            "per_second": 2,  # 20 per 10 seconds
            "per_minute": 80,
            "burst": 10
        }
    }
    
    def __init__(self, max_workers: int = 10):
        self.sessions = {}
        
        # Create rate-limited sessions for each endpoint type
        for endpoint, limits in self.RATE_LIMITS.items():
            session = LimiterSession(
                per_second=limits["per_second"],
                per_minute=limits["per_minute"],
                burst=limits["burst"]
            )
            session.headers.update({
                "User-Agent": "loc-downloader/0.1.0"
            })
            self.sessions[endpoint] = session
            
        # Default session for unknown endpoints
        self.default_session = requests.Session()
        self.default_session.headers.update({
            "User-Agent": "loc-downloader/0.1.0"
        })
            
        self.max_workers = max_workers
        
    def _get_endpoint_type(self, url: str) -> str:
        if "/newspapers/" in url:
            return "newspapers"
        elif "/item/" in url:
            return "item"
        elif "/resource/" in url:
            return "resource"
        elif "/collections/" in url:
            return "collections"
        return "item"  # default
            
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=60),
        retry=retry_if_exception_type(requests.exceptions.RequestException),
        before_sleep=before_sleep_log(logger, logging.WARNING)
    )
    def _make_request(self, url: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        endpoint_type = self._get_endpoint_type(url)
        session = self.sessions.get(endpoint_type, self.default_session)
        
        if params is None:
            params = {}
        
        params.setdefault("fo", "json")
        
        response = session.get(url, params=params, timeout=30)
        
        if response.status_code == 429:
            logger.warning(f"Rate limit hit for {url}, waiting...")
            time.sleep(300)
            raise requests.exceptions.RequestException("Rate limit hit")
            
        response.raise_for_status()
        return response.json()
                
    def parse_url(self, url: str) -> Tuple[str, str]:
        parsed = urlparse(url)
        path = parsed.path
        
        item_match = re.search(r'/item/([^/]+)/?', path)
        if item_match:
            return "item", item_match.group(1)
            
        collection_match = re.search(r'/collections/([^/]+)/?', path)
        if collection_match:
            return "collection", collection_match.group(1)
            
        raise ValueError(f"URL {url} is not a valid item or collection URL")
        
    def get_item(self, item_id: str) -> ItemResponse:
        url = f"{self.BASE_URL}/item/{item_id}/"
        data = self._make_request(url)
        return ItemResponse(**data)
        
    def get_collection_items(self, collection_name: str, 
                           limit: Optional[int] = None) -> List[SearchResult]:
        url = f"{self.BASE_URL}/collections/{collection_name}/"
        
        all_results = []
        page = 1
        per_page = 1000
        
        initial_data = self._make_request(url, params={"c": per_page, "sp": page})
        total_results = initial_data["pagination"]["total"]
        
        if total_results > 100000:
            logger.info(f"Collection has {total_results} items, using date faceting")
            return self._get_collection_with_faceting(collection_name, limit)
            
        with tqdm(total=min(total_results, limit or total_results), desc="Fetching items") as pbar:
            while True:
                params = {
                    "c": per_page,
                    "sp": page,
                    "fa": "digitized:true"
                }
                
                data = self._make_request(url, params=params)
                response = SearchResponse(**data)
                
                for result in response.results:
                    if limit and len(all_results) >= limit:
                        return all_results
                        
                    all_results.append(result)
                    pbar.update(1)
                    
                if response.pagination.next is None:
                    break
                    
                page += 1
                
        return all_results
        
    def _get_collection_with_faceting(self, collection_name: str,
                                    limit: Optional[int] = None) -> List[SearchResult]:
        url = f"{self.BASE_URL}/collections/{collection_name}/"
        
        date_ranges = self._find_optimal_date_ranges(url)
        
        all_results = []
        total_processed = 0
        
        with tqdm(total=limit, desc="Fetching items with date faceting") as pbar:
            for start_year, end_year in date_ranges:
                if limit and total_processed >= limit:
                    break
                    
                page = 1
                per_page = 1000
                
                while True:
                    params = {
                        "c": per_page,
                        "sp": page,
                        "fa": "digitized:true",
                        "dates": f"{start_year}/{end_year}"
                    }
                    
                    data = self._make_request(url, params=params)
                    response = SearchResponse(**data)
                    
                    for result in response.results:
                        if limit and len(all_results) >= limit:
                            return all_results
                            
                        all_results.append(result)
                        pbar.update(1)
                        
                    if response.pagination.next is None:
                        break
                        
                    page += 1
                    
        return all_results
        
    def _find_optimal_date_ranges(self, base_url: str) -> List[Tuple[int, int]]:
        data = self._make_request(base_url, params={"fa": "digitized:true"})
        
        date_facets = None
        for facet in data.get("facets", []):
            if facet.get("name") == "dates":
                date_facets = facet.get("buckets", [])
                break
                
        if not date_facets:
            raise LocAPIError("No date facets found")
            
        ranges = []
        for bucket in date_facets:
            count = bucket.get("count", 0)
            value = bucket.get("value", "")
            
            if count < 100000 and value:
                year_match = re.match(r"(\d{4})/(\d{4})", value)
                if year_match:
                    start_year = int(year_match.group(1))
                    end_year = int(year_match.group(2))
                    ranges.append((start_year, end_year))
            elif count >= 100000 and value:
                year_match = re.match(r"(\d{4})/(\d{4})", value)
                if year_match:
                    start_year = int(year_match.group(1))
                    end_year = int(year_match.group(2))
                    
                    mid_year = (start_year + end_year) // 2
                    ranges.extend([
                        (start_year, mid_year),
                        (mid_year + 1, end_year)
                    ])
                    
        return sorted(ranges)
        
    def download_item_files(self, item_id: str, output_dir: str,
                           mimetype: Optional[str] = None) -> List[str]:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        item_response = self.get_item(item_id)
        
        downloaded_files = []
        files_to_download = []
        
        for resource in item_response.resources:
            for file_group in resource.files:
                for file_info in file_group:
                    if file_info.url:
                        if not mimetype or file_info.mimetype == mimetype:
                            files_to_download.append((file_info.url, file_info.mimetype))
                        
        logger.info(f"Found {len(files_to_download)} files to download")
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {}
            
            for url, file_mimetype in files_to_download:
                future = executor.submit(self._download_file, url, output_path, item_id)
                futures[future] = url
                
            with tqdm(total=len(futures), desc="Downloading files") as pbar:
                for future in as_completed(futures):
                    try:
                        filepath = future.result()
                        if filepath:
                            downloaded_files.append(filepath)
                    except Exception as e:
                        logger.error(f"Failed to download {futures[future]}: {e}")
                    pbar.update(1)
                    
        return downloaded_files
        
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(requests.exceptions.RequestException),
        before_sleep=before_sleep_log(logger, logging.WARNING)
    )
    def _download_file(self, url: str, output_dir: Path, item_id: str) -> Optional[str]:
        session = self.sessions.get("resource", self.default_session)
        
        response = session.get(url, stream=True, timeout=60)
        response.raise_for_status()
        
        filename = self._get_filename_from_url(url, response.headers, item_id)
        filepath = output_dir / filename
        
        with open(filepath, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    
        return str(filepath)
            
    def _get_filename_from_url(self, url: str, headers: Dict[str, str], item_id: str) -> str:
        content_disposition = headers.get("Content-Disposition", "")
        if content_disposition:
            filename_match = re.search(r'filename="([^"]+)"', content_disposition)
            if filename_match:
                return filename_match.group(1)
                
        parsed = urlparse(url)
        path_parts = parsed.path.strip("/").split("/")
        
        if path_parts and path_parts[-1]:
            return path_parts[-1]
            
        # Try to guess extension from mimetype
        ext = mimetypes.guess_extension(headers.get("Content-Type", "").split(";")[0].strip())
        if not ext:
            ext = ""
        return f"{item_id}_{int(time.time())}{ext}"
        
        
    def download_collection_files(self, collection_name: str, output_dir: str,
                                 limit: Optional[int] = None,
                                 mimetype: Optional[str] = None) -> List[str]:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        items = self.get_collection_items(collection_name, limit=limit)
        
        all_downloaded = []
        
        for item in tqdm(items, desc="Processing items"):
            item_id = item.id.split("/")[-2]
            
            try:
                # Get full item data to check for LCCN
                item_data = self.get_item(item_id)
                if item_data.item.number_lccn:
                    item_dir = output_path / item_data.item.number_lccn[0]
                else:
                    item_dir = output_path / item_id
                
                downloaded = self.download_item_files(item_id, str(item_dir), mimetype=mimetype)
                all_downloaded.extend(downloaded)
            except Exception as e:
                logger.error(f"Failed to download files for item {item_id}: {e}")
                
        return all_downloaded
        
    def save_metadata(self, data: Any, output_file: str):
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if isinstance(data, (ItemResponse, SearchResult)):
            data_dict = data.model_dump()
        elif isinstance(data, list) and all(isinstance(item, SearchResult) for item in data):
            data_dict = [item.model_dump() for item in data]
        else:
            data_dict = data
            
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data_dict, f, indent=2, ensure_ascii=False)