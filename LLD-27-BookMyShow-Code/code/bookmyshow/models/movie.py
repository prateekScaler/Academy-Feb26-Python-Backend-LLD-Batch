"""Movie — a value object: title + language, no behaviour. Shared across shows."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Movie:
    movie_id: str
    title: str
    language: str
