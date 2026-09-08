import os
import unittest

from app import create_app
from app.extensions import db
from app.repositories.favorites_repository import FavoritesRepository
from app.services.movie_service import MovieService
from app.services.tmdb_service import TMDBService

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+psycopg://myuser:MovieMatch1234@localhost:5432/moviematch_test",
)


class FakeTMDB(TMDBService):
    def __init__(self):
        pass

    def get_popular_movies(self, page=1):
        return [
            {
                "id": 1,
                "title": "Popular Film",
                "overview": "An overview",
                "poster_path": "/poster.jpg",
                "backdrop_path": "/backdrop.jpg",
                "release_date": "2020-05-01",
                "vote_average": 8.1,
                "vote_count": 100,
            }
        ]

    def search_movies(self, query, page=1):
        return [
            {
                "id": 2,
                "title": f"Result for {query}",
                "overview": None,
                "poster_path": None,
                "backdrop_path": None,
                "release_date": None,
                "vote_average": 0.0,
                "vote_count": 0,
            }
        ]

    def get_movie_details(self, movie_id):
        return {
            "id": movie_id,
            "title": "Detailed Film",
            "overview": "Detailed overview",
            "poster_path": "/detailed.jpg",
            "backdrop_path": "/backdrop.jpg",
            "release_date": "2019-11-22",
            "vote_average": 7.5,
            "vote_count": 50,
            "runtime": 120,
            "genres": [{"id": 18, "name": "Drama"}],
            "status": "Released",
            "tagline": "A tagline",
        }


def build_app():
    class TestConfig:
        TESTING = True
        SQLALCHEMY_DATABASE_URI = TEST_DATABASE_URL
        SQLALCHEMY_TRACK_MODIFICATIONS = False
        TMDB_API_KEY = "test-key"
        TMDB_BASE_URL = "https://example.test/3"
        TMDB_IMAGE_BASE_URL = "https://images.example.test/t/p"
        TMDB_IMAGE_SIZE = "w500"
        CORS_ORIGINS = ["http://localhost:3000"]
        SESSION_HEADER = "X-Session-ID"

    app = create_app(TestConfig)

    with app.app_context():
        db.drop_all()
        db.create_all()

    movie_service = MovieService(
        FakeTMDB(),
        image_base_url=TestConfig.TMDB_IMAGE_BASE_URL,
        image_size=TestConfig.TMDB_IMAGE_SIZE,
    )
    repository = FavoritesRepository()
    from app.services.favorite_service import FavoriteService

    app.movie_service = movie_service
    app.favorite_service = FavoriteService(repository, movie_service)
    return app


class MovieServiceTest(unittest.TestCase):
    def setUp(self):
        app = build_app()
        self.app = app
        self.service = app.movie_service

    def test_popular_movies_serialization(self):
        movies = self.service.get_popular_movies()
        self.assertEqual(len(movies), 1)
        movie = movies[0]
        self.assertEqual(movie["id"], 1)
        self.assertEqual(movie["title"], "Popular Film")
        self.assertEqual(movie["poster_url"], "https://images.example.test/t/p/w500/poster.jpg")
        self.assertEqual(movie["year"], 2020)

    def test_search_movies(self):
        results = self.service.search_movies("inception")
        self.assertEqual(results[0]["title"], "Result for inception")
        self.assertIsNone(results[0]["poster_url"])
        self.assertIsNone(results[0]["year"])

    def test_movie_details(self):
        details = self.service.get_movie_details(2)
        self.assertEqual(details["runtime"], 120)
        self.assertEqual(details["genres"], ["Drama"])
        self.assertEqual(details["year"], 2019)

    def test_details_default_routing(self):
        client = self.app.test_client()
        resp = client.get("/api/movies/2")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["title"], "Detailed Film")


class FavoritesApiTest(unittest.TestCase):
    def setUp(self):
        self.app = build_app()
        self.client = self.app.test_client()

    def test_favorites_requires_session(self):
        resp = self.client.get("/api/favorites")
        self.assertEqual(resp.status_code, 400)

    def test_add_list_remove_favorite(self):
        headers = {"X-Session-ID": "session-abc"}

        resp = self.client.post("/api/favorites/2", headers=headers)
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.get_json()["movie_id"], 2)
        self.assertEqual(resp.get_json()["title"], "Detailed Film")

        resp = self.client.get("/api/favorites", headers=headers)
        self.assertEqual(resp.status_code, 200)
        results = resp.get_json()["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["movie_id"], 2)

        resp = self.client.delete("/api/favorites/2", headers=headers)
        self.assertEqual(resp.status_code, 200)

        resp = self.client.get("/api/favorites", headers=headers)
        self.assertEqual(resp.get_json()["results"], [])

    def test_duplicate_favorite_is_idempotent(self):
        headers = {"X-Session-ID": "session-dup"}
        self.client.post("/api/favorites/2", headers=headers)
        resp = self.client.post("/api/favorites/2", headers=headers)
        self.assertEqual(resp.status_code, 201)
        result = self.client.get("/api/favorites", headers=headers).get_json()
        self.assertEqual(len(result["results"]), 1)

    def test_favorites_scoped_to_session(self):
        self.client.post("/api/favorites/2", headers={"X-Session-ID": "session-a"})
        resp = self.client.get("/api/favorites", headers={"X-Session-ID": "session-b"})
        self.assertEqual(resp.get_json()["results"], [])

    def test_remove_missing_favorite(self):
        resp = self.client.delete(
            "/api/favorites/999", headers={"X-Session-ID": "session-x"}
        )
        self.assertEqual(resp.status_code, 404)


class HealthTest(unittest.TestCase):
    def setUp(self):
        self.app = build_app()
        self.client = self.app.test_client()

    def test_health(self):
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json(), {"status": "ok"})

    def test_search_requires_query(self):
        resp = self.client.get("/api/movies/search")
        self.assertEqual(resp.status_code, 400)


if __name__ == "__main__":
    unittest.main()