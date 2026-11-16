from sqlalchemy.orm import Session
from db_models.user import UserDBModel
from db_models.movies import MoviesDBModel
import allure


class DBHelper:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    """=== Методы для работы с БД в тестах с User ==="""

    @allure.step("БД: Создание тестового пользователя с данными {user_data}")
    def create_test_user(self, user_data: dict) -> UserDBModel:
        user = UserDBModel(**user_data)
        self.db_session.add(user)
        self.db_session.commit()
        self.db_session.refresh(user)
        return user

    @allure.step("БД: Получение пользователя по id={user_id}")
    def get_user_by_id(self, user_id: str):
        return self.db_session.query(UserDBModel).filter(UserDBModel.id == user_id).first()

    @allure.step("БД: Получение пользователя по email={email}")
    def get_user_by_email(self, email: str):
        return self.db_session.query(UserDBModel).filter(UserDBModel.email == email).first()

    @allure.step("БД: Проверка существования пользователя с почтой '{email}'")
    def user_exists_by_email(self, email: str) -> bool:
        return self.db_session.query(UserDBModel).filter(UserDBModel.email == email).count() > 0

    @allure.step("БД: Удаление пользователя {user}")
    def delete_user(self, user: UserDBModel):
        self.db_session.delete(user)
        self.db_session.commit()

    @allure.step("БД: Очистка тестовых данных {objects_to_delete}")
    def cleanup_test_data(self, objects_to_delete: list):
        for obj in objects_to_delete:
            if obj:
                self.db_session.delete(obj)
        self.db_session.commit()

    """=== Методы для работы с БД в тестах с Movies ==="""

    @allure.step("БД: Создание тестового фильма с данными {movie_data}")
    def create_test_movie(self, movie_data: dict) -> MoviesDBModel:
        movie = MoviesDBModel(**movie_data)
        self.db_session.add(movie)
        self.db_session.commit()
        self.db_session.refresh(movie)
        return movie

    @allure.step("БД: Получение фильма по id={movie_id}")
    def get_movie_by_id(self, movie_id: int):
        return self.db_session.query(MoviesDBModel).filter(MoviesDBModel.id == movie_id).first()

    @allure.step("БД: Проверка существования фильма с названием '{name}'")
    def movie_exists_by_name(self, name: str) -> bool:
        return self.db_session.query(MoviesDBModel).filter(MoviesDBModel.name == name).count() > 0

    @allure.step("БД: Получение фильма по названию '{name}'")
    def get_movie_by_name(self, name: str):
        return self.db_session.query(MoviesDBModel).filter(MoviesDBModel.name == name).first()

    @allure.step("БД: Удаление фильма '{movie}'")
    def delete_movie(self, movie: MoviesDBModel):
        self.db_session.delete(movie)
        self.db_session.commit()

