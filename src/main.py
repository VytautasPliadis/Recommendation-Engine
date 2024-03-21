from typing import Optional, List
import logging

import fastapi as _fastapi
import sqlalchemy.orm as _orm
from db_api import schemas as _schemas, models as _models, services as _services

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = _fastapi.FastAPI()

_services.create_database()


# Endpoint to write actor to the database
@app.post("/actors/", response_model=_schemas.Actor)
def create_actor(
    actor: _schemas.CreateActor, db: _orm.Session = _fastapi.Depends(_services.get_db)
):
    """
    Create a new actor in the database.

    Args:
        actor (_schemas.CreateActor): The actor data to be created.

    Returns:
        _schemas.Actor: The created actor.
    """
    db_actor = _services.get_actor(db=db, name=actor.name)
    if db_actor:
        raise _fastapi.HTTPException(
            status_code=400, detail="Actor is in the database already"
        )
    return _services.create_actor(db=db, actor=actor)


# Endpoint to get actor from database
@app.get("/actors/{actor_name}", response_model=_schemas.Actor)
def get_actor(
    actor_name: str, db: _orm.Session = _fastapi.Depends(_services.get_db)
) -> Optional[_schemas.Actor]:
    """
    Retrieve an actor by name from the database.

    Args:
        actor_name (str): The name of the actor to retrieve.

    Returns:
        Optional[_schemas.Actor]: The actor information if found, or None if not found.
    """
    db_actor = _services.get_actor(db=db, name=actor_name)
    if not db_actor:
        raise _fastapi.HTTPException(status_code=404, detail="Actor not found")
    return db_actor


# Endpoint to write director to the database
@app.post("/directors/", response_model=_schemas.Director)
def create_director(
    director: _schemas.CreateDirector,
    db: _orm.Session = _fastapi.Depends(_services.get_db),
):
    """
    Create a new director and store it in the database.

    Args:
        director (CreateDirector): The director information to be created.
        db (Session, optional): The database session. Automatically provided by FastAPI.

    Returns:
        Director: The created director information.
    """
    db_director = _services.get_director(db=db, name=director.name)
    if db_director:
        raise _fastapi.HTTPException(
            status_code=400, detail="Director is in the database already"
        )
    return _services.create_director(db=db, director=director)


# Endpoint to get director from database
@app.get("/director/{director_name}", response_model=_schemas.Director)
def get_director(
    director_name: str, db: _orm.Session = _fastapi.Depends(_services.get_db)
) -> Optional[_schemas.Director]:
    """
    Retrieve director information by name from the database.

    Args:
        director_name (str): The name of the director to retrieve.
        db (Session, optional): The database session. Automatically provided by FastAPI.

    Returns:
        Director: The retrieved director information.
    """

    db_director = _services.get_director(db=db, name=director_name)
    if not db_director:
        raise _fastapi.HTTPException(status_code=404, detail="Director not found")
    return db_director


# Endpoint to write media to the database
@app.post("/media/", response_model=_schemas.Media)
def create_media(
    media: _schemas.Media, db: _orm.Session = _fastapi.Depends(_services.get_db)
):
    """
    Create a new media entry and store it in the database.

    Args:
        media (Media): The media information to be created.
        db (Session, optional): The database session. Automatically provided by FastAPI.

    Returns:
        Media: The created media information.
    """
    db_media = _services.get_media(db=db, title=media.title)
    if db_media:
        raise _fastapi.HTTPException(
            status_code=400, detail="Media is in the database already"
        )
    return _services.create_media(db=db, media=media)


# Endpoint to get media from database
@app.get("/media/{media_title}", response_model=_schemas.Media)
def get_media(media_title: str, db: _orm.Session = _fastapi.Depends(_services.get_db)):
    """
    Retrieve media information by title from the database.

    Args:
        media_title (str): The title of the media to retrieve.
        db (Session, optional): The database session. Automatically provided by FastAPI.

    Returns:
        Media: The retrieved media information.
    """

    db_media = _services.get_media(db=db, title=media_title)
    if not db_media:
        raise _fastapi.HTTPException(status_code=404, detail="Media not found")
    return db_media


@app.post("/associate-actor-with-media/")
def associate_actor_with_media(
    actor_id: int, media_id: str, db: _orm.Session = _fastapi.Depends(_services.get_db)
):
    """
    Associate an actor with a media entry in the database.

    Args:
        actor_id (int): The ID of the actor to associate.
        media_id (str): The ID of the media to associate.
        db (Session, optional): The database session. Automatically provided by FastAPI.

    Returns:
        dict: A message indicating the success of the association.
    """
    media = db.query(_models.Media).filter(_models.Media.id == media_id).first()
    if not media:
        raise _fastapi.HTTPException(status_code=404, detail="Media not found")

    actor = db.query(_models.Actor).filter(_models.Actor.actor_id == actor_id).first()
    if not actor:
        raise _fastapi.HTTPException(status_code=404, detail="Actor not found")

    if actor not in media.actor:
        media.actor.append(actor)
        db.commit()

    return {"message": "Actor associated with media successfully"}


@app.post("/associate-director-with-media/")
def associate_director_with_media(
    director_id: int,
    media_id: str,
    db: _orm.Session = _fastapi.Depends(_services.get_db),
):
    """
    Associate a director with a media entry in the database.

    Args:
        director_id (int): The ID of the director to associate.
        media_id (str): The ID of the media to associate.
        db (Session, optional): The database session. Automatically provided by FastAPI.

    Returns:
        dict: A message indicating the success of the association.
    """
    media = db.query(_models.Media).filter(_models.Media.id == media_id).first()
    if not media:
        raise _fastapi.HTTPException(status_code=404, detail="Media not found")

    director = (
        db.query(_models.Director)
        .filter(_models.Director.director_id == director_id)
        .first()
    )
    if not director:
        raise _fastapi.HTTPException(status_code=404, detail="Director not found")

    if director not in media.director:
        media.director.append(director)
        db.commit()

    return {"message": "Director associated with media successfully"}


@app.get(
    "/recommendations/genre-target-score",
    response_model=List[_schemas.MediaRecommendation],
)
def get_recommendations(
    genre_type: str,
    target_imdb_score: float = 7.0,
    db: _orm.Session = _fastapi.Depends(_services.get_db),
):
    """
    Get media recommendations based on genre and minimum IMDb score.

    Args:
        genre_type (str): The genre type for which recommendations are requested.
        target_imdb_score (float, optional): The minimum IMDb score for recommended media. Default is 7.0.
        db (Session, optional): The database session. Automatically provided by FastAPI.

    Returns:
        List[_schemas.MediaRecommendation]: A list of recommended media matching the genre and IMDb score criteria.
    """
    try:
        recommendations = _services.recommend_by_sore(
            db=db, genre_type=genre_type, target_imdb_score=target_imdb_score
        )
        return recommendations
    except Exception as e:
        logger.error(f"Error in getting recommendations: {str(e)}")
        raise _fastapi.HTTPException(
            status_code=500, detail="An error occurred while fetching recommendations."
        )


@app.get("/recommendations/actor", response_model=List[_schemas.MediaRecommendation])
def get_recommendations(
    name: str, db: _orm.Session = _fastapi.Depends(_services.get_db)
):
    """
    Get media recommendations based on genre and target IMDb score.

    Args:
        genre_type (str): The genre type for recommendations.
        target_imdb_score (float, optional): The target IMDb score. Defaults to 7.0.

    Returns:
        List[_schemas.MediaRecommendation]: A list of recommended media.
    """
    try:
        recommendations = _services.recommend_by_actor(db=db, name=name)
        return recommendations
    except Exception as e:
        logger.error(f"Error in getting recommendations: {str(e)}")
        raise _fastapi.HTTPException(
            status_code=500, detail="An error occurred while fetching recommendations."
        )


@app.get("/recommendations/director", response_model=List[_schemas.MediaRecommendation])
def get_recommendations(
    name: str, db: _orm.Session = _fastapi.Depends(_services.get_db)
):
    """
    Get media recommendations based on the name of a director.

    Args:
        name (str): The name of the director for which recommendations are requested.

    Returns:
        List[_schemas.MediaRecommendation]: A list of recommended media associated with the director.
    """
    try:
        recommendations = _services.recommend_by_director(db=db, name=name)
        return recommendations
    except Exception as e:
        logger.error(f"Error in getting recommendations: {str(e)}")
        raise _fastapi.HTTPException(
            status_code=500, detail="An error occurred while fetching recommendations."
        )
