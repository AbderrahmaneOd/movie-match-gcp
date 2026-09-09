from datetime import datetime, timezone

from app.extensions import db


class Favorite(db.Model):
    __tablename__ = "favorites"

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(128), nullable=False, index=True)
    movie_id = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(500), nullable=False)
    poster_path = db.Column(db.String(500))
    release_date = db.Column(db.String(50))
    vote_average = db.Column(db.Float)
    year = db.Column(db.Integer)
    created_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    __table_args__ = (
        db.UniqueConstraint("session_id", "movie_id", name="uq_favorites_session_movie"),
    )

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
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }