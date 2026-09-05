from app.services.tmdb_service import TMDBError, TMDBService


def _year_from_release_date(release_date):
    if release_date and len(release_date) >= 4 and release_date[:4].isdigit():
        return int(release_date[:4])
    return None


class MovieService:
    def __init__(self, tmdb, image_base_url, image_size):
        self.tmdb = tmdb
        self.image_base_url = image_base_url.rstrip("/")
        self.image_size = image_size

    def _image_url(self, path):
        if not path:
            return None
        return f"{self.image_base_url}/{self.image_size}{path}"

    def _serialize_movie(self, item):
        year = _year_from_release_date(item.get("release_date"))
        return {
            "id": item.get("id"),
            "title": item.get("title"),
            "overview": item.get("overview"),
            "poster_url": self._image_url(item.get("poster_path")),
            "backdrop_url": self._image_url(item.get("backdrop_path")),
            "release_date": item.get("release_date"),
            "year": year,
            "vote_average": item.get("vote_average"),
            "vote_count": item.get("vote_count"),
        }

    def get_popular_movies(self, page=1):
        results = self.tmdb.get_popular_movies(page=page)
        return [self._serialize_movie(item) for item in results]

    def search_movies(self, query, page=1):
        results = self.tmdb.search_movies(query, page=page)
        return [self._serialize_movie(item) for item in results]

    def get_movie_details(self, movie_id):
        details = self.tmdb.get_movie_details(movie_id)
        genres = [genre.get("name") for genre in details.get("genres", [])]
        year = _year_from_release_date(details.get("release_date"))

        movie = self._serialize_movie(details)
        movie.update(
            {
                "runtime": details.get("runtime"),
                "genres": genres,
                "status": details.get("status"),
                "tagline": details.get("tagline"),
            }
        )
        return movie

    def get_for_favorite(self, movie_id):
        """Minimal movie data used when snapshotting a favorite."""
        try:
            details = self.get_movie_details(movie_id)
            return {
                "movie_id": details["id"],
                "title": details["title"] or f"Movie {movie_id}",
                "poster_path": details.get("poster_url"),
                "release_date": details.get("release_date"),
                "vote_average": details.get("vote_average"),
                "year": details.get("year"),
            }
        except TMDBError:
            return {
                "movie_id": movie_id,
                "title": f"Movie {movie_id}",
                "poster_path": None,
                "release_date": None,
                "vote_average": None,
                "year": None,
            }