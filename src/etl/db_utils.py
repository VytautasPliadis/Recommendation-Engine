import ast
import logging

from ast import literal_eval
from itertools import chain

import sqlalchemy as sql
from dotenv import load_dotenv
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker, load_only

from data_models import Actor, Base, Director, Media, Genre, Production


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def create_database_session(db_url):
    """
    Create a database session using the DB_URL from environment variables.

    Returns:
        sqlalchemy.orm.Session: A SQLAlchemy database session.
    Raises:
        SQLAlchemyError: If an error occurs while creating the session.
    """
    try:
        engine = sql.create_engine(db_url)
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()

        logger.info("Database session created successfully.")
        return session

    except SQLAlchemyError as e:
        logger.error(f"An error occurred while creating the database session: {e}")
        raise


def insert_entities(session, df, entity_type):
    """
    Insert entity data into the database.

    Args:
        session (sqlalchemy.orm.Session): A SQLAlchemy database session.
        df (pd.DataFrame): The DataFrame containing entity data.
        entity_type (str): The type of entity to insert ("actor" or "director").

    Returns:
        list: A list of inserted entity objects.
    Raises:
        SQLAlchemyError: If an error occurs during insertion.
    """
    entity_classes = {"actor": Actor, "director": Director}

    # Use the entity_classes dictionary to get the class
    entity_class = entity_classes.get(entity_type.lower())

    entity_role = entity_type.upper()

    try:
        entity_df = df.loc[df["role"] == entity_role, "name"]
        unique_entities = entity_df.unique()

        # Create instances of the entity
        entities = [entity_class(name=name) for name in unique_entities]

        session.add_all(entities)
        session.commit()

        logger.info(f"{entity_role} table - finished.")
        return entities

    except SQLAlchemyError as e:
        logger.exception(
            f"An error occurred while uploading {entity_type} to database: {e}"
        )
        session.rollback()
        raise

    finally:
        session.close()


def extract_values(value):
    """
        Extract and return values from a string representation of a list or set.

        Args:
            value (str): A string representation of a list or set.

        Returns:
            set: A set containing the extracted values.
        """
    return set(literal_eval(value))


def insert_entity(
        session, df, column_name, entity_class, model_type, filter_value=None
):
    """
    Insert entities into the database.

    Args:
        session (sqlalchemy.orm.Session): A SQLAlchemy database session.
        df (pd.DataFrame): The DataFrame containing entity data.
        column_name (str): The name of the DataFrame column containing entity values.
        entity_class (sqlalchemy.ext.declarative.api.DeclarativeBase): The SQLAlchemy class representing the entity.
        model_type (str): The name of the model attribute to set with entity values.
        filter_value (str, optional): A value to filter out from entity values.

    Returns:
        None

    Raises:
        SQLAlchemyError: If an error occurs during insertion.
    """

    try:
        entity_df = df[[column_name]]
        unique_entities = set(
            chain.from_iterable(entity_df[column_name].apply(extract_values))
        )

        if filter_value:
            unique_entities.discard(filter_value)

        entities = []

        for value in unique_entities:
            entity = entity_class()
            setattr(entity, model_type, value)
            entities.append(entity)

        session.add_all(entities)
        session.commit()
        logger.info(f"{entity_class.__name__} table - finished.")

    except SQLAlchemyError as e:
        logger.exception(
            f"An error occurred while inserting {entity_class.__name__}: {e}"
        )
        session.rollback()
        raise

    finally:
        session.close()


def insert_genre(session, df):
    """
    Insert genre information into the database.

    Args:
        session (sqlalchemy.orm.Session): A SQLAlchemy database session.
        df (pd.DataFrame): The DataFrame containing genre data.

    Returns:
        None
    """
    insert_entity(session, df, "genres", Genre, "genre_type")


def insert_production(session, df):
    """
    Insert production country information into the database.

    Args:
        session (sqlalchemy.orm.Session): A SQLAlchemy database session.
        df (pd.DataFrame): The DataFrame containing production country data.

    Returns:
        None
    """
    insert_entity(
        session, df, "production_countries", Production, "country", filter_value="XX"
    )


def insert_media(session, df):
    """
    Insert media information into the database.

    Args:
        session (sqlalchemy.orm.Session): A SQLAlchemy database session.
        df (pd.DataFrame): The DataFrame containing media data.

    Returns:
        None
    """
    # Drop duplicates based on the 'title' column
    filtered_df = df.drop_duplicates(subset=["title"])

    try:
        media_instances = [
            Media(
                id=row["id"],
                title=row["title"],
                type=row["type"],  # Ensure this matches enum values in the database
                release_year=row["release_year"],
                age_certification=row["age_certification"],
                runtime=row["runtime"],
                seasons=row["seasons"],
                imdb_score=row["imdb_score"],
                imdb_votes=row["imdb_votes"],
            )
            for index, row in filtered_df.iterrows()
        ]

        # Bulk insert the prepared media instances
        session.bulk_save_objects(media_instances)
        session.commit()
        logger.info("Media table - finished.")

    except Exception as e:
        logger.exception(f"An error occurred while uploading to the database: {e}")
        session.rollback()
        raise

    finally:
        session.close()


# RELATIONS
def retrieve_media_instances(session, media_ids):
    """
    Retrieve media instances by their IDs.

    Args:
        session (sqlalchemy.orm.Session): A SQLAlchemy database session.
        media_ids (list): A list of media IDs to retrieve.

    Returns:
        dict: A dictionary mapping media IDs to media instances.
    """
    return {
        media.id: media
        for media in session.query(Media).filter(Media.id.in_(media_ids)).all()
    }


def retrieve_existing_entities(session, EntityModel, entity_names):
    """
    Retrieve existing entities by their names.

    Args:
        session (sqlalchemy.orm.Session): A SQLAlchemy database session.
        EntityModel (sqlalchemy.ext.declarative.api.DeclarativeBase): The SQLAlchemy class representing the entity.
        entity_names (list): A list of entity names to retrieve.

    Returns:
        dict: A dictionary mapping entity names to entity instances.
    """
    entities = (
        session.query(EntityModel)
        .filter(EntityModel.name.in_(entity_names))
        .options(load_only(EntityModel.name))
        .all()
    )
    return {entity.name.strip(): entity for entity in entities}


def create_relationships(
        session, entity_data, media_dict, entity_dict, relationship_attr
):
    """
    Create relationships between media and entities.

    Args:
        session (sqlalchemy.orm.Session): A SQLAlchemy database session.
        entity_data (pd.DataFrame): A DataFrame containing entity data.
        media_dict (dict): A dictionary mapping media IDs to media instances.
        entity_dict (dict): A dictionary mapping entity names to entity instances.
        relationship_attr (str): The name of the relationship attribute in the Media class.

    Returns:
        None
    """
    for _, row in entity_data.iterrows():
        media_id = row["id"]
        entity_name = row["name"].strip()

        media = media_dict.get(media_id)
        if media:
            entity = entity_dict.get(entity_name)
            if entity:
                getattr(media, relationship_attr).append(entity)


def insert_relationships(session, df, role, EntityModel, relationship_attr):
    """
    Insert relationships between media and entities based on the role.

    Args:
        session (sqlalchemy.orm.Session): A SQLAlchemy database session.
        df (pd.DataFrame): The DataFrame containing relationship data.
        role (str): The role of the entities (e.g., "ACTOR" or "DIRECTOR").
        EntityModel (sqlalchemy.ext.declarative.api.DeclarativeBase): The SQLAlchemy class representing the entity.
        relationship_attr (str): The name of the relationship attribute in the Media class.

    Returns:
        None
    """
    entity_data = df[df["role"] == role][["id", "name"]]

    try:
        media_ids = entity_data["id"].tolist()
        media_dict = retrieve_media_instances(session, media_ids)

        entity_names = entity_data["name"].apply(lambda x: x.strip()).tolist()
        entity_dict = retrieve_existing_entities(session, EntityModel, entity_names)

        create_relationships(
            session, entity_data, media_dict, entity_dict, relationship_attr
        )
        session.commit()
        logger.info(f"Media-{role} relationships - finished.")

    except SQLAlchemyError as e:
        logger.exception(
            f"An error occurred while inserting Media-{role} relationships: {e}"
        )
        session.rollback()
        raise

    finally:
        session.close()


def insert_media_actors_relations(session, df):
    """
    Insert relationships between media and actors.

    Args:
        session (sqlalchemy.orm.Session): A SQLAlchemy database session.
        df (pd.DataFrame): The DataFrame containing actor relationship data.

    Returns:
        None
    """
    insert_relationships(session, df, "ACTOR", Actor, "actor")


def insert_media_directors_relations(session, df):
    """
    Insert relationships between media and directors.

    Args:
        session (sqlalchemy.orm.Session): A SQLAlchemy database session.
        df (pd.DataFrame): The DataFrame containing director relationship data.

    Returns:
        None
    """
    insert_relationships(session, df, "DIRECTOR", Director, "director")


def insert_media_genre_relations(session, df):
    """
    Insert relationships between media and genres.

    Args:
        session (sqlalchemy.orm.Session): A SQLAlchemy database session.
        df (pd.DataFrame): The DataFrame containing genre relationship data.

    Returns:
        None
    """
    df = df.drop_duplicates(subset=["title"])
    media_ids = df["id"].tolist()
    media_dict = retrieve_media_instances(session, media_ids)

    genre_types = df["genres"].apply(lambda x: x.strip()).tolist()
    existing_genres = session.query(Genre).options(load_only(Genre.genre_type)).all()
    existing_genres_types = {
        genre.genre_type.strip(): genre for genre in existing_genres
    }

    try:
        for _, row in df.iterrows():
            media_id = row["id"]
            genre_list_string = row["genres"]
            genre_list = ast.literal_eval(genre_list_string)
            genre_list = [genre.strip() for genre in genre_list]

            media = media_dict.get(media_id)
            if media:
                for genre_type in genre_list:
                    genre = existing_genres_types.get(genre_type)
                    if genre:
                        media.genre.append(genre)
        session.commit()
        logger.info(f"Media-Genre relationships - finished.")

    except SQLAlchemyError as e:
        logger.exception(
            "An error occurred while inserting Media-Genre relationships: {}".format(e)
        )
        session.rollback()
        raise
    finally:
        session.close()


def insert_media_production_relations(session, df):
    """
    Insert relationships between media and production countries.

    Args:
        session (sqlalchemy.orm.Session): A SQLAlchemy database session.
        df (pd.DataFrame): The DataFrame containing production country relationship data.

    Returns:
        None
    """
    df = df.drop_duplicates(subset=["title"])
    media_ids = df["id"].tolist()
    media_dict = retrieve_media_instances(session, media_ids)

    countries = df["production_countries"].apply(lambda x: x.strip()).tolist()
    existing_countries = (
        session.query(Production).options(load_only(Production.country_id)).all()
    )
    existing_countries_id = {
        country.country.strip(): country for country in existing_countries
    }

    try:
        for _, row in df.iterrows():
            media_id = row["id"]
            country_list_string = row["production_countries"]
            country_list = ast.literal_eval(country_list_string)
            country_list = [country.strip() for country in country_list]

            media = media_dict.get(media_id)
            if media:
                for country_id in country_list:
                    country_id = existing_countries_id.get(country_id)
                    if country_id:
                        media.production.append(country_id)
        session.commit()
        logger.info(f"Media-Genre relationships - finished.")

    except SQLAlchemyError as e:
        logger.exception(
            "An error occurred while inserting Media-Genre relationships: {}".format(e)
        )
        session.rollback()
        raise
    finally:
        session.close()
