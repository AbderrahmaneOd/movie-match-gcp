from app.database import get_db
from app.models.favorite import Favorite


class FavoritesRepository:
    def __init__(self, app):
        self.app = app

    def _db(self):
        return get_db(self.app)

    def list_by_session(self, session_id):
        rows = self._db().execute(
            """
            SELECT movie_id, title, poster_path, release_date,
                   vote_average, year, created_at
            FROM favorites
            WHERE session_id = ?
            ORDER BY created_at DESC, id DESC
            """,
            (session_id,),
        ).fetchall()
        return [Favorite(**dict(row)) for row in rows]

    def add(self, session_id, favorite):
        db = self._db()
        db.execute(
            """
            INSERT OR IGNORE INTO favorites
                (session_id, movie_id, title, poster_path,
                 release_date, vote_average, year)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                session_id,
                favorite.movie_id,
                favorite.title,
                favorite.poster_path,
                favorite.release_date,
                favorite.vote_average,
                favorite.year,
            ),
        )
        db.commit()
        return self.get(session_id, favorite.movie_id)

    def remove(self, session_id, movie_id):
        db = self._db()
        db.execute(
            "DELETE FROM favorites WHERE session_id = ? AND movie_id = ?",
            (session_id, movie_id),
        )
        db.commit()
        return db.total_changes > 0

    def get(self, session_id, movie_id):
        row = self._db().execute(
            """
            SELECT movie_id, title, poster_path, release_date,
                   vote_average, year, created_at
            FROM favorites
            WHERE session_id = ? AND movie_id = ?
            """,
            (session_id, movie_id),
        ).fetchone()
        return Favorite(**dict(row)) if row else None

    def count(self, session_id):
        row = self._db().execute(
            "SELECT COUNT(*) AS total FROM favorites WHERE session_id = ?",
            (session_id,),
        ).fetchone()
        return row["total"]