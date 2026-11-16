from models.base_models import MovieCreate
from utils.data_generator import DataGenerator
from random import randint, choice

def generate_film_data(**kwargs) -> MovieCreate:
    data = {
        "name": DataGenerator.generate_film_name(),
        "price": DataGenerator.generate_price(),
        "description": DataGenerator.generate_film_description(),
        "imageUrl": "https://image.url",
        "location": choice(['MSK', "SPB"]),
        "published": choice([True, False]),
        "genreId": randint(5, 10),
    }
    data.update(kwargs)
    return MovieCreate(**data)

def generate_movie_db_data(**kwargs) -> dict:
    data = {
        "name": DataGenerator.generate_film_name(),
        "price": DataGenerator.generate_price(),
        "description": DataGenerator.generate_film_description(),
        "image_url": "https://image.url",
        "location": choice(['MSK', "SPB"]),
        "published": choice([True, False]),
        "rating": randint(0,5),
        "genre_id": randint(5, 10),
        "created_at": DataGenerator.generate_creation_date()
    }
    data.update(kwargs)
    return data
