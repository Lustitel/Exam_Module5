from Module5.models.base_models import RegisterUserResponse


class TestUser:

    def test_create_user(self, super_admin, creation_user_data):
        response = super_admin.api.user_api.create_user(creation_user_data)
        created_user = RegisterUserResponse(**response.json())

        assert created_user.email == creation_user_data.email
        assert created_user.fullName == creation_user_data.fullName
        assert created_user.roles == creation_user_data.roles
        assert created_user.verified is True

    def test_get_user_by_locator(self, super_admin, creation_user_data):
        created_user_response = super_admin.api.user_api.create_user(creation_user_data)
        created_user = RegisterUserResponse(**created_user_response.json())
        user_by_id = RegisterUserResponse(**super_admin.api.user_api.get_user(created_user.id).json())
        user_by_email = RegisterUserResponse(**super_admin.api.user_api.get_user(creation_user_data.email).json())

        assert user_by_id == user_by_email, "Содержание ответов должно быть идентичным"
        assert user_by_id.id and user_by_id.id  != '', "ID должен быть не пустым"
        assert user_by_id.email == creation_user_data.email


    def test_get_user_by_email_common_user(self, common_user):
        response = common_user.api.user_api.get_user(common_user.email, expected_status=403)
        assert response.json().get("error") == "Forbidden"

    def test_create_user_by_admin(self, admin, creation_user_data):
        response = admin.api.user_api.create_user(creation_user_data)
        created_user = RegisterUserResponse(**response.json())

        assert created_user.email == creation_user_data.email
        assert created_user.fullName == creation_user_data.fullName
        assert created_user.roles == creation_user_data.roles
        assert created_user.verified is True
