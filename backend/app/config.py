import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")

    TMDB_API_KEY = os.getenv("TMDB_API_KEY")
    TMDB_BASE_URL = os.getenv("TMDB_BASE_URL", "https://api.themoviedb.org/3")
    TMDB_IMAGE_BASE_URL = os.getenv(
        "TMDB_IMAGE_BASE_URL", "https://image.tmdb.org/t/p"
    )
    TMDB_IMAGE_SIZE = os.getenv("TMDB_IMAGE_SIZE", "w500")

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATABASE_PATH = os.getenv(
        "DATABASE_PATH", os.path.join(BASE_DIR, "movie_match.db")
    )

    CORS_ORIGINS = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:3000,http://127.0.0.1:3000",
        ).split(",")
        if origin.strip()
    ]

    SESSION_HEADER = os.getenv("SESSION_HEADER", "X-Session-ID")