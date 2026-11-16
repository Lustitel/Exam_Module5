import datetime

import allure
import pytest
import requests
from pytest_check import check

from clients.api_manager import ApiManager
from constants.roles import Roles
from data.auth.register_data import get_register_payload
from pydantic import ValidationError
from Module5.models.base_models import TestUser, RegisterUserResponse


class TestAuth:
    def test_register_user(self, user_session, test_user):
        client = user_session()
        response = client.auth_api.register_user(test_user, timeout=5)
        response_data = response.json()

        assert response_data["email"] == test_user.email
        # добавим еще проверок
        assert "id" in response_data
        assert "USER" in response_data["roles"]

    def test_register_and_login_user(self, user_session, test_user):
        client = user_session()
        client.auth_api.register_user(test_user)
        login_data = {
            "email": test_user.email,
            "password": test_user.password
        }
        response = client.auth_api.login_user(login_data)
        response_data = response.json()

        assert "accessToken" in response_data
        assert response_data["user"]["email"] == test_user.email

    def test_logout_user(self, user_session, test_user):
        client = user_session()
        client.auth_api.register_user(test_user)
        client.auth_api.login_user(test_user)
        response = client.auth_api.logout_user()

        assert response.status_code == 200, f"Expected 200, actual {response.status_code}"
        assert response.text == "OK"

    def test_update_headers(self, user_session, test_user):
        client = user_session()
        client.auth_api.register_user(test_user)
        response = client.auth_api.login_user(test_user)
        token = response.json()["accessToken"]
        client.auth_api._update_session_headers({"Authorization": "Bearer " + token})

        response = client.auth_api.send_request(
            "GET",
            "/user/me"
        )
        # Все последующие запросы через эту сессию будут с токеном автоматически
        assert response.status_code == 200, f"Expected 200, actual {response.status_code}"
        assert "Authorization" in client.auth_api.session.headers
        assert client.auth_api.session.headers["Authorization"] == "Bearer " + token

    def test_reset_headers(self, user_session):
        client = user_session()
        client.auth_api._update_session_headers({"foo": "bar"})
        assert "foo" in client.auth_api.session.headers

    def test_get_user_info(self, super_admin, common_user):
        response = super_admin.api.user_api.get_user_info(common_user.email).json()

        assert response["email"] == common_user.email
        assert "id" in response

    def test_delete_user(self, super_admin, user_session, test_user):
        client = user_session()
        register_response = client.auth_api.register_user(test_user).json()
        user_id = register_response["id"]

        response = super_admin.api.user_api.delete_user(user_id)

        assert response.status_code == 200
        assert super_admin.api.user_api.get_user_info(user_id).json() == {}
        client.auth_api.login_user(test_user, expected_status=401)


class TestAuthNegative:
    def test_login_user_wrong_password(self, user_session, test_user):
        client = user_session()
        client.auth_api.register_user(test_user)

        wrong_creds = test_user.model_copy()
        wrong_creds.password = 'DILDO'

        response = client.auth_api.login_user(wrong_creds, expected_status=401)

        assert response.status_code == 401, f"Expected 401, actual {response.status_code}"

    def test_login_user_wrong_creds(self, user_session, test_user):
        client = user_session()
        response = client.auth_api.login_user(test_user, expected_status=401)

        assert response.status_code == 401, f"Expected 401, actual {response.status_code}"

    def test_register_timeout(self, user_session, test_user):
        client = user_session()
        with pytest.raises(requests.exceptions.Timeout):
            client.auth_api.register_user(test_user, timeout=0.001)

    def test_delete_users(self, common_user, user_session):
        client = user_session()
        user1 = get_register_payload()
        user2 = get_register_payload()

        u1_resp = client.auth_api.register_user(user1).json()
        u2_resp = client.auth_api.register_user(user2).json()

        common_user.api.user_api.delete_users(u1_resp["id"], u2_resp["id"], expected_status=403)

        assert client.auth_api.login_user(user1).status_code == 201
        assert client.auth_api.login_user(user2).status_code == 201

    def test_user_model_rejects_invalid_email(self):
        with pytest.raises(ValidationError):
            TestUser(email="не-почта", fullName="Иван", password="12345678",
                     passwordRepeat="12345678", roles=[Roles.USER])

class TestSoftAsserts:

    @allure.title("Тест регистрации пользователя с помощью Mock")
    @allure.severity(allure.severity_level.MINOR)
    @allure.label("qa_name", "Ivan Petrovich")
    def test_register_user_mock(self, api_manager: ApiManager, test_user: TestUser, mocker):
        with allure.step(" Мокаем метод register_user в auth_api"):
            mock_response = RegisterUserResponse(  # Фиктивный ответ
                id="id",
                email="email@email.com",
                fullName="fullName",
                verified=True,
                banned=False,
                roles=[Roles.SUPER_ADMIN],
                createdAt=datetime.datetime.now()
            )

            mocker.patch.object(
                api_manager.auth_api,  # Объект, который нужно замокать
                'register_user',  # Метод, который нужно замокать
                return_value=mock_response  # Фиктивный ответ
            )

        with allure.step("Вызываем метод, который должен быть замокан"):
            register_user_response = api_manager.auth_api.register_user(test_user)

        with allure.step("Проверяем, что ответ соответствует ожидаемому"):
            with allure.step("Проверка поля персональных данных"):  # обратите внимание на вложенность allure.step
                with check:
                    # Строка ниже выдаст исключающее и, но выполнение теста продолжится
                    check.equal(register_user_response.fullName, "INCORRECT_NAME", "НЕСОВПАДЕНИЕ fullName")
                    check.equal(register_user_response.email, mock_response.email)

            with allure.step("Проверка поля banned"):
                with check("Проверка поля banned"):  # можно использовать вместо allure.step
                    check.equal(register_user_response.banned, mock_response.banned)