from fastapi import FastAPI, WebSocket
import uvicorn
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pin_manager import PinManager
from threading import Lock
import time
import asyncio

signal_count = 0
counter_lock = Lock()
timeframe = 5
starting_time = time.time()
hall_rpm = 0
visual_rpm = 0


manager = PinManager()


def read_from_fifo():
    global visual_rpm
    with open("/tmp/visual_tachometer_fifo", "r") as file:
        visual_rpm = float(file.read())
        print(visual_rpm)


def gpio_callback(channel):
    global signal_count
    with counter_lock:
        signal_count += 1


async def reset_metrics():
    global signal_count
    global hall_rpm
    global starting_time
    while True:
        await asyncio.sleep(timeframe)
        with counter_lock:
            elapsed_time = time.time() - starting_time
            hall_rpm = signal_count / elapsed_time * 60
            signal_count = 0
            starting_time = time.time()
        read_from_fifo()


# Start the reset_metrics coroutine
asyncio.create_task(reset_metrics())

# GPIO.setmode(GPIO.BCM)
# GPIO.setup(17, GPIO.OUT)
# GPIO.setup(27, GPIO.IN)
# GPIO.add_event_detect(27, GPIO.FALLING, callback=gpio_callback, bouncetime=20)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
def read_root():
    with open("static/index.html", "r") as file:
        return file.read()


class Status(BaseModel):
    enabled: bool


@app.post("/api/pump")
def pump(status: Status):
    manager.active_pump(status.enabled)
    return {"status": "SUCCESS"}


@app.post("/api/small_valve")
def small_valve(status: Status):
    manager.active_small_valve(status.enabled)
    return {"status": "SUCCESS"}


class PercentageStatus(BaseModel):
    enabled: bool
    percentage: float


@app.post("/api/big_valve")
async def big_valve(status: PercentageStatus):
    try:
        await manager.change_big_valve(status.percentage, status.enabled)
    except ValueError as e:
        return {"status": "ERROR", "message": str(e)}
    return {"status": "SUCCESS"}


@app.websocket("/get_stats")
async def stats(websocket: WebSocket):
    await websocket.accept()
    while True:
        await websocket.send_json({"hall_rpm": hall_rpm})
        await asyncio.sleep(timeframe)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
