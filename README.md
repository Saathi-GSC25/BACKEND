## Setup Guide

1. Setup a docker environment with the following Dockerfile
```
# Use the official Python 3.13 image as the base image
FROM python:3.13-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    APP_HOME=/app \
    VIRTUAL_ENV=/opt/venv

# Set the working directory
WORKDIR $APP_HOME

# Install system dependencies (combining both examples)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git \
        vim \
        ffmpeg \ 
        python3-blockdev \
        libblockdev-dev \
        python3-bytesize \
        python3-pyudev \
        python3-parted \
        python3-selinux \
        adwaita-icon-theme-full \
        lvm2 \
        dbus \
        brltty \
        python3-brlapi && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install virtualenv package and create a virtual environment
RUN pip install virtualenv && \
    virtualenv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Upgrade pip
RUN python -m pip install --upgrade pip

# Clone the repository
RUN git clone https://github.com/Saathi-GSC25/BACKEND.git $APP_HOME

RUN python -m pip install -r requirements.txt

# Expose the port the app runs on
EXPOSE 5000

# Set the entrypoint to run a shell
CMD ["/bin/bash"]
```

2. Build the docker image using - `docker build --no-cache -t <image_name> . `
3. Run the docker container using - `docker run -p 5000:5000 -it <image_name> `
4. Setup the key acquired from Google Cloud Provider with the new GCP Key and update the `GCP_KEY` variable in the config file with its path.
5. Make a folder called `uploads`.
6. Setup a file `config.py` with the following information - 
```
GEMINI_API_KEY = <YOUR_API_KEY>
UPLOAD_FOLDER = 'uploads'

class APIConfig:
    API_TITLE = "SaathiAPI"
    API_VERSION = "0.0.1"
    OPENAPI_VERSION = "3.0.3"
    OPENAPI_URL_PREFIX = "/"
    OPENAPI_SWAGGER_UI_PATH = "/docs"
    OPENAPI_SWAGGER_UI_URL = "https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/3.24.2/"

```

