from datetime import datetime
import pytz
from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/ping")
def ping():
    return "PONG!"

@app.get("/fake/worldclockapi/api/json/utc/now")
def get_current_utc_time():
    now = datetime.now(pytz.utc)
    return {
        "$id": "1",
        "currentDateTime": now.strftime("%Y-%m-%dT%H:%MZ"),
        "utcOffset": "00:00:00",
        "isDayLightSavingsTime": False,
        "dayOfTheWeek": now.strftime("%A"),
        "timeZoneName": "UTC",
        "currentFileTime": int(now.timestamp() * 10**7),
        "ordinalDate": now.strftime("%Y-%j"),
        "serviceResponse": None
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=16001)
