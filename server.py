from fastapi import FastAPI, WebSocket
import uvicorn
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pin_manager import PinManager
from threading import Lock
import time
import asyncio
import os
import RPi.GPIO as GPIO

hall_signal_count = 0
device_signal_count = 1
counter_lock = Lock()
device_lock = Lock()
timeframe = 5
starting_time = time.time()
hall_rpm = 0
device_l_per_h = 0


manager = PinManager()


# def read_from_fifo():
#     global visual_rpm
#     with open("/tmp/visual_tachometer_fifo", "r") as file:
#         visual_rpm = float(file.read())
#         print(visual_rpm)


def hall_gpio_callback(channel):
    global hall_signal_count
    with counter_lock:
        hall_signal_count += 1


def device_gpio_callback(channel):
    global device_signal_count
    with device_lock:
        device_signal_count += 1


async def reset_metrics():
    global hall_signal_count
    global device_signal_count
    global hall_rpm
    global device_l_per_h
    global starting_time

    folder_path = "./calc/"
    files = os.listdir(folder_path)
    file_count = len(files)
    output_file = f"{folder_path}{file_count}.csv"
    with open(output_file, "w") as f:
        f.write("Time, Hall RPM, Przeplywomiez L/h, Big Valve status\n")

    while True:
        await asyncio.sleep(timeframe)
        with counter_lock:
            elapsed_time = time.time() - starting_time
            hall_rpm = hall_signal_count / elapsed_time * 60
            hall_signal_count = 0
        with device_lock:
            elapsed_time = time.time() - starting_time
            device_l_per_h = ((device_signal_count / timeframe) * 60.0) / 7.5
            device_signal_count = 0

        print(time.time(), hall_rpm, device_l_per_h, manager.get_big_valve_status())
        with open(output_file, "a") as f:
            f.write(
                f"{int(time.time())}, {hall_rpm}, {device_l_per_h}, {manager.get_big_valve_status()}\n"
            )
        starting_time = time.time()
        # read_from_fifo()


# Start the reset_metrics coroutine
asyncio.create_task(reset_metrics())

GPIO.setmode(GPIO.BCM)
GPIO.setup(24, GPIO.IN)
GPIO.setup(25, GPIO.IN)
GPIO.add_event_detect(24, GPIO.FALLING, callback=hall_gpio_callback, bouncetime=20)
GPIO.add_event_detect(25, GPIO.FALLING, callback=device_gpio_callback, bouncetime=20)

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
