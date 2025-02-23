import requests
import os
from datetime import datetime
from typing import List, Dict, Optional
from urllib.parse import urlencode

class UnsplashPhotoSearch:
    def __init__(self, access_key: str = None):
        """
        Initialize Unsplash client with access key
        Args:
            access_key: Unsplash API access key. If None, will try to get from UNSPLASH_ACCESS_KEY env var
        """
        self.access_key = access_key or os.getenv("UNSPLASH_ACCESS_KEY")
        if not self.access_key:
            raise ValueError("Unsplash access key is required")
        
        self.base_url = "https://api.unsplash.com"
        # Headers-based authentication
        self.headers = {
            "Authorization": f"Client-ID {self.access_key}"
        }

    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """
        Make authenticated request to Unsplash API
        Supports both header-based and query parameter authentication
        """
        try:
            # Add client_id to query parameters as fallback authentication
            params = params or {}
            params["client_id"] = self.access_key
            
            response = requests.get(
                endpoint,
                headers=self.headers,
                params=params
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Error making request to Unsplash: {e}")
            return None

    def search_photos(self, query: str, page: int = 1, per_page: int = 1) -> Optional[str]:
        """
        Search Unsplash photos by query/title and return the first photo URL
        
        Args:
            query: Search query/title
            page: Page number (default: 1) 
            per_page: Number of results per page (default: 1)
        
        Returns:
            URL of the first matching photo or None if no results
        """
        endpoint = f"{self.base_url}/search/photos"
        params = {
            "query": query,
            "page": page,
            "per_page": per_page
        }
        
        results = self._make_request(endpoint, params)
        if results and results.get("results") and len(results["results"]) > 0:
            return results["results"][0]["urls"]["regular"]
        
        return None
