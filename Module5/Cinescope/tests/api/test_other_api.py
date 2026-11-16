import allure
import pytest
import random

from sqlalchemy.orm import Session

from conftest import session
from db_models.transactions import AccountTransactionTemplate
from utils.data_generator import DataGenerator

@allure.epic("Тестирование транзакций")
@allure.feature("Тестирование транзакций между счетами")
class TestAccountsTransactions:

    @allure.story("Неизменность баланса при недопустимом значении перевода")
    @allure.description("""
        Этот тест проверяет, что баланс пользователей не меняется при попытке перевести недопустимую сумму.
        Шаги:
        1. Создание двух счетов: Stan и Bob.
        2. Перевод 2000 единиц от Stan к Bob.
        3. Проверка выброса исключения.
        4. Проверка сохранения балансов
        5. Очистка тестовых данных.
        """)
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.label("qa_name", "Ivan Petrovich")
    @allure.title("Тест перевода денег между счетами 200 рублей")
    def test_accounts_transaction_template(self, db_session: Session):
        # ====================================================================== Подготовка к тесту
        with allure.step("Создание тестовых данных в базе данных: счета Stan и Bob"):
            stan = AccountTransactionTemplate(user=f"Stan_{DataGenerator.generate_random_int(10)}", balance=1000)
            bob = AccountTransactionTemplate(user=f"Bob_{DataGenerator.generate_random_int(10)}", balance=500)

        db_session.add_all([stan, bob])
        db_session.commit()

        @allure.step("Функция перевода денег: transfer_money")
        @allure.description( """
            функция выполняющая транзакцию, имитация вызова функции на стороне тестируемого сервиса
            и вызывая метод transfer_money, мы как будто бы делаем запрос в api_manager.movies_api.transfer_money
            """)
        def transfer_money(session, from_account, to_account, amount):
            with allure.step(" Получаем счета"):
                from_account = session.query(AccountTransactionTemplate).filter_by(user=from_account).one()
                to_account = session.query(AccountTransactionTemplate).filter_by(user=to_account).one()

            with allure.step("Проверяем, что на счете достаточно средств"):
                if from_account.balance < amount:
                    raise ValueError("Недостаточно средств на счете")

            with allure.step("Выполняем перевод"):
                from_account.balance -= amount
                to_account.balance += amount

            with allure.step("Сохраняем изменения"):
                session.commit()

        # ====================================================================== Тест
        with allure.step("Проверяем начальные балансы"):
            assert stan.balance == 1000
            assert bob.balance == 500

        with allure.step("Проверяем срабатывание исключения"):
            with pytest.raises(ValueError, match="Недостаточно средств"):
                with allure.step("Выполняем перевод 2000 единиц от stan к bob и делаем rollback"):
                    transfer_money(db_session, from_account=stan.user, to_account=bob.user, amount=2000)
                    db_session.rollback()

        with allure.step("Получаем данные stan и bob из бд для дальнейшей проверки"):
            stan_record = db_session.query(AccountTransactionTemplate).filter_by(user=stan.user).one()
            bob_record = db_session.query(AccountTransactionTemplate).filter_by(user=bob.user).one()

        with allure.step("Проверяем, что балансы не изменились"):
            assert stan_record.balance == 1000
            assert bob_record.balance == 500

        with allure.step("Удаляем данные для тестирования из базы и фиксируем изменения"):
            db_session.delete(stan)
            db_session.delete(bob)
            db_session.commit()

    def test_delete_movie(self, super_admin, created_test_movie, db_helper):
        movie_id = created_test_movie.id

        delete_response = super_admin.api.movies_api.delete_movie(movie_id)
        assert delete_response.status_code == 200

        get_response = super_admin.api.movies_api.get_movies_id(movie_id=movie_id, expected_status=404)
        assert get_response.status_code == 404


@allure.title("Тест с перезапусками")
@pytest.mark.flaky(reruns=3)
def test_with_retries(delay_between_retries):
    with allure.step("Шаг 1: Проверка случайного значения"):
        result = random.choice([True, False])
        assert result, "Тест упал, потому что результат False"