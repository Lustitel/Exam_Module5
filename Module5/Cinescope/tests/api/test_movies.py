import allure
import pytest

from data.movies.film_data import generate_film_data
from models.base_models import MovieResponse, MoviesListResponse
from utils.check_movie_response_request_equality import movie_response_request_missmatch


@allure.epic("Тестирование api movies")
@allure.feature("Тестирование получения всех фильмов")
class TestGetMovies:

    @allure.title("Функция проверки наличия всех необходимых полей у ответа get /movies")
    @pytest.mark.api
    @pytest.mark.smoke
    def test_validate_movies_fields(self, session_user):
        response = session_user.api.movies_api.get_movies().json()
        response_data = MoviesListResponse(**response)

        assert response_data


@allure.epic("Тестирование api movies")
@allure.feature("Тестирование фильтрации фильмов")
class TestGetMoviesFiltersPositive:

    @allure.title("Проверка получения списка фильмов без фильтров")
    @pytest.mark.api
    @pytest.mark.smoke
    @pytest.mark.filters
    @pytest.mark.positive
    def test_no_filter(self, session_user):
        test_filters = {}
        response = session_user.api.movies_api.get_movies(params=test_filters)
        response_data = MoviesListResponse(**response.json())

        assert len(response_data.movies) > 0

    @allure.title("Проверка фильтрации по размеру страницы (pageSize)")
    @pytest.mark.api
    @pytest.mark.smoke
    @pytest.mark.filters
    @pytest.mark.positive
    def test_filter_page_size(self, session_user):
        page_size = 1
        test_filters = {"pageSize": page_size}
        response = session_user.api.movies_api.get_movies(params=test_filters).json()
        response_data = MoviesListResponse(**response)

        assert response_data.pageSize == page_size
        assert len(response_data.movies) == page_size

    @allure.title("Проверка пагинации по номеру страницы (page)")
    @pytest.mark.api
    @pytest.mark.smoke
    @pytest.mark.filters
    @pytest.mark.positive
    def test_filter_page_number(self, session_user):
        page_number = 10
        test_filters = {"page": page_number}
        response = session_user.api.movies_api.get_movies(params=test_filters).json()
        response_data = MoviesListResponse(**response)

        assert len(response_data.movies) > 0
        assert response_data.page == page_number

    @allure.title("Проверка фильтрации фильмов по диапазону цен (minPrice, maxPrice)")
    @pytest.mark.api
    @pytest.mark.smoke
    @pytest.mark.filters
    @pytest.mark.positive
    def test_filter_price(self, session_user):
        min_price = 1
        max_price = 2000
        test_filters = {"minPrice": min_price, "maxPrice": max_price}
        response = session_user.api.movies_api.get_movies(params=test_filters).json()
        response_data = MoviesListResponse(**response)

        assert len(response_data.movies) > 0
        assert all(min_price <= movie.price <= max_price for movie in response_data.movies)

    @allure.title("Проверка фильтрации фильмов по локации (locations)")
    @pytest.mark.api
    @pytest.mark.smoke
    @pytest.mark.filters
    @pytest.mark.positive
    def test_filter_locations(self, session_user):
        locations = "MSK"
        test_filters = {"locations": locations}
        response = session_user.api.movies_api.get_movies(params=test_filters).json()
        response_data = MoviesListResponse(**response)

        assert len(response_data.movies) > 0
        assert all(movie.location == locations for movie in response_data.movies)

    @allure.title("Проверка фильтрации фильмов по статусу публикации (published)")
    @pytest.mark.api
    @pytest.mark.smoke
    @pytest.mark.filters
    @pytest.mark.positive
    @pytest.mark.parametrize("status,expected_status", [("true", True), ("false", False)], ids=["published_true", "published_false"])
    def test_filter_published_status(self, session_user, status, expected_status):
        response = session_user.api.movies_api.get_movies(params={"published": f"{status}"}).json()
        response_data = MoviesListResponse(**response)

        assert len(response_data.movies) > 0, "Опубликованные фильмы не найдены"
        assert all(movie.published is expected_status for movie in response_data.movies)

    @allure.title("Проверка фильтрации фильмов по жанру (genreId)")
    @pytest.mark.api
    @pytest.mark.smoke
    @pytest.mark.filters
    @pytest.mark.positive
    def test_filter_genre_id(self, session_user):
        genre_id = 5
        response = session_user.api.movies_api.get_movies(params={"genreId": genre_id}).json()
        response_data = MoviesListResponse(**response)

        assert len(response_data.movies) > 0, f"Фильмы с id жанра: {genre_id} не найдены"
        assert all(movie.genreId == genre_id for movie in response_data.movies)

    @allure.title("Проверка сортировки фильмов по дате создания по возрастанию (createdAt=asc)")
    @pytest.mark.api
    @pytest.mark.smoke
    @pytest.mark.filters
    @pytest.mark.positive
    def test_filter_show_order_asc(self, session_user):
        created_at = "asc"
        response = session_user.api.movies_api.get_movies(params={"createdAt": created_at}).json()
        response_data = MoviesListResponse(**response)
        movies_created_at = [movie.createdAt for movie in response_data.movies]

        assert len(response_data.movies) > 0, "Фильмы не найдены"
        assert movies_created_at == sorted(movies_created_at)

    @allure.title("Проверка сортировки фильмов по дате создания по убыванию (createdAt=desc)")
    @pytest.mark.api
    @pytest.mark.smoke
    @pytest.mark.filters
    @pytest.mark.positive
    def test_filter_show_order_desc(self, session_user):
        created_at = "desc"
        response = session_user.api.movies_api.get_movies(params={"createdAt": created_at}).json()
        response_data = MoviesListResponse(**response)
        movies_created_at = [movie.createdAt for movie in response_data.movies]

        assert len(response_data.movies) > 0, "Фильмы не найдены"
        assert movies_created_at == sorted(movies_created_at, reverse=True)

    @allure.title("Проверка фильтрации при максимальном граничном значении maxPrice")
    @pytest.mark.api
    @pytest.mark.smoke
    @pytest.mark.filters
    @pytest.mark.positive
    def test_max_price_max_value(self, session_user):
        max_int = 2**31 - 1
        response = session_user.api.movies_api.get_movies(params={"maxPrice": max_int})
        response_data = MoviesListResponse(**response.json())

        assert len(response_data.movies) > 0
        assert all(movie.price <= max_int for movie in response_data.movies)


@allure.epic("Тестирование api movies")
@allure.feature("Тестирование фильтрации фильмов")
class TestGetMoviesFiltersNegative:

    @allure.title("Проверка ошибки при передаче pageSize меньше минимального значения (0)")
    @pytest.mark.api
    @pytest.mark.filters
    @pytest.mark.negative
    def test_page_size_min_boundary(self, session_user):
        response_data = session_user.api.movies_api.get_movies(params={"pageSize": 0}, expected_status=400)

        assert response_data.json() == {'message': ['Поле pageSize имеет минимальную величину 1'], 'error': 'Bad Request', 'statusCode': 400}

    @allure.title("Проверка ошибки при передаче отрицательного pageSize (-1)")
    @pytest.mark.api
    @pytest.mark.filters
    @pytest.mark.negative
    def test_page_size_invalid_value(self, session_user):
        response_data = session_user.api.movies_api.get_movies(params={"pageSize": -1}, expected_status=400)

        assert response_data.json() == {'message': ['Поле pageSize имеет минимальную величину 1'], 'error': 'Bad Request', 'statusCode': 400}

    @allure.title("Проверка ошибки при превышении максимального значения pageSize (21)")
    @pytest.mark.api
    @pytest.mark.filters
    @pytest.mark.negative
    def test_page_size_max_boundary(self, session_user):
        response_data = session_user.api.movies_api.get_movies(params={"pageSize": 21}, expected_status=400)

        assert response_data.json() == {'message': ['Поле pageSize имеет максимальную величину 20'], 'error': 'Bad Request', 'statusCode': 400}

    @allure.title("Проверка ошибки при передаче minPrice меньше минимального значения (0)")
    @pytest.mark.api
    @pytest.mark.filters
    @pytest.mark.negative
    def test_min_price_min_boundary(self, session_user):
        response_data = session_user.api.movies_api.get_movies(params={"minPrice": 0}, expected_status=400)

        assert response_data.json() == {'message': ['Поле minPrice имеет минимальную величину 1'], 'error': 'Bad Request', 'statusCode': 400}

    @allure.title("Проверка ошибки при передаче minPrice равного дефолтному maxPrice (1000)")
    @pytest.mark.api
    @pytest.mark.filters
    @pytest.mark.negative
    def test_min_price_max_boundary_without_max_price(self, session_user):
        response_data = session_user.api.movies_api.get_movies(params={"minPrice": 1000}, expected_status=400)

        assert response_data.json() == {
            "message": "minPrice must be less than maxPrice",
            "error": "Bad Request",
            "statusCode": 400
        }, "Значение minPrice не должно превышать или равняться дефолтному значению maxPrice=1000"

    @allure.title("Проверка ошибки при передаче maxPrice равного 0")
    @pytest.mark.api
    @pytest.mark.filters
    @pytest.mark.negative
    def test_max_price_min_boundary(self, session_user):
        response_data = session_user.api.movies_api.get_movies(params={"maxPrice": 0}, expected_status=400)

        assert response_data.json() == {'message': 'minPrice must be less than maxPrice', 'error': 'Bad Request', 'statusCode': 400}

    @allure.title("Проверка ошибки, когда maxPrice меньше minPrice")
    @pytest.mark.api
    @pytest.mark.filters
    @pytest.mark.negative
    def test_max_price_less_min_price(self, session_user):
        response_data = session_user.api.movies_api.get_movies(params={"minPrice": 2, "maxPrice": 1}, expected_status=400)

        assert response_data.json() == {'message': 'minPrice must be less than maxPrice', 'error': 'Bad Request', 'statusCode': 400}

    @allure.title("Проверка ошибки при превышении максимального int для maxPrice")
    @pytest.mark.api
    @pytest.mark.filters
    @pytest.mark.negative
    def test_max_price_max_boundary(self, session_user):
        over_max_int = 2**31
        response_data = session_user.api.movies_api.get_movies(params={"maxPrice": over_max_int}, expected_status=400)

        assert response_data.json() in [
            {'error': 'Bad Request', 'message': 'Некорректные данные', 'statusCode': 400},
            {'message': 'Bad Request', 'statusCode': 400}
        ]


@allure.epic("Тестирование api movies")
@allure.feature("Тестирование создания фильмов")
class TestCreateMoviesPositive:

    @allure.title("Функция проверки создания фильма при валидном теле")
    @pytest.mark.api
    @pytest.mark.smoke
    @pytest.mark.flaky
    @pytest.mark.positive
    @pytest.mark.creation
    @pytest.mark.db
    def test_create_film(self, super_admin, test_film, db_helper):

        with allure.step(f"API: создание фильма {test_film}"):
            response = super_admin.api.movies_api.create_movie(test_film)
            created_movie = MovieResponse(**response.json())

        mismatches = movie_response_request_missmatch(test_film, created_movie)
        assert not mismatches, f"Следующие поля созданного фильма не совпали: {mismatches}"

        with allure.step(f"БД: создание фильма {test_film} с корректными данными"):
            movie_from_db = db_helper.get_movie_by_id(created_movie.id)
            assert movie_from_db is not None
            assert created_movie.id == movie_from_db.id
            assert created_movie.name == movie_from_db.name
            assert created_movie.price == movie_from_db.price
            assert created_movie.description == movie_from_db.description


@allure.epic("Тестирование api movies")
@allure.feature("Тестирование создания фильмов")
@allure.story("Проверка негативных сценариев создания фильмов")
@allure.description("Тест проверяет, корректно обрабатываются ошибки при передаче невалидного тела фильма")
class TestCreateMoviesNegative:

    @allure.title("Функция проверки выброса ошибки при наличии недостающих полей в теле movie")
    @pytest.mark.api
    @pytest.mark.negative
    @pytest.mark.creation
    @pytest.mark.db
    @pytest.mark.parametrize("movie_field", ["name", "price", "description", "location", "published", "genreId"])
    def test_create_film_missing_fields(self, super_admin, test_film, movie_field, db_helper):
        with allure.step(f"Создание фильма с отсутствующими полями: {movie_field}"):
            missing_field = test_film.model_dump(mode="json")
            missing_field.pop(movie_field)

        with allure.step(f"API: Создание фильма {test_film}"):
            response_data = super_admin.api.movies_api.create_movie(missing_field, expected_status=400).json()

        with allure.step(f"БД: Попытка создать фильм {test_film}"):
            movie_from_db = db_helper.movie_exists_by_name(test_film.name)

        assert response_data["statusCode"] == 400
        assert response_data["error"] == "Bad Request"
        assert any(movie_field in msg for msg in response_data["message"]), (
            f"В сообщении об ошибке не найдено поле '{movie_field}': {response_data['message']}"
        )
        assert not movie_from_db

    @allure.title("Функция проверки выброса ошибки при дублировании поля name в теле movie")
    @pytest.mark.api
    @pytest.mark.negative
    @pytest.mark.db
    @pytest.mark.creation
    def test_create_film_duplicate_name(self, super_admin, test_film, db_helper):
        with allure.step(f"API: Создание первого фильма {test_film}"):
            first_response = super_admin.api.movies_api.create_movie(test_film).json()
            first_created_movie = MovieResponse(**first_response)

        with allure.step(f"API: Создание второго фильма {test_film} с дублирующимся названием"):
            second_film = generate_film_data(name=test_film.name)
            response_data = super_admin.api.movies_api.create_movie(second_film, expected_status=409).json()
            assert response_data == {'message': 'Фильм с таким названием уже существует', 'error': 'Conflict',
                                     'statusCode': 409}
        with allure.step(f"БД: создание первого фильма {test_film} с корректными данными"):
            movie_from_db = db_helper.get_movie_by_id(first_created_movie.id)
            assert movie_from_db is not None
            assert movie_from_db.description == first_created_movie.description

    @allure.title("Функция проверки выброса ошибки при передаче невалидного значения для поля фильма")
    @pytest.mark.api
    @pytest.mark.negative
    @pytest.mark.creation
    @pytest.mark.db
    @pytest.mark.parametrize("movie_field,field_value", [
        ("name", 123),
        ("price", "price"),
        ("description", 21),
        ("location", 34),
        ("published", "bober"),
        ("genreId", "wow")
    ])
    def test_create_film_invalid_field_type(self, super_admin, test_film, movie_field, field_value, db_helper):

        with allure.step(f"API: Попытка создать фильм с невалидными данными: {movie_field}: {field_value}"):
            invalid_movie = test_film.model_dump(mode="json")
            invalid_movie[movie_field] = field_value
            response_data = super_admin.api.movies_api.create_movie(invalid_movie, expected_status=400).json()
            assert response_data["statusCode"] == 400
            assert response_data["error"] == "Bad Request"
            assert any(movie_field in msg for msg in response_data["message"]), (
                f"Имя поля '{movie_field}' не найдено в сообщениях об ошибке: {response_data['message']}"
            )

        with allure.step(f"БД: Попытка создать фильм {test_film}"):
            movie_from_db = db_helper.movie_exists_by_name(test_film.name)
            assert not movie_from_db

    @allure.title("Функция проверки выброса ошибки при попытке создать фильм без соответствующих прав")
    @pytest.mark.api
    @pytest.mark.negative
    @pytest.mark.creation
    @pytest.mark.db
    def test_user_role_creation_denied(self, common_user, test_film, db_helper):
        response = common_user.api.movies_api.create_movie(test_film, expected_status=403)
        movie_from_db = db_helper.movie_exists_by_name(test_film.name)

        assert response.json() == {'error': 'Forbidden', 'message': 'Forbidden resource', 'statusCode': 403}
        assert not movie_from_db


@allure.epic("Тестирование api movies")
@allure.feature("Тестирование получения фильма по его id")
class TestGetMovieViaId:

    @allure.title("Проверка успешного получения фильма по его id")
    @pytest.mark.api
    @pytest.mark.smoke
    @pytest.mark.positive
    def test_get_film_via_id(self, session_user, created_film):
        movie_id = created_film.id
        response_data = session_user.api.movies_api.get_movies_id(movie_id, timeout=5).json()
        movie_get_by_id = MovieResponse(**response_data)

        mismatches = movie_response_request_missmatch(created_film, movie_get_by_id)
        assert not mismatches, f"Следующие поля созданного фильма не совпали: {mismatches}"
        assert movie_get_by_id.id == created_film.id

    @allure.title("Проверка ошибки 404 при запросе фильма с несуществующим id")
    @pytest.mark.api
    @pytest.mark.negative
    def test_get_film_invalid_id(self, session_user):
        response_data = session_user.api.movies_api.get_movies_id(0, expected_status=404)

        assert response_data.json() in [
            {'message': 'Фильм не найден', 'error': 'Not Found', 'statusCode': 404},
            {'message': 'Not Found', 'statusCode': 404}
        ]

    @allure.title("Проверка ошибки при передаче невалидного типа id")
    @pytest.mark.api
    @pytest.mark.negative
    def test_get_film_invalid_id_type(self, session_user):
        response_data = session_user.api.movies_api.get_movies_id("uwu", expected_status=500)

        assert response_data.json() == {'message': 'Internal server error', 'statusCode': 500}


@allure.epic("Тестирование api movies")
@allure.feature("Тестирование удаления фильмов")
class TestDeleteMovie:

    @allure.title("Проверка ролевой модели при удалении фильма")
    @pytest.mark.api
    @pytest.mark.smoke
    @pytest.mark.db
    @pytest.mark.parametrize(
        "role,status,movie_delete_from_db_expected",
        [("common_user", 403, False), ("admin", 403, False), ("super_admin", 200, True)],
        ids=["User", "Admin", "Super Admin"]
    )
    def test_delete_movie(self, role, status, created_film, request, db_helper, movie_delete_from_db_expected):
        with allure.step("Подготовка тестовых данных"):
            movie_id = created_film.id
            user_role = request.getfixturevalue(role)
            get_status_after_delete_attempt = 404 if status == 200 else 200

        with allure.step("API: удаление фильма"):
            response_delete = user_role.api.movies_api.delete_movie(movie_id, timeout=5, expected_status=status)
            response_get = user_role.api.movies_api.get_movies_id(movie_id, timeout=5, expected_status=get_status_after_delete_attempt)
            movie_from_db = db_helper.get_movie_by_id(movie_id)
            movie_deleted_from_db = movie_from_db is None
            assert response_delete.status_code == status
            assert response_get.status_code == get_status_after_delete_attempt
            assert movie_deleted_from_db is movie_delete_from_db_expected

    @allure.title("Проверка ошибки 404 при удалении фильма с несуществующим id")
    @pytest.mark.api
    @pytest.mark.negative
    @pytest.mark.db
    def test_delete_movie_invalid_id(self, super_admin, db_helper):
        movie_id = 0
        response = super_admin.api.movies_api.delete_movie(movie_id, expected_status=404)
        movie_from_db = db_helper.get_movie_by_id(movie_id)

        assert response.json() in [
            {'message': 'Фильм не найден', 'error': 'Not Found', 'statusCode': 404},
            {'message': 'Not Found', 'statusCode': 404}
        ]
        assert movie_from_db is None


@allure.epic("Тестирование api movies")
@allure.feature("Тестирование частичного обновления фильмов")
class TestPatchMovie:

    @allure.title("Функция проверки успешного patch")
    @pytest.mark.api
    @pytest.mark.smoke
    @pytest.mark.positive
    @pytest.mark.db
    def test_patch_movie(self, super_admin, created_film, db_helper):
        with allure.step("Создание данных для обновления фильма"):
            movie_id = created_film.id
            new_name = f"{created_film.name} 2"
            patch_payload = {"name": new_name}

        with allure.step("Обновления фильма"):
            response_data = super_admin.api.movies_api.patch_movie(movie_id, patch_payload).json()
            patched_movie = MovieResponse(**response_data)
            movie_from_db = db_helper.get_movie_by_id(movie_id)
            assert patched_movie.name == new_name
            assert movie_from_db is not None
            assert movie_from_db.name == new_name

        mismatches = movie_response_request_missmatch(created_film, patched_movie)
        assert len(mismatches) == 1 and "name" in mismatches, (
            f"Ожидалось изменение только поля 'name', но изменились: {mismatches}"
        )


    @allure.title("Функция проверки выброса ошибки при невалидном id")
    @pytest.mark.api
    @pytest.mark.negative
    @pytest.mark.parametrize(
        "invalid_id",
        [0, -1, 2**31],
        ids=["Zero id", "Negative id", "Max int id"]
    )
    def test_patch_movie_invalid_id(self, super_admin, created_film, invalid_id):
        new_name = f"{created_film.name} 2"
        patch_data = {"name": new_name}
        response = super_admin.api.movies_api.patch_movie(invalid_id, patch_data, expected_status=404)

        assert response.json() in [
            {'message': 'Фильм не найден', 'error': 'Not Found', 'statusCode': 404},
            {'message': 'Not Found', 'statusCode': 404}
        ]

    @allure.title("Функция проверки выброса ошибки при невалидном теле фильма")
    @pytest.mark.api
    @pytest.mark.negative
    @pytest.mark.parametrize("movie_field,field_value", [
        ("name", 123),
        ("price", "price"),
        ("description", 21),
        ("location", 34),
        ("published", "bober"),
        ("genreId", "wow")
    ])
    def test_patch_movie_invalid_payload(self, super_admin, created_film, movie_field, field_value):
        movie_id = created_film.id
        invalid_payload = {movie_field: field_value}
        response_data = super_admin.api.movies_api.patch_movie(movie_id, invalid_payload, expected_status=400).json()

        assert response_data["statusCode"] == 400
        assert response_data["error"] == "Bad Request"
        assert any(movie_field in msg for msg in response_data["message"]), (
            f"Имя поля '{movie_field}' не найдено в сообщениях об ошибке: {response_data['message']}"
        )