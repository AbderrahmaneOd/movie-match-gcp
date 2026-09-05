from typing import Optional


class Favorite:
    def __init__(
        self,
        movie_id: int,
        title: str,
        poster_path: Optional[str] = None,
        release_date: Optional[str] = None,
        vote_average: Optional[float] = None,
        year: Optional[int] = None,
        created_at: Optional[str] = None,
    ):
        self.movie_id = movie_id
        self.title = title
        self.poster_path = poster_path
        self.release_date = release_date
        self.vote_average = vote_average
        self.year = year
        self.created_at = created_at

    def to_dict(self, image_url_builder=None):
        poster_url = self.poster_path
        if poster_url and image_url_builder and not poster_url.startswith("http"):
            poster_url = image_url_builder(poster_url)

        return {
            "movie_id": self.movie_id,
            "title": self.title,
            "poster_url": poster_url,
            "release_date": self.release_date,
            "year": self.year,
            "vote_average": self.vote_average,
            "created_at": self.created_at,
        }