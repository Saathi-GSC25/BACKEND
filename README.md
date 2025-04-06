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
        tmux \
        curl \
        redis-server \
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

2. Build the docker image 
```
docker build --no-cache -t <image_name> .
```
3. Run the docker container with the ports 5000(flask) and 6379(redis) exposed 
```
docker run -it -p 5000:5000 -p 6379:6379 <image_name>
```
4. Setup the key acquired from Google Cloud Provider with the new GCP Key and update the `GCP_KEY` variable in the config file with its path.
5. Make a folder called `uploads`
6. Setup a file `.env` with the following information - 
```
GEMINI_API_KEY = <YOUR_API_KEY>
```
7. Download the Google Cloud Provider SDK using 
```
curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-sdk-455.0.0-linux-x86_64.tar.gz
```
8. Extract the files using 
```
tar -xf google-cloud-sdk-455.0.0-linux-x86_64.tar.gz
```
9. Install `gcloud` SDK by running the following command 
```
./google-cloud-sdk/install.sh
```
10. Open a new bash terminal or use `source ~/.bashrc`  
```
gcloud auth application-default login
```
11. Enter the virtual environment and run the flask application. 
```
source $VIRTUAL_ENV/bin/activate
python app.py
```

TODO: Redisserver start command
