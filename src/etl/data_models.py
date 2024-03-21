from sqlalchemy import Column, Integer, String, Table, ForeignKey, Numeric, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

media_actor_association = Table(
    "media_actor",
    Base.metadata,
    Column("media_id", String(9), ForeignKey("media.id")),
    Column("actor_id", Integer, ForeignKey("actor.actor_id")),
)

media_director_association = Table(
    "media_director",
    Base.metadata,
    Column("media_id", String(9), ForeignKey("media.id")),
    Column("director_id", Integer, ForeignKey("director.director_id")),
)

media_genre_association = Table(
    "media_genre",
    Base.metadata,
    Column("media_id", String(9), ForeignKey("media.id")),
    Column("genre_id", Integer, ForeignKey("genre.genre_id")),
)

media_production_association = Table(
    "media_production",
    Base.metadata,
    Column("media_id", String(9), ForeignKey("media.id")),
    Column("country_id", Integer, ForeignKey("production.country_id")),
)


class Genre(Base):
    __tablename__ = "genre"
    genre_id = Column(Integer, primary_key=True)
    genre_type = Column(String(15), unique=True, index=True)

    media = relationship(
        "Media", secondary=media_genre_association, back_populates="genre"
    )


class Production(Base):
    __tablename__ = "production"
    country_id = Column(Integer, primary_key=True)
    country = Column(String(2), nullable=True, unique=True)

    media = relationship(
        "Media", secondary=media_production_association, back_populates="production"
    )


class Actor(Base):
    __tablename__ = "actor"
    actor_id = Column(Integer, primary_key=True)
    name = Column(String(80), unique=True, nullable=False)

    media = relationship(
        "Media", secondary=media_actor_association, back_populates="actor"
    )


class Director(Base):
    __tablename__ = "director"
    director_id = Column(Integer, primary_key=True)
    name = Column(String(80), unique=True, nullable=False)

    media = relationship(
        "Media", secondary=media_director_association, back_populates="director"
    )


class Media(Base):
    __tablename__ = "media"
    id = Column(String(9), primary_key=True)
    title = Column(String(105), unique=True, nullable=False)
    type = Column("media_type", Enum("MOVIE", "SHOW", name="type"))
    release_year = Column(Integer)
    age_certification = Column(String(5))
    runtime = Column(Integer)
    seasons = Column(Numeric(precision=4, scale=2), nullable=True)
    imdb_score = Column(Numeric(precision=3, scale=2), nullable=True)
    imdb_votes = Column(Integer)

    actor = relationship(
        "Actor", secondary=media_actor_association, back_populates="media"
    )
    director = relationship(
        "Director", secondary=media_director_association, back_populates="media"
    )
    genre = relationship(
        "Genre", secondary=media_genre_association, back_populates="media"
    )
    production = relationship(
        "Production", secondary=media_production_association, back_populates="media"
    )
