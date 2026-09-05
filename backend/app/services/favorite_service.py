import logging

from app.models.favorite import Favorite

logger = logging.getLogger(__name__)


class FavoriteService:
    def __init__(self, repository, movie_service):
        self.repository = repository
        self.movie_service = movie_service

    def list_favorites(self, session_id):
        app = self.repository.app
        image_builder = lambda path: self.movie_service._image_url(path)
        return [
            favorite.to_dict(image_url_builder=image_builder)
            for favorite in self.repository.list_by_session(session_id)
        ]

    def add_favorite(self, session_id, movie_id):
        data = self.movie_service.get_for_favorite(movie_id)
        favorite = Favorite(
            movie_id=data["movie_id"],
            title=data["title"],
            poster_path=data.get("poster_path"),
            release_date=data.get("release_date"),
            vote_average=data.get("vote_average"),
            year=data.get("year"),
        )
        saved = self.repository.add(session_id, favorite)
        return saved.to_dict(image_url_builder=self.movie_service._image_url)

    def remove_favorite(self, session_id, movie_id):
        return self.repository.remove(session_id, movie_id)

    def is_favorite(self, session_id, movie_id):
        return self.repository.get(session_id, movie_id) is not None