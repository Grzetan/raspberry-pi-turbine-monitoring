from fastapi import FastAPI
import uvicorn
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

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
    print(status.enabled)
    return {"status": "Turbine is enabled" if status.enabled else "Turbine is disabled"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
