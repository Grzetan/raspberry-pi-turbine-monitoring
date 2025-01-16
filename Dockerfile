FROM python:3.12-slim
WORKDIR /app
RUN apt-get update && apt-get install -y \
    python3-dev \
    gcc \
    cmake \
    g++ \
    libopencv-dev
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN cd visual_tachometer && cmake . && make && cd ..
EXPOSE 8000
CMD ["sh", "-c", "./visual_tachometer/visualTachometer"]
#"./build/visualTachometer & uvicorn server:app --host 0.0.0.0 --port 8000"]