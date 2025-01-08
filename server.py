from fastapi import FastAPI, WebSocket
import uvicorn
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import RPi.GPIO as GPIO
from threading import Lock
import time
import asyncio

signal_count = 0
counter_lock = Lock()
timeframe = 5
starting_time = time.time()
rpm = 0


def gpio_callback(channel):
    global signal_count
    with counter_lock:
        signal_count += 1


async def reset_metrics():
    global signal_count
    global rpm
    global starting_time
    while True:
        await asyncio.sleep(timeframe)
        with counter_lock:
            elapsed_time = time.time() - starting_time
            rpm = signal_count / elapsed_time * 60
            signal_count = 0
            starting_time = time.time()


# Start the reset_metrics coroutine
asyncio.create_task(reset_metrics())

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)
GPIO.setup(27, GPIO.IN)
GPIO.add_event_detect(27, GPIO.FALLING, callback=gpio_callback, bouncetime=20)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
def read_root():
    with open("static/index.html", "r") as file:
        return file.read()


class TurbineStatus(BaseModel):
    enabled: bool


@app.post("/api/turbine")
def turbine(status: TurbineStatus):
    GPIO.output(17, GPIO.HIGH if status.enabled else GPIO.LOW)
    return {"status": "Turbine is enabled" if status.enabled else "Turbine is disabled"}


@app.websocket("/get_stats")
async def stats(websocket: WebSocket):
    websocket.accept()
    while True:
        await websocket.send_json({"rpm": rpm})
        await asyncio.sleep(timeframe)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
