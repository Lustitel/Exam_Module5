from custom_requester.custom_requester import CustomRequester
from Cinescope.config.base_urls import WHAT_IS_TODAY_BASE_URL
from Module5.models.mock_models import DateTimeRequest

WHAT_IS_TODAY_ENDPOINT = "/what_is_today"
PING_ENDPOINT = "/ping"


class WhatIsTodayApi(CustomRequester):
    def __init__(self, session):
        super().__init__(session=session, base_url=WHAT_IS_TODAY_BASE_URL)

    def get_holiday(self, current_date_time: str, expected_status=200, **kwargs):
        payload = DateTimeRequest(currentDateTime=current_date_time).model_dump()
        return self.send_request(
            "POST",
            WHAT_IS_TODAY_ENDPOINT,
            data=payload,
            expected_status=expected_status,
            **kwargs
        )

    def ping(self, expected_status=200, **kwargs):
        return self.send_request("GET", PING_ENDPOINT, expected_status=expected_status, **kwargs)
