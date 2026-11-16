from custom_requester.custom_requester import CustomRequester
from config.base_urls import API_BASE_URL
import allure

MOVIES = "/movies"
REVIEWS = "/reviews"
GENRES = "/genres"

class MoviesApi(CustomRequester):
    def __init__(self, session):
        super().__init__(session=session, base_url=API_BASE_URL)

    @allure.step("API: Получение списка фильмов с параметрами {params}")
    def get_movies(self, expected_status=200, params=None, **kwargs):
        return self.send_request("GET", MOVIES, params=params, expected_status=expected_status, **kwargs)

    @allure.step("API: Получение фильма по id={movie_id} с параметрами {params}")
    def get_movies_id(self, movie_id=None, expected_status=200, params=None, **kwargs):
        return self.send_request("GET", f"{MOVIES}/{movie_id}", params=params, expected_status=expected_status, **kwargs)

    @allure.step("API: Создание фильма с данными {film_data}")
    def create_movie(self, film_data, expected_status=201, params=None, **kwargs):
        return self.send_request("POST", MOVIES, data=film_data, params=params, expected_status=expected_status, **kwargs)

    @allure.step("API: Удаление фильма с id={movie_id}")
    def delete_movie(self, movie_id, expected_status=200, params=None, **kwargs):
        return self.send_request("DELETE", f"{MOVIES}/{movie_id}", params=params, expected_status=expected_status, **kwargs)

    @allure.step("API: Частичное обновление фильма с id={movie_id} новыми данными {film_data}")
    def patch_movie(self, movie_id, film_data, expected_status=200, params=None, **kwargs):
        return self.send_request("PATCH", f"{MOVIES}/{movie_id}", data=film_data, params=params, expected_status=expected_status, **kwargs)

