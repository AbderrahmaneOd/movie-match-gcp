from flask import Blueprint, jsonify, request

from app.routes.errors import error_response
from app.services.tmdb_service import TMDBError

favorites_bp = Blueprint("favorites", __name__, url_prefix="/api/favorites")


def get_session_id():
    from flask import current_app

    return request.headers.get(current_app.config["SESSION_HEADER"])


def get_favorite_service():
    from flask import current_app

    return current_app.favorite_service


def get_event_service():
    from flask import current_app

    return current_app.event_service


@favorites_bp.route("", methods=["GET"])
def list_favorites():
    session_id = get_session_id()
    if not session_id:
        return error_response("Session ID header is required", status_code=400)
    favorites = get_favorite_service().list_favorites(session_id)
    return jsonify({"results": favorites})


@favorites_bp.route("/<int:movie_id>", methods=["POST"])
def add_favorite(movie_id):
    session_id = get_session_id()
    if not session_id:
        return error_response("Session ID header is required", status_code=400)

    try:
        favorite = get_favorite_service().add_favorite(session_id, movie_id)
    except TMDBError as exc:
        return error_response(str(exc), status_code=502)

    get_event_service().publish(
        "movie_favorited", movie_id=movie_id, session_id=session_id
    )
    return jsonify(favorite), 201


@favorites_bp.route("/<int:movie_id>", methods=["DELETE"])
def remove_favorite(movie_id):
    session_id = get_session_id()
    if not session_id:
        return error_response("Session ID header is required", status_code=400)

    removed = get_favorite_service().remove_favorite(session_id, movie_id)
    if not removed:
        return error_response("Favorite not found", status_code=404)

    get_event_service().publish(
        "movie_unfavorited", movie_id=movie_id, session_id=session_id
    )
    return jsonify({"removed": True, "movie_id": movie_id})