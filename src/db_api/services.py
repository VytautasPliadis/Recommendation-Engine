import logging

import sqlalchemy.orm as _orm

from . import database as _database
from . import models as _models
from . import schemas as _schemas

logging.basicConfig(level=logging.INFO)


def create_database():
    """ Create the database schema based on the SQLAlchemy models. """
    return _database.Base.metadata.create_all(bind=_database.engine)


def get_db():
    """
    Provide a database session for the current request.

    Yields:
        _orm.Session: A SQLAlchemy database session.
    """
    db = _database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_actor(db: _orm.Session, name: str):
    """
    Retrieve an actor by name from the database.

    Args:
        db (_orm.Session): The SQLAlchemy database session.
        name (str): The name of the actor to retrieve.

    Returns:
        _models.Actor: The actor object if found, else None.
    """
    return db.query(_models.Actor).filter(_models.Actor.name == name).first()


def create_actor(db: _orm.Session, actor: _schemas.CreateActor):
    """
    Create a new actor in the database.

    Args:
        db (_orm.Session): The SQLAlchemy database session.
        actor (_schemas.CreateActor): The actor information to create.

    Returns:
        _models.Actor: The created actor object.
    """
    db_actor = _models.Actor(name=actor.name)
    db.add(db_actor)
    db.commit()
    db.refresh(db_actor)
    return db_actor


def get_director(db: _orm.Session, name: str):
    """
    Retrieve a director by name from the database.

    Args:
        db (_orm.Session): The SQLAlchemy database session.
        name (str): The name of the director to retrieve.

    Returns:
        _models.Director: The director object if found, else None.
    """
    return db.query(_models.Director).filter(_models.Director.name == name).first()


def create_director(db: _orm.Session, director: _schemas.CreateDirector):
    """
    Create a new director in the database.

    Args:
        db (_orm.Session): The SQLAlchemy database session.
        director (_schemas.CreateDirector): The director information to create.

    Returns:
        _models.Director: The created director object.
    """
    db_director = _models.Director(name=director.name)
    db.add(db_director)
    db.commit()
    db.refresh(db_director)
    return db_director


def get_media(db: _orm.Session, title: str):
    """
    Retrieve media by title from the database.

    Args:
        db (_orm.Session): The SQLAlchemy database session.
        title (str): The title of the media to retrieve.

    Returns:
        _models.Media: The media object if found, else None.
    """
    return db.query(_models.Media).filter(_models.Media.title == title).first()


def create_media(db: _orm.Session, media: _schemas.Media):
    """
    Create a new media entry in the database.

    Args:
        db (_orm.Session): The SQLAlchemy database session.
        media (_schemas.Media): The media information to create.

    Returns:
        _models.Media: The created media object.
    """
    db_media = _models.Media(
        id=media.id,
        title=media.title,
        type=media.type.value,
        release_year=media.release_year,
        age_certification=media.age_certification,
        runtime=media.runtime,
        seasons=media.seasons,
        imdb_score=media.imdb_score,
        imdb_votes=media.imdb_votes,
    )
    db.add(db_media)
    db.commit()
    db.refresh(db_media)
    return db_media


def recommend_by_sore(
        db: _orm.Session,
        genre_type: str,
        target_imdb_score: float,
        score_range: float = 0.5,
):
    """
    Recommend media based on genre and IMDb score around a specified target.

    Args:
        db (_orm.Session): The SQLAlchemy database session.
        genre_type (str): The genre type to filter media by.
        target_imdb_score (float): The target IMDb score.
        score_range (float, optional): The range for IMDb scores (default is 0.5).

    Returns:
        List[dict]: A list of recommended media information as dictionaries.
    """

    min_imdb_score = target_imdb_score - score_range
    max_imdb_score = target_imdb_score + score_range

    recommended_media = (
        db.query(_models.Media)
        .join(_models.Media.genre)
        .filter(_models.Genre.genre_type == genre_type)
        .filter(_models.Media.imdb_score >= min_imdb_score)
        .filter(_models.Media.imdb_score <= max_imdb_score)
        .order_by(_models.Media.imdb_votes.desc())
        .limit(10)
        .all()
    )

    media_list = []
    for media in recommended_media:
        media_info = {
            "title": media.title,
            "release_year": media.release_year,
            "imdb_votes": float(media.imdb_votes),
            "imdb_score": float(media.imdb_score),
        }
        media_list.append(media_info)

    return media_list


def recommend_by_actor(db: _orm.Session, name: str):
    """
    Recommend media based on a specific actor.

    Args:
        db (_orm.Session): The SQLAlchemy database session.
        name (str): The name of the actor.

    Returns:
        List[dict]: A list of recommended media information as dictionaries.
    """

    recommended_media = (
        db.query(_models.Media)
        .join(_models.media_actor_association)
        .join(_models.Actor)
        .filter(_models.Actor.name == name)
        .order_by(_models.Media.imdb_score.desc(), _models.Media.imdb_votes.desc())
        .limit(10)
        .all()
    )

    media_list = []
    for media in recommended_media:
        media_info = {
            "title": media.title,
            "release_year": media.release_year,
            "imdb_votes": float(media.imdb_votes),
            "imdb_score": float(media.imdb_score),
        }
        media_list.append(media_info)

    return media_list


def recommend_by_director(db: _orm.Session, name: str):
    """
    Recommend media based on a specific director.

    Args:
        db (_orm.Session): The SQLAlchemy database session.
        name (str): The name of the director.

    Returns:
        List[dict]: A list of recommended media information as dictionaries.
    """
    recommended_media = (
        db.query(_models.Media)
        .join(_models.media_director_association)
        .join(_models.Director)
        .filter(_models.Director.name == name)
        .order_by(_models.Media.imdb_score.desc(), _models.Media.imdb_votes.desc())
        .limit(10)
        .all()
    )

    media_list = []
    for media in recommended_media:
        media_info = {
            "title": media.title,
            "release_year": media.release_year,
            "imdb_votes": float(media.imdb_votes),
            "imdb_score": float(media.imdb_score),
        }
        media_list.append(media_info)

    return media_list
