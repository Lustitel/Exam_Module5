from uuid import uuid4
from datetime import datetime
from Module5.models.base_models import TestUser
from constants.roles import Roles
from utils.data_generator import DataGenerator

def get_register_payload() -> TestUser:
    random_password = DataGenerator.generate_random_password()
    return TestUser(
        email=DataGenerator.generate_random_email(),
        fullName=DataGenerator.generate_firstname() + f" {DataGenerator.generate_lastname()}",
        password=random_password,
        passwordRepeat=random_password,
        roles=[Roles.USER]      # Указываем явно, см. ловушку exclude_unset в главе 6
    )

def generate_user_db_data(**kwargs) -> dict:
    """Генерирует словарь для вставки в таблицу users через UserDBModel"""
    payload = get_register_payload()
    data = {
        'id': f'{uuid4()}',
        'email': payload.email,
        'full_name': payload.fullName,
        'password': payload.password,
        'created_at': datetime.now(),
        'updated_at': datetime.now(),
        'verified': False,
        'banned': False,
        'roles': '{USER}'
    }
    data.update(kwargs)
    return data
