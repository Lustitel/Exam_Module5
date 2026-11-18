import pytz
import requests

from datetime import datetime
from Cinescope.config.base_urls import FAKE_WORLD_CLOCK_BASE_URL
from Module5.models.mock_models import WorldClockResponse, WhatIsTodayResponse

def get_worldclockap_time() -> WorldClockResponse:
    """
    Функция, обращающаяся во внешний сервис мирового времени.
    В реальной жизни она ходит на http://worldclockapi.com/api/json/utc/now.
    Для тестов мы подменяем (мокаем/стабим) именно её!
    """
    response = requests.get("http://worldclockapi.com/api/json/utc/now", timeout=5)
    assert response.status_code == 200, "Удаленный сервис недоступен"
    return WorldClockResponse(**response.json())

def run_wiremock_worldclockap_time():
# Запуск WireMock сервера (если используется standalone, этот шаг можно пропустить)
    wiremock_url = "http://localhost:8080/__admin/mappings"
    mapping = {
        "request": {
            "method": "GET",
            "url": "/wire/mock/api/json/utc/now"  # Эмулируем запрос к worldclockapi
        },
        "response": {
            "status": 200,
            "body": '''{
                "$id": "1",
                "currentDateTime": "2025-03-08T00:00Z",
                "utcOffset": "00:00",
                "isDayLightSavingsTime": false,
                "dayOfTheWeek": "Wednesday",
                "timeZoneName": "UTC",
                "currentFileTime": 1324567890123,
                "ordinalDate": "2025-1",
                "serviceResponse": null
            }'''
        }
    }
    response = requests.post(wiremock_url, json=mapping)
    assert response.status_code == 201, "Не удалось настроить WireMock"

def get_fake_worldclockap_time() -> WorldClockResponse:
    """Функция, обращающаяся в наш локальный Fake API (FastAPI на 16002 порту)"""
    url = f"{FAKE_WORLD_CLOCK_BASE_URL}/fake/worldclockapi/api/json/utc/now"
    response = requests.get(url, timeout=5)
    assert response.status_code == 200, "Fake сервис недоступен"
    return WorldClockResponse(**response.json())


class TestTodayIsHolidayServiceAPI:
    """
    Тестирование сервиса WhatIsToday с использованием различных подходов:
    1. pytest-mock (mocker)
    2. Stub через monkeypatch
    3. Fake API (отдельный FastAPI сервис)
    4. WireMock (docker)
    """

    def test_what_is_today_by_mock(self, api_manager, mocker):
        """
        Способ 1: MOCK через pytest-mock (mocker.patch).
        Подменяем функцию get_worldclockap_time, чтобы она вернула объект с датой 1 января.
        """
        # Подменяем возвращаемое значение функции в точке её импорта/вызова
        mocker.patch(
            "tests.api.test_mock_services.get_worldclockap_time",
            return_value=WorldClockResponse(currentDateTime="2025-01-01T00:00Z")
        )

        # Вызываем функцию (она возвратит наш замоканный объект без выхода в интернет)
        time_data = get_worldclockap_time()
        assert time_data.currentDateTime == "2025-01-01T00:00Z"

        # Отправляем запрос через архитектурный клиент api_manager
        response = api_manager.what_is_today_api.get_holiday(time_data.currentDateTime)
        result = WhatIsTodayResponse(**response.json())

        assert result.message == "Новый год", "1 января должен быть Новый год!"

    def test_what_is_today_by_stub(self, api_manager, monkeypatch):
        """
        Способ 2: STUB через pytest fixture monkeypatch.
        Подменяем функцию get_worldclockap_time на заглушку-функцию, отдающую 9 мая.
        """

        # Подменяем оригинальную функцию на стаб
        monkeypatch.setattr(
            "tests.api.test_mock_services.get_worldclockap_time",
            lambda: WorldClockResponse(currentDateTime="2025-05-09T00:00Z")
        )

        time_data = get_worldclockap_time()
        assert time_data.currentDateTime == "2025-05-09T00:00Z"

        # Проверяем ответ нашего сервиса
        response = api_manager.what_is_today_api.get_holiday(time_data.currentDateTime)
        result = WhatIsTodayResponse(**response.json())

        assert result.message == "День Победы", "9 мая должен быть День Победы!"

    def test_fake_worldclockap_by_fake_api(self):  # проверка работоспособности сервиса worldclockap
        world_clock_response = get_fake_worldclockap_time()
        # Выводим текущую дату и время
        current_date_time = world_clock_response.currentDateTime
        print(f"Текущая дата и время: {current_date_time=}")

        assert current_date_time == datetime.now(pytz.utc).strftime("%Y-%m-%dT%H:%MZ"), "Дата не совпадает"

    def test_what_is_today_by_fake_api(self, api_manager):
        """
        Способ 3: FAKE API.
        Используем локальный микросервис (порт 16001), который эмулирует контракт worldclockapi.
        """
        time_data = get_fake_worldclockap_time()
        assert time_data.currentDateTime is not None

        response = api_manager.what_is_today_api.get_holiday(time_data.currentDateTime)
        result = WhatIsTodayResponse(**response.json())

        # Так как дата текущая реальная, сервис вернёт соответствующий праздник или его отсутствие
        assert result.message == "Сегодня нет праздников в России.", "Сегодня нет праздника!"

    def test_what_is_today_by_wiremock(self, api_manager): #Данный тест максимально похож на базовый
        # запускаем наш мок сервер
        run_wiremock_worldclockap_time()

        # Выполняем запрос к WireMock (имитация worldclockapi)
        world_clock_response = requests.get("http://localhost:8080/wire/mock/api/json/utc/now")
        assert world_clock_response.status_code == 200, "Удаленный сервис недоступен"
        # Парсим JSON-ответ с использованием Pydantic модели
        current_date_time = WorldClockResponse(**world_clock_response.json()).currentDateTime

        # Выполняем запрос к тестируемому сервису what_is_today
        what_is_today_response = api_manager.what_is_today_api.get_holiday(current_date_time)

        # Проверяем статус ответа от тестируемого сервиса
        assert what_is_today_response.status_code == 200, "Удаленный сервис недоступен"
        # Парсим JSON-ответ от тестируемого сервиса с использованием Pydantic модели
        what_is_today_data = WhatIsTodayResponse(**what_is_today_response.json())
        # Проверяем, что ответ соответствует ожидаемому
        assert what_is_today_data.message == "Международный женский день", "8 марта же?"