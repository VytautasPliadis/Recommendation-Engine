from enum import Enum
from typing import Optional

import pydantic as pydantic


class CreateActor(pydantic.BaseModel):
    name: str


class Actor(CreateActor):
    actor_id: int


class CreateDirector(pydantic.BaseModel):
    name: str


class Director(CreateDirector):
    director_id: int


class MediaType(Enum):
    MOVIE = "MOVIE"
    SHOW = "SHOW"


class Media(pydantic.BaseModel):
    id: str
    title: str
    type: MediaType
    release_year: int
    age_certification: str
    runtime: int
    seasons: Optional[int]
    imdb_score: Optional[float]
    imdb_votes: Optional[int]

    class Config:
        from_attributes = True


class MediaRecommendation(pydantic.BaseModel):
    title: str
    release_year: int
