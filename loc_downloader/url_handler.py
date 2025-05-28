import re
from typing import Tuple, Dict, Optional, Any
from urllib.parse import urlparse, urljoin


class LocURLHandler:
    """Handles all URL operations for the Library of Congress API."""
    
    BASE_URL = "https://www.loc.gov"
    
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or self.BASE_URL
    
    def parse_url(self, url: str) -> Tuple[str, str]:
        """Parse a LoC URL to determine its type and identifier.
        
        Args:
            url: The LoC URL to parse
            
        Returns:
            Tuple of (url_type, identifier) where url_type is 'item' or 'collection'
            
        Raises:
            ValueError: If the URL is not a valid LoC URL
        """
        parsed = urlparse(url)
        path = parsed.path
        
        # Check for item URL
        item_match = re.search(r'/item/([^/]+)/?', path)
        if item_match:
            return 'item', item_match.group(1)
        
        # Check for collection URL
        collection_match = re.search(r'/collections/([^/]+)/?', path)
        if collection_match:
            return 'collection', collection_match.group(1)
        
        raise ValueError(f"Invalid LoC URL: {url}")
    
    def get_item_url(self, item_id: str, format: str = "json") -> str:
        """Construct URL for an item endpoint.
        
        Args:
            item_id: The item identifier
            format: Response format (json or yaml)
            
        Returns:
            The constructed URL
        """
        return f"{self.base_url}/item/{item_id}/?fo={format}"
    
    def get_collection_url(self, collection_name: str) -> str:
        """Construct URL for a collection endpoint.
        
        Args:
            collection_name: The collection identifier
            
        Returns:
            The constructed URL
        """
        return f"{self.base_url}/collections/{collection_name}/"
    
    def get_resource_url(self, resource_url: str) -> str:
        """Construct full URL for a resource.
        
        Args:
            resource_url: The resource URL (may be relative or absolute)
            
        Returns:
            The full resource URL
        """
        if resource_url.startswith('http'):
            return resource_url
        return urljoin(self.base_url, resource_url)
    
    def is_item_url(self, url: str) -> bool:
        """Check if URL is for an item endpoint.
        
        Args:
            url: The URL to check
            
        Returns:
            True if this is an item URL
        """
        return "/item/" in url
    
    def is_collection_url(self, url: str) -> bool:
        """Check if URL is for a collection endpoint.
        
        Args:
            url: The URL to check
            
        Returns:
            True if this is a collection URL
        """
        return "/collections/" in url
    
    def is_resource_url(self, url: str) -> bool:
        """Check if URL is for a resource endpoint.
        
        Args:
            url: The URL to check
            
        Returns:
            True if this is a resource URL
        """
        return "/resources/" in url
    
    def add_params_to_url(self, url: str, params: Dict[str, Any]) -> str:
        """Add query parameters to a URL.
        
        Args:
            url: The base URL
            params: Dictionary of query parameters
            
        Returns:
            URL with query parameters added
        """
        if not params:
            return url
        
        # Simple implementation - could be enhanced with proper URL parsing
        param_str = "&".join(f"{k}={v}" for k, v in params.items() if v is not None)
        separator = "&" if "?" in url else "?"
        return f"{url}{separator}{param_str}"