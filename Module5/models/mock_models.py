from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class WorldClockResponse(BaseModel):
    """Модель ответа сервиса мирового времени (worldclockapi)"""
    id: Optional[str] = Field(default=None, alias="$id")
    currentDateTime: str
    utcOffset: Optional[str] = None
    isDayLightSavingsTime: Optional[bool] = None
    dayOfTheWeek: Optional[str] = None
    timeZoneName: Optional[str] = None
    currentFileTime: Optional[int] = None
    ordinalDate: Optional[str] = None
    serviceResponse: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)


class DateTimeRequest(BaseModel):
    """Модель запроса к сервису WhatIsToday"""
    currentDateTime: str  # Формат: "2025-02-13T21:43Z"


class WhatIsTodayResponse(BaseModel):
    """Модель ответа сервиса WhatIsToday"""
    message: str