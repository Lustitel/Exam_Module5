import logging
from typing import Optional, Literal, List
from constants.roles import Roles
from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import datetime

logger = logging.getLogger(__name__)

EMAIL_PATTERN = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
MOVIE_NAME_PATTERN = r"^[a-zA-Zа-яА-ЯёЁ0-9\s.,:!?'\"()—–-]+$"
MOVIE_DESCRIPTION_PATTERN = r"^[a-zA-Zа-яА-ЯёЁ0-9\s.,:;!?'\"()—–\-«»\n\r]+$"
URL_PATTERN = r"^https?://[^\s/$.?#].[^\s]*$"

class TestUser(BaseModel):
    __test__ = False
    email: str = Field(..., pattern=EMAIL_PATTERN, description="Email адрес")
    fullName: str = Field(..., min_length=1, max_length=100, description="ФИО")
    password: str = Field(..., min_length=8, max_length=20, description="Пароль")
    passwordRepeat: str = Field(..., min_length=8, max_length=20, description="Повтор пароля")
    roles: list[Roles]
    verified: Optional[bool] = None
    banned: Optional[bool] = None

    @field_validator("passwordRepeat")
    def check_password_repeat(cls, repeat: str, info) -> str:
        if "password" in info.data and repeat != info.data["password"]:
            raise ValueError(f"Повторно введённый пароль не совпадает с паролем")
        return repeat

class RegisterUserResponse(BaseModel):
    id: str
    email: str = Field(..., pattern=EMAIL_PATTERN)
    fullName: str = Field(..., min_length=1, max_length=100)
    verified: bool
    roles: list[Roles]
    createdAt: datetime
    banned: Optional[bool] = None


class MovieCreate(BaseModel):
    """Модель для создания нового фильма"""
    name: str = Field(..., min_length=1, max_length=150, pattern=MOVIE_NAME_PATTERN, description="Название фильма")
    price: int = Field(..., ge=0, le=2**31-1, description="Цена фильма")
    description: str = Field(..., min_length=1, max_length=1000, pattern=MOVIE_DESCRIPTION_PATTERN, description="Описание фильма")
    imageUrl: Optional[str] = Field(default=None, pattern=URL_PATTERN, description="Изображение фильма")
    location: Literal["MSK", "SPB"] = Field(default="MSK", description="Город показа: MSK или SPB")
    published: bool = Field(default=False, description="Опубликован ли фильм для пользователей")
    genreId: int = Field(...,gt=0,description="Идентификатор жанра")

class GenreResponse(BaseModel):
    """Модель жанра внутри ответа фильма"""
    name: str = Field(..., min_length=1, max_length=100, description="Название жанра")
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

class MovieResponse(BaseModel):
    """Модель одного фильма (возвращается сервером при GET /movies/{id}, POST, PATCH)"""
    id: int = Field(..., gt=0, description="Уникальный идентификатор фильма в БД")
    name: str = Field(..., min_length=1, max_length=150, pattern=MOVIE_NAME_PATTERN, description="Название фильма")
    price: int | float = Field(..., ge=0, le=2**31 - 1, description="Цена билета")
    description: str = Field(..., min_length=1, max_length=1000, pattern=MOVIE_DESCRIPTION_PATTERN, description="Описание фильма")
    imageUrl: Optional[str] = Field(default=None, pattern=URL_PATTERN, description="Ссылка на постер")
    location: Literal["MSK", "SPB"] = Field(..., description="Город показа (MSK, SPB)")
    published: bool = Field(..., description="Статус публикации")
    genreId: int = Field(..., gt=0, description="ID связанного жанра")
    genre: GenreResponse = Field(..., description="Вложенный объект с информацией о жанре")
    rating: float = Field(..., ge=0, le=10, description="Рейтинг фильма")
    createdAt: datetime = Field(..., description="Дата и время создания записи (валидируется в ISO datetime)")
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

class MoviesListResponse(BaseModel):
    """Модель ответа со списком фильмов и пагинацией (GET /movies)"""
    movies: List[MovieResponse] = Field(..., description="Список фильмов на текущей странице")
    count: int = Field(..., ge=0, description="Общее количество фильмов в базе")
    page: int = Field(..., ge=1, description="Номер текущей страницы")
    pageSize: int = Field(..., ge=1, description="Количество фильмов на странице")
    pageCount: int = Field(..., ge=0, description="Общее количество доступных страниц")
    model_config = ConfigDict(populate_by_name=True, extra="ignore")