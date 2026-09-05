from flask import Blueprint, jsonify, request

from app.routes.errors import error_response
from app.services.tmdb_service import TMDBError

movies_bp = Blueprint("movies", __name__, url_prefix="/api/movies")


def get_movie_service():
    from flask import current_app

    return current_app.movie_service


def get_event_service():
    from flask import current_app

    return current_app.event_service


@movies_bp.route("/popular", methods=["GET"])
def popular_movies():
    page = request.args.get("page", default=1, type=int)
    if page < 1:
        return error_response("Page must be a positive integer")
    try:
        movies = get_movie_service().get_popular_movies(page=page)
    except TMDBError as exc:
        return error_response(str(exc), status_code=502)
    return jsonify({"results": movies, "page": page})


@movies_bp.route("/search", methods=["GET"])
def search_movies():
    query = request.args.get("q", "").strip()
    if not query:
        return error_response("Query parameter 'q' is required")
    if len(query) > 200:
        return error_response("Query is too long")

    try:
        movies = get_movie_service().search_movies(query)
    except TMDBError as exc:
        return error_response(str(exc), status_code=502)

    get_event_service().publish("movie_searched", metadata={"query": query})
    return jsonify({"results": movies, "query": query})


@movies_bp.route("/<int:movie_id>", methods=["GET"])
def movie_details(movie_id):
    try:
        movie = get_movie_service().get_movie_details(movie_id)
    except TMDBError as exc:
        return error_response(str(exc), status_code=502)

    session_id = request.headers.get("X-Session-ID")
    get_event_service().publish(
        "movie_viewed", movie_id=movie_id, session_id=session_id
    )
    return jsonify(movie)