from clients.auth_api import AuthApi
from clients.user_api import UserApi
from clients.movies_api import MoviesApi
from clients.what_is_today_api import WhatIsTodayApi

class ApiManager:
    def __init__(self, session):
        self.session = session
        self.auth_api = AuthApi(session)
        self.movies_api = MoviesApi(session)
        self.user_api = UserApi(session)
        self.what_is_today_api = WhatIsTodayApi(session)

    def close_session(self):
        self.session.close()
