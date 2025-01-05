# Raspberry Pi Turbine Monitoring

This project uses FastAPI to monitor turbine data on a Raspberry Pi.

## Prerequisites

- Docker installed on your Raspberry Pi

## Running the Docker Image

1. Build the Docker image:

    ```sh
    sudo docker build -t turbine-monitoring .
    ```

2. Run the Docker container:

    ```sh
    sudo docker run --privileged -v /sys/class/gpio:/sys/class/gpio -v /dev/gpiomem:/dev/gpiomem -p 8000:8000 turbine-monitoring    
    ```

3. Access the FastAPI application:

    Open your browser and go to `http://<your-raspberry-pi-ip>:8000`

## API Documentation

FastAPI provides interactive API documentation. You can access it at:

- Swagger UI: `http://<your-raspberry-pi-ip>:8000/docs`
- ReDoc: `http://<your-raspberry-pi-ip>:8000/redoc`

## Stopping the Docker Container

To stop the running container, use:

```sh
docker stop <container_id>
```

Replace `<container_id>` with the actual container ID, which you can find using:

```sh
docker ps
```

## Setup WebRTC server on PI
https://james-batchelor.com/index.php/2023/11/10/install-mediamtx-on-raspbian-bookworm/