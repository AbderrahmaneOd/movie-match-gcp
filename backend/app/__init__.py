from flask import Flask
from flask_cors import CORS

from app.config import Config
from app.extensions import db
from app.repositories.favorites_repository import FavoritesRepository
from app.routes.errors import error_response
from app.routes.favorites import favorites_bp
from app.routes.health import health_bp
from app.routes.movies import movies_bp
from app.services.event_service import EventService
from app.services.favorite_service import FavoriteService
from app.services.movie_service import MovieService
from app.services.tmdb_service import TMDBError, TMDBService

import app.models  # noqa: F401  ensure models are registered with SQLAlchemy metadata


def create_app(config_object=None):
    app = Flask(__name__)
    app.config.from_object(config_object or Config)

    db.init_app(app)

    tmdb = TMDBService(
        api_key=app.config["TMDB_API_KEY"],
        base_url=app.config["TMDB_BASE_URL"],
    )
    movie_service = MovieService(
        tmdb,
        image_base_url=app.config["TMDB_IMAGE_BASE_URL"],
        image_size=app.config["TMDB_IMAGE_SIZE"],
    )
    favorite_repository = FavoritesRepository()
    favorite_service = FavoriteService(favorite_repository, movie_service)

    app.movie_service = movie_service
    app.favorite_service = favorite_service
    app.event_service = EventService()

    CORS(
        app,
        resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}},
        supports_credentials=True,
    )

    app.register_blueprint(health_bp)
    app.register_blueprint(movies_bp)
    app.register_blueprint(favorites_bp)

    @app.errorhandler(TMDBError)
    def handle_tmdb_error(exc):
        return error_response(str(exc), status_code=502)

    @app.errorhandler(404)
    def handle_not_found(error):
        return error_response("Resource not found", status_code=404)

    return app