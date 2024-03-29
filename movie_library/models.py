from dataclasses import dataclass, field
from datetime import datetime
from re import S

# This is a code generator
# adds extra methods: wrapper, init, comparison between object
# dataclass module
@dataclass
class Movie:

    # First the required properties:
    _id: str
    title: str
    director: str
    year: int

    # Secondly the optional properties (these are set to default):
    cast: list[str] = field(default_factory=list)
    series: list[str] = field(default_factory=list)
    last_watched: datetime = None
    rating: int = 0
    tags: list[str] = field(default_factory=list)
    description: str = None
    video_link: str = None 

@dataclass
class User:
    _id: str
    email: str
    password: str
    movies: list[str] = field(default_factory=list)
