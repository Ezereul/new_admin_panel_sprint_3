from typing import Any

from etl.models import FilmworkModel


class DataTransform:
    def consolidate_films(self, film_details: list[dict[str, Any]]) -> list[FilmworkModel]:
        films = {}
        for detail in film_details:
            film_id = detail["fw_id"]
            if film_id not in films:
                films[film_id] = {
                    "id": film_id,
                    "imdb_rating": detail["rating"],
                    "genre": set(),
                    "title": detail["title"],
                    "description": detail["description"],
                    "director": [],
                    "actors_names": [],
                    "writers_names": [],
                    "actors": [],
                    "writers": [],
                }
            role = detail["role"]
            if role == "actor":
                actor = {"id": detail["person_id"], "name": detail["full_name"]}
                if actor not in films[film_id]["actors"]:
                    films[film_id]["actors"].append(actor)
                    films[film_id]["actors_names"].append(detail["full_name"])
            elif role == "writer":
                writer = {"id": detail["person_id"], "name": detail["full_name"]}
                if writer not in films[film_id]["writers"]:
                    films[film_id]["writers"].append(writer)
                    films[film_id]["writers_names"].append(detail["full_name"])
            elif role == "director":
                films[film_id]["director"].append(detail["full_name"])
            films[film_id]["genre"].add(detail["genre_name"] or set())

        for film in films.values():
            film["genre"] = list(film["genre"])

        return [FilmworkModel(**film) for film in films.values()]
