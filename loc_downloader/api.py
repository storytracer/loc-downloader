import logging
import re
import time
import mimetypes
from typing import List, Optional, Dict, Any, Tuple, Generator, Union
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
from .url_handler import LocURLHandler


logger = logging.getLogger(__name__)




class LocAPI:
    
    PAGE_SIZE = 1000  # Default number of results per page
    DEEP_PAGING_LIMIT = 100000  # Limit for deep paging collections
    
    RATE_LIMITS = {
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
        self.url_handler = LocURLHandler()
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
        if self.url_handler.is_item_url(url):
            return "item"
        elif self.url_handler.is_resource_url(url):
            return "resource"
        elif self.url_handler.is_collection_url(url):
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
        return self.url_handler.parse_url(url)
        
    def get_item(self, item_id: str) -> ItemResponse:
        url = self.url_handler.get_item_url(item_id)
        data = self._make_request(url)
        return ItemResponse(**data)
        
    def get_collection_items(self, collection_name: str, 
                           limit: Optional[int] = None) -> List[SearchResult]:
        url = self.url_handler.get_collection_url(collection_name)
        
        all_results = []
        page = 1
        per_page = self.PAGE_SIZE
        
        initial_data = self._make_request(url, params={"c": per_page, "sp": page})
        total_results = initial_data["pagination"]["total"]
        
        if total_results > self.DEEP_PAGING_LIMIT:
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
        url = self.url_handler.get_collection_url(collection_name)
        
        date_ranges = self._find_optimal_date_ranges(url)
        
        all_results = []
        total_processed = 0
        
        with tqdm(total=limit, desc="Fetching items with date faceting") as pbar:
            for start_year, end_year in date_ranges:
                if limit and total_processed >= limit:
                    break
                    
                page = 1
                per_page = self.PAGE_SIZE
                
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
            
            if count < self.DEEP_PAGING_LIMIT and value:
                year_match = re.match(r"(\d{4})/(\d{4})", value)
                if year_match:
                    start_year = int(year_match.group(1))
                    end_year = int(year_match.group(2))
                    ranges.append((start_year, end_year))
            elif count >= self.DEEP_PAGING_LIMIT and value:
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
    
    def _check_existing_pages(self, resume_dir: Optional[Path], total_pages: int, year_range: Optional[str] = None) -> List[int]:
        """Check which pages need to be downloaded based on existing files."""
        if not resume_dir or not resume_dir.exists():
            return list(range(1, total_pages + 1))
        
        existing_pages = set()
        for page_file in resume_dir.glob("*.jsonl"):
            try:
                # Handle both simple page numbers and faceted page names
                filename = page_file.stem
                if "_" in filename and year_range:
                    # Faceted page: year_range_0001
                    # Only consider files that match the current year_range
                    if filename.startswith(f"{year_range}_"):
                        page_num = int(filename.split("_")[-1])
                        existing_pages.add(page_num)
                elif "_" not in filename and not year_range:
                    # Simple page number (non-faceted)
                    page_num = int(filename)
                    existing_pages.add(page_num)
            except ValueError:
                continue
        
        pages_to_fetch = [p for p in range(1, total_pages + 1) if p not in existing_pages]
        
        if existing_pages:
            logger.info(f"Found {len(existing_pages)} existing pages, need to fetch {len(pages_to_fetch)} more")
        
        return pages_to_fetch
    
    def _parse_date_facets(self, base_url: str) -> List[Dict[str, Any]]:
        """Parse date facets from the API response."""
        data = self._make_request(base_url, params={"fa": "digitized:true", "fo": "json"})
        
        date_facets = []
        for facet in data.get("facets", []):
            if facet.get("type") == "dates":
                for filter_item in facet.get("filters", []):
                    if filter_item.get("count", 0) > 0:
                        # Extract year range from dates parameter
                        link = filter_item.get("on", "")
                        dates_match = re.search(r'dates=([^&]+)', link)
                        if dates_match:
                            year_range = dates_match.group(1).replace("/", "-")
                        else:
                            year_range = filter_item.get("term", "unknown")
                        
                        date_facets.append({
                            "year_range": year_range,
                            "count": filter_item.get("count", 0),
                            "link": link
                        })
                break
        
        return date_facets
    
    def iter_collection_items(self, collection_name: str, 
                            limit: Optional[int] = None) -> Generator[SearchResult, None, None]:
        """Generator version of get_collection_items for streaming."""
        url = self.url_handler.get_collection_url(collection_name)
        
        page = 1
        per_page = self.PAGE_SIZE
        items_yielded = 0
        
        initial_data = self._make_request(url, params={"c": per_page, "sp": page})
        total_results = initial_data["pagination"]["total"]
        
        if total_results > self.DEEP_PAGING_LIMIT:
            logger.info(f"Collection has {total_results} items, using date faceting")
            yield from self._iter_collection_with_faceting(collection_name, limit)
            return
            
        while True:
            params = {
                "c": per_page,
                "sp": page,
                "fa": "digitized:true"
            }
            
            data = self._make_request(url, params=params)
            response = SearchResponse(**data)
            
            for result in response.results:
                if limit and items_yielded >= limit:
                    return
                    
                yield result
                items_yielded += 1
                
            if response.pagination.next is None:
                break
                
            page += 1
    
    def iter_collection_pages(self, collection_name: str, 
                            limit: Optional[int] = None,
                            resume_dir: Optional[Path] = None) -> Generator[Tuple[int, List[SearchResult]], None, None]:
        """Generator that yields (page_number, results) tuples for collection pages."""
        url = self.url_handler.get_collection_url(collection_name)
        per_page = self.PAGE_SIZE
        
        # Get total results
        initial_data = self._make_request(url, params={"c": 1})
        total_results = initial_data["pagination"]["total"]
        
        if total_results > self.DEEP_PAGING_LIMIT:
            logger.info(f"Collection has {total_results} items, using date faceting")
            yield from self._iter_collection_pages_with_faceting(collection_name, limit, resume_dir)
            return
        
        # Calculate total pages
        total_pages = (total_results + per_page - 1) // per_page
        if limit:
            max_pages = (limit + per_page - 1) // per_page
            total_pages = min(total_pages, max_pages)
        
        # Check existing pages
        pages_to_fetch = self._check_existing_pages(resume_dir, total_pages)
        
        if not pages_to_fetch:
            logger.info("All pages already downloaded")
            return
        
        logger.info(f"Downloading {len(pages_to_fetch)} pages")
        
        # Download missing pages in parallel
        yield from self._fetch_pages_parallel(url, pages_to_fetch, per_page, limit)
    
    def _fetch_pages_parallel(self, url: str, pages_to_fetch: List[int], 
                             per_page: int, limit: Optional[int] = None) -> Generator[Tuple[int, List[SearchResult]], None, None]:
        """Fetch multiple pages in parallel using ThreadPoolExecutor."""
        def fetch_page(page_num: int) -> Tuple[int, List[SearchResult]]:
            params = {
                "c": per_page,
                "sp": page_num,
                "fa": "digitized:true"
            }
            
            data = self._make_request(url, params=params)
            response = SearchResponse(**data)
            return (page_num, response.results)
        
        items_yielded = 0
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all page requests
            future_to_page = {executor.submit(fetch_page, page): page for page in pages_to_fetch}
            
            # Process completed requests as they finish
            for future in as_completed(future_to_page):
                try:
                    page_num, page_results = future.result()
                    
                    # Apply limit if specified
                    if limit:
                        remaining_items = limit - items_yielded
                        if remaining_items <= 0:
                            break
                        if len(page_results) > remaining_items:
                            page_results = page_results[:remaining_items]
                    
                    items_yielded += len(page_results)
                    
                    if page_results:
                        yield (page_num, page_results)
                        
                except Exception as e:
                    page_num = future_to_page[future]
                    logger.error(f"Failed to fetch page {page_num}: {e}")
    
    def _fetch_facet_pages_parallel(self, facet_url: str, pages_to_fetch: List[int], 
                                   per_page: int, year_range: str, 
                                   limit: Optional[int] = None, 
                                   items_yielded: int = 0) -> Generator[Tuple[str, List[SearchResult]], None, None]:
        """Fetch multiple faceted pages in parallel using ThreadPoolExecutor."""
        def fetch_page(page_num: int) -> Tuple[int, List[SearchResult]]:
            params = {
                "c": per_page,
                "sp": page_num,
                "fo": "json"
            }
            
            data = self._make_request(facet_url, params=params)
            response = SearchResponse(**data)
            return (page_num, response.results)
        
        local_items_yielded = 0
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all page requests
            future_to_page = {executor.submit(fetch_page, page): page for page in pages_to_fetch}
            
            # Process completed requests as they finish
            for future in as_completed(future_to_page):
                try:
                    page_num, page_results = future.result()
                    
                    # Apply limit if specified
                    if limit:
                        remaining_items = limit - items_yielded - local_items_yielded
                        if remaining_items <= 0:
                            break
                        if len(page_results) > remaining_items:
                            page_results = page_results[:remaining_items]
                    
                    local_items_yielded += len(page_results)
                    
                    if page_results:
                        # Use combined identifier for faceted pages
                        page_id = f"{year_range}_{str(page_num).zfill(4)}"
                        yield (page_id, page_results)
                        
                except Exception as e:
                    page_num = future_to_page[future]
                    logger.error(f"Failed to fetch faceted page {page_num} for {year_range}: {e}")
    
    def _iter_collection_with_faceting(self, collection_name: str,
                                     limit: Optional[int] = None) -> Generator[SearchResult, None, None]:
        """Generator version of _get_collection_with_faceting for streaming."""
        url = self.url_handler.get_collection_url(collection_name)
        
        date_ranges = self._find_optimal_date_ranges(url)
        items_yielded = 0
        
        for start_year, end_year in date_ranges:
            if limit and items_yielded >= limit:
                break
                
            page = 1
            per_page = self.PAGE_SIZE
            
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
                    if limit and items_yielded >= limit:
                        return
                        
                    yield result
                    items_yielded += 1
                    
                if response.pagination.next is None:
                    break
                    
                page += 1
    
    def _iter_collection_pages_with_faceting(self, collection_name: str,
                                           limit: Optional[int] = None,
                                           resume_dir: Optional[Path] = None) -> Generator[Tuple[Union[int, str], List[SearchResult]], None, None]:
        """Generator version for pages with date faceting."""
        url = self.url_handler.get_collection_url(collection_name)
        per_page = self.PAGE_SIZE
        
        # Get date facets
        date_facets = self._parse_date_facets(url)
        
        # Create output directory structure for date facets
        items_yielded = 0
        
        for facet in date_facets:
            if limit and items_yielded >= limit:
                break
                
            year_range = facet["year_range"]
            facet_url = facet["link"]
            
            # Get total pages for this facet
            facet_data = self._make_request(facet_url, params={"c": 1, "fo": "json"})
            total_pages = (facet_data["pagination"]["total"] + per_page - 1) // per_page
            
            # Check existing pages for this facet (use resume_dir directly without subdirectory)
            pages_to_fetch = self._check_existing_pages(resume_dir, total_pages, year_range) if resume_dir else list(range(1, total_pages + 1))
            
            if not pages_to_fetch:
                # Count existing items for this facet to update items_yielded
                if resume_dir:
                    for page_file in resume_dir.glob(f"{year_range}_*.jsonl"):
                        try:
                            with open(page_file, 'r') as f:
                                items_yielded += sum(1 for _ in f)
                        except Exception:
                            continue
                continue
            
            # Download pages for this facet in parallel
            logger.info(f"Downloading {len(pages_to_fetch)} pages for year range {year_range}")
            
            # Use parallel fetching for this facet
            for page_id, page_results in self._fetch_facet_pages_parallel(
                facet_url, pages_to_fetch, per_page, year_range, limit, items_yielded
            ):
                items_yielded += len(page_results)
                yield (page_id, page_results)
                
                if limit and items_yielded >= limit:
                    return
        
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
        
        response = session.get(url, timeout=60)
        response.raise_for_status()
        
        filename = self._get_filename_from_url(url, response.headers, item_id)
        filepath = output_dir / filename
        
        with open(filepath, "wb") as f:
            f.write(response.content)
                    
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
        
        with open(output_path, "w", encoding="utf-8") as f:
            if isinstance(data, (ItemResponse, SearchResult)):
                # Single item - write as one line
                f.write(json.dumps(data.model_dump(), ensure_ascii=False) + "\n")
            elif isinstance(data, list):
                # Multiple items - write each as a separate line
                for item in data:
                    if isinstance(item, SearchResult):
                        f.write(json.dumps(item.model_dump(), ensure_ascii=False) + "\n")
                    else:
                        f.write(json.dumps(item, ensure_ascii=False) + "\n")
            else:
                # Fallback for other data types
                f.write(json.dumps(data, ensure_ascii=False) + "\n")
    
    def save_metadata_streaming(self, data_generator: Generator[SearchResult, None, None], 
                              output_file: str, total: Optional[int] = None):
        """Save metadata in streaming mode, writing each item as it's received."""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            with tqdm(total=total, desc="Saving metadata") as pbar:
                for item in data_generator:
                    f.write(json.dumps(item.model_dump(), ensure_ascii=False) + "\n")
                    f.flush()  # Ensure data is written immediately
                    pbar.update(1)
    
    def save_metadata_resumable(self, page_generator: Generator[Tuple[Union[int, str], List[SearchResult]], None, None],
                              output_file: str, total: Optional[int] = None):
        """Save metadata with page-based resumability."""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectory for page files
        pages_dir = output_path.parent / output_path.stem
        pages_dir.mkdir(parents=True, exist_ok=True)
        
        # Count existing items for progress bar
        existing_items = self._count_existing_items(pages_dir)
        
        # Save each page to a separate file
        with tqdm(total=total, desc="Downloading metadata", initial=existing_items) as pbar:
            for page_id, page_results in page_generator:
                # Handle both numeric and string page IDs
                if isinstance(page_id, int):
                    page_file = pages_dir / f"{str(page_id).zfill(4)}.jsonl"
                else:
                    # For faceted pages with year ranges
                    page_file = pages_dir / f"{page_id}.jsonl"
                
                # Save page results
                with open(page_file, "w", encoding="utf-8") as f:
                    for item in page_results:
                        f.write(json.dumps(item.model_dump(), ensure_ascii=False) + "\n")
                
                pbar.update(len(page_results))
        
        # Merge all pages into final output file
        logger.info("Merging page files into final output")
        self._merge_page_files(pages_dir, output_path)
    
    def _merge_page_files(self, pages_dir: Path, output_file: Path):
        """Merge individual page files into a single output file."""
        page_files = sorted(pages_dir.glob("*.jsonl"))
        
        if not page_files:
            logger.warning("No page files found to merge")
            return
        
        with open(output_file, "w", encoding="utf-8") as out_f:
            with tqdm(total=len(page_files), desc="Merging pages") as pbar:
                for page_file in page_files:
                    with open(page_file, "r", encoding="utf-8") as in_f:
                        for line in in_f:
                            out_f.write(line)
                    pbar.update(1)
        
        logger.info(f"Merged {len(page_files)} pages into {output_file}")
    
    def _count_existing_items(self, pages_dir: Path) -> int:
        """Count total items in existing page files."""
        if not pages_dir.exists():
            return 0
        
        count = 0
        for page_file in pages_dir.glob("*.jsonl"):
            try:
                with open(page_file, 'r') as f:
                    count += sum(1 for _ in f)
            except Exception:
                continue
        
        return count