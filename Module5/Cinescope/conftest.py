import time

import pytest
import requests

from typing import Iterator

from requests import Session

from clients.api_manager import ApiManager
from data.movies.film_data import generate_film_data
from data.movies.reviews_data import generate_review
from data.auth.register_data import get_register_payload, generate_user_db_data
from data.movies.film_data import generate_movie_db_data
from models.base_models import MovieResponse, MovieCreate
from resources.user_creds import SuperAdminCreds
from entities.user import User
from constants.roles import Roles
from Module5.models.base_models import TestUser

from db_requester.db_client import get_db_session
from db_requester.db_helper import DBHelper


@pytest.fixture(scope="session")
def session() -> Iterator[Session]:
    session = requests.Session()
    yield session
    session.close()

@pytest.fixture(scope="session")
def api_manager(session):
    return ApiManager(session)

@pytest.fixture
def test_user() -> TestUser:
    return get_register_payload()

@pytest.fixture(scope="function")
def creation_user_data(test_user: TestUser) -> TestUser:
    return test_user.model_copy(update={"verified": True, "banned": False})

@pytest.fixture(scope='function')
def test_film() -> MovieCreate:
    return generate_film_data()


@pytest.fixture(scope='function')
def test_review():
    return generate_review()

@pytest.fixture
def generate_registered_user(api_manager):
    def _create():
        test_user = get_register_payload()
        response = api_manager.auth_api.register_user(test_user).json()
        test_user.model_copy(update={"id": response["id"]})
        api_manager.auth_api.authenticate(test_user.email, test_user.password)

        return test_user

    return _create

@pytest.fixture(scope="function")
def registered_user(api_manager, generate_registered_user):
    return generate_registered_user()

@pytest.fixture(scope="function")
def created_film(super_admin, test_film, db_helper) -> Iterator[MovieResponse]:
    response = super_admin.api.movies_api.create_movie(test_film)
    movie = MovieResponse(**response.json())
    yield movie
    movie_in_db = db_helper.get_movie_by_id(movie.id)
    if movie_in_db:
        db_helper.delete_movie(movie_in_db)

@pytest.fixture(scope="session")
def user_session():
    user_pool = []

    def _create_user_session():
        session = requests.Session()
        user_session = ApiManager(session)
        user_pool.append(user_session)
        return user_session

    yield _create_user_session

    for user in user_pool:
        user.close_session()

@pytest.fixture(scope="session")
def super_admin(user_session):
    new_session = user_session()

    super_admin = User(
        SuperAdminCreds.USERNAME,
        SuperAdminCreds.PASSWORD,
        [Roles.SUPER_ADMIN.value],
        new_session)

    super_admin.api.auth_api.authenticate(*super_admin.creds)
    return super_admin

@pytest.fixture(scope="function")
def admin(user_session, super_admin):
    new_session = user_session()
    admin_data = get_register_payload()
    admin_data = admin_data.model_copy(update={"verified": True, "banned": False})

    admin = User(
        admin_data.email,
        admin_data.password,
        [Roles.ADMIN.value],
        new_session)

    response = super_admin.api.user_api.create_user(admin_data).json()
    admin_id = response["id"]
    super_admin.api.user_api.change_user_data(admin_id, {"roles": [Roles.ADMIN.value]})
    admin.api.auth_api.authenticate(*admin.creds)
    return admin

@pytest.fixture(scope="function")
def common_user(user_session, super_admin, creation_user_data):
    new_session = user_session()

    common_user = User(
        creation_user_data.email,
        creation_user_data.password,
        [Roles.USER.value],
        new_session)

    super_admin.api.user_api.create_user(creation_user_data)
    common_user.api.auth_api.authenticate(*common_user.creds)
    return common_user

@pytest.fixture(scope="session")
def session_user(user_session, super_admin):
    new_session = user_session()
    user_data = get_register_payload()
    user_data = user_data.model_copy(update={"verified": True, "banned": False})

    user = User(
        user_data.email,
        user_data.password,
        [Roles.USER.value],
        new_session)

    super_admin.api.user_api.create_user(user_data)
    user.api.auth_api.authenticate(*user.creds)
    return user

@pytest.fixture(scope="function")
def db_user_data():
    return generate_user_db_data()

@pytest.fixture(scope="function")
def db_movie_data():
    return generate_movie_db_data()

@pytest.fixture(scope="module")
def db_session():
    db_session = get_db_session()
    yield db_session
    db_session.close()

@pytest.fixture(scope="function")
def db_helper(db_session) -> DBHelper:
    db_helper = DBHelper(db_session)
    return db_helper

@pytest.fixture(scope="function")
def created_test_user(db_helper):
    user = db_helper.create_test_user(generate_user_db_data())
    yield user
    if db_helper.get_user_by_id(user.id):
        db_helper.delete_user(user)

@pytest.fixture(scope="function")
def created_test_movie(db_helper):
    movie = db_helper.create_test_movie(generate_movie_db_data())
    yield movie
    if db_helper.get_movie_by_name(movie.name):
        db_helper.delete_movie(movie)

@pytest.fixture(scope="function") #была добавлена в файл conftest.py
def delay_between_retries():
    time.sleep(2)  # Задержка в 2 секунды\ это не обязательно, но
    yield          # нужно понимать что такая возможность имеется
