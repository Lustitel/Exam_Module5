import allure
from pydantic import BaseModel

@allure.step("Проверка совпадения полей переданного и реально созданного фильмов {request} и {response}")
def movie_response_request_missmatch(request: BaseModel, response: BaseModel) -> dict:
    diff = {
        movie_field: {"expected": getattr(request, movie_field), "actual": getattr(response, movie_field)}
        for movie_field in request.model_fields if
        getattr(request, movie_field) != getattr(response, movie_field)
    }

    return diff