from flask import Blueprint, jsonify, request
import redis
import os
import json

from app.routes.errors import error_response
from app.services.tmdb_service import TMDBError

movies_bp = Blueprint("movies", __name__, url_prefix="/api/movies")

# Initialize Redis client via environment variables.
# Falls back to None so the app runs (and caching is skipped) when
# REDIS_HOST/REDIS_PORT are not configured.
redis_client = None
if os.getenv("REDIS_HOST"):
    redis_client = redis.Redis(
        host=os.getenv("REDIS_HOST"),
        port=os.getenv("REDIS_PORT", 6379),
        decode_responses=True,
    )

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
    
    cache_key = f"movies:popular:page:{page}"
    print(f"Fetching popular movies for page {page} with cache key: {cache_key}")
    
    # 1. Read-aside: Check cache first
    if redis_client is not None:
        try:
            cached_data = redis_client.get(cache_key)
            if cached_data:
                print(f"Cache hit for key: {cache_key}")
                return jsonify({"results": json.loads(cached_data), "page": page, "source": "cache"})
        except redis.RedisError:
            pass  # Fail gracefully if Redis is temporarily unreachable
    
    # 2. Fetch fresh data from TMDB
    try:
        movies = get_movie_service().get_popular_movies(page=page)
    except TMDBError as exc:
        return error_response(str(exc), status_code=502)
    
    # 3. Cache the fresh result with a 2-hour TTL (7200 seconds)
    if redis_client is not None:
        try:
            redis_client.setex(cache_key, 7200, json.dumps(movies))
        except redis.RedisError:
            pass
    
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
    
    session_id = request.headers.get("X-Session-ID")
    get_event_service().publish(
        "movie_viewed", movie_id=movie_id, session_id=session_id
    )
    
    cache_key = f"movies:detail:{movie_id}"
    
    try:
        cached_data = redis_client.get(cache_key) if redis_client is not None else None
        if cached_data:
            return jsonify(json.loads(cached_data))
    except redis.RedisError:
        pass
    
    try:
        movie = get_movie_service().get_movie_details(movie_id)
    except TMDBError as exc:
        return error_response(str(exc), status_code=502)

    try:
        # Cache movie details for 24 hours (86400 seconds)
        if redis_client is not None:
            redis_client.setex(cache_key, 86400, json.dumps(movie))
    except redis.RedisError:
        pass
    
    return jsonify(movie)