import pytest
import logging
import json

from Module5.models.base_models import TestUser
from constants.roles import Roles

logger = logging.getLogger(__name__)

def test_user_data(test_user):
    test_user.roles = [Roles.SUPER_ADMIN]
    logger.info(f"{test_user.email=} {test_user.fullName=} {test_user.password=} {test_user.passwordRepeat=} {test_user.roles=}")

def test_serialization(test_user):
    data = json.loads(test_user.model_dump_json())
    new_user_data = TestUser(**data).model_dump_json(exclude_none=True)
    new_user = TestUser.model_validate_json(new_user_data)
    assert "verified" not in new_user_data and "banned" not in new_user_data
    logger.info(f"{new_user.model_dump()=} \n{new_user.model_dump_json(exclude_unset=True)=} \n{new_user.model_dump_json(exclude_none=True)=}")

@pytest.mark.xfail(reason="Нарочно скармливается неверный пароль")
def test_repeat_password_ok(test_user):
    data = json.loads(test_user.model_dump_json())
    user_data = TestUser(**data).model_dump(exclude_none=True)
    user_data["password"] = "111111111"
    TestUser.model_validate(user_data)
    logger.info(f"{user_data["password"]=}  {user_data["passwordRepeat"]}")

def test_email(test_user):
    data = json.loads(test_user.model_dump_json())
    user_data = TestUser(**data).model_dump(exclude_none=True)
    user_data["email"] = "deb@email.com"
    TestUser.model_validate(user_data)
    logger.info(f"{user_data["password"]=}  {user_data["passwordRepeat"]}")