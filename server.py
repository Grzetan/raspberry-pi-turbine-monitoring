from fastapi import FastAPI
import uvicorn

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Welcome to the Raspberry Pi Turbine Monitoring System"}


@app.get("/status")
def get_status():
    return {"status": "All systems operational"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
