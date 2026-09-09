import os

from dotenv import load_dotenv

load_dotenv()


def _build_database_uri():
    """Build the SQLAlchemy database URI from environment variables.

    Local dev (TCP):
        DATABASE_URL=postgresql+psycopg://myuser:MovieMatch1234@localhost:5432/MovieMatch

    GCP Cloud Run (UNIX socket via Cloud SQL Auth Proxy):
        DB_SOCKET_DIR=/cloudsql/PROJECT:REGION:INSTANCE
        DB_USER=<user>
        DB_PASSWORD=<password>
        DB_NAME=<dbname>
    """
    url = os.getenv("DATABASE_URL")
    if url:
        return url

    user = os.getenv("DB_USER", "myuser")
    password = os.getenv("DB_PASSWORD", "MovieMatch1234")
    name = os.getenv("DB_NAME", "MovieMatch")
    socket_dir = os.getenv("DB_SOCKET_DIR")

    if socket_dir:
        return f"postgresql+psycopg://{user}:{password}@/{name}?host={socket_dir}"

    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    return f"postgresql+psycopg://{user}:{password}@{host}:{port}/{name}"


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")

    SQLALCHEMY_DATABASE_URI = _build_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }

    TMDB_API_KEY = os.getenv("TMDB_API_KEY")
    TMDB_BASE_URL = os.getenv("TMDB_BASE_URL", "https://api.themoviedb.org/3")
    TMDB_IMAGE_BASE_URL = os.getenv(
        "TMDB_IMAGE_BASE_URL", "https://image.tmdb.org/t/p"
    )
    TMDB_IMAGE_SIZE = os.getenv("TMDB_IMAGE_SIZE", "w500")

    CORS_ORIGINS = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:3000,http://127.0.0.1:3000",
        ).split(",")
        if origin.strip()
    ]

    SESSION_HEADER = os.getenv("SESSION_HEADER", "X-Session-ID")
    
    GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
    TOPIC_ID = os.getenv("TOPIC_ID")
    PUBSUB_EMULATOR_HOST = os.getenv("PUBSUB_EMULATOR_HOST")