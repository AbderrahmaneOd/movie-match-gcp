import logging

import requests

logger = logging.getLogger(__name__)


class TMDBError(Exception):
    """Raised when a TMDB API call fails."""


class TMDBService:
    def __init__(self, api_key, base_url, timeout=10):
        if not api_key:
            raise TMDBError("TMDB_API_KEY is not configured")
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _headers(self):
        return {
            "accept": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

    def _get(self, path, params=None):
        url = f"{self.base_url}{path}"
        try:
            response = requests.get(
                url,
                headers=self._headers(),
                params=params,
                timeout=self.timeout,
            )
        except requests.RequestException as exc:
            logger.error("TMDB request failed url=%s error=%s", url, exc)
            raise TMDBError("Unable to reach TMDB") from exc

        if response.status_code == 401:
            raise TMDBError("Invalid TMDB API key")
        if response.status_code == 404:
            raise TMDBError("Movie not found")
        if not response.ok:
            logger.error(
                "TMDB request returned status=%s url=%s", response.status_code, url
            )
            raise TMDBError("TMDB request failed")

        return response.json()

    def get_popular_movies(self, page=1):
        data = self._get(
            "/movie/popular", params={"language": "en-US", "page": page}
        )
        return data.get("results", [])

    def search_movies(self, query, page=1):
        data = self._get(
            "/search/movie",
            params={
                "query": query,
                "language": "en-US",
                "page": page,
                "include_adult": False,
            },
        )
        return data.get("results", [])

    def get_movie_details(self, movie_id):
        return self._get(
            f"/movie/{movie_id}",
            params={"language": "en-US", "append_to_response": "credits"},
        )