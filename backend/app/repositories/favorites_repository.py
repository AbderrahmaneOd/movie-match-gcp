from app.extensions import db
from app.models.favorite import Favorite


class FavoritesRepository:
    def list_by_session(self, session_id):
        return (
            db.session.execute(
                db.select(Favorite)
                .where(Favorite.session_id == session_id)
                .order_by(Favorite.created_at.desc(), Favorite.id.desc())
            )
            .scalars()
            .all()
        )

    def add(self, session_id, favorite):
        existing = db.session.execute(
            db.select(Favorite).where(
                Favorite.session_id == session_id,
                Favorite.movie_id == favorite.movie_id,
            )
        ).scalar_one_or_none()

        if existing is not None:
            return existing

        favorite.session_id = session_id
        db.session.add(favorite)
        db.session.commit()
        db.session.refresh(favorite)
        return favorite

    def remove(self, session_id, movie_id):
        favorite = db.session.execute(
            db.select(Favorite).where(
                Favorite.session_id == session_id,
                Favorite.movie_id == movie_id,
            )
        ).scalar_one_or_none()

        if favorite is None:
            return False

        db.session.delete(favorite)
        db.session.commit()
        return True

    def get(self, session_id, movie_id):
        return db.session.execute(
            db.select(Favorite).where(
                Favorite.session_id == session_id,
                Favorite.movie_id == movie_id,
            )
        ).scalar_one_or_none()