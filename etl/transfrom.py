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

            self._process_role(film_id, detail, films)
            if detail["genre_name"] is not None:
                films[film_id]["genre"].add(detail["genre_name"])

        for film in films.values():
            film["genre"] = list(film["genre"])

        return [FilmworkModel(**film) for film in films.values()]

    def _process_role(self, film_id: str, detail: dict[str, Any], films: dict[str, Any]) -> None:
        role = detail["role"]
        person = {"id": detail["person_id"], "name": detail["full_name"]}
        full_name = detail["full_name"]

        if role == "actor" and person not in films[film_id]["actors"]:
            films[film_id]["actors"].append(person)
            films[film_id]["actors_names"].append(full_name)

        elif role == "writer" and person not in films[film_id]["writers"]:
            films[film_id]["writers"].append(person)
            films[film_id]["writers_names"].append(full_name)

        elif role == "director" and full_name not in films[film_id]["director"]:
            films[film_id]["director"].append(full_name)
