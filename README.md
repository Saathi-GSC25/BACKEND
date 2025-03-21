## Setup Guide


docker build --no-cache -t flasktry .
docker run -p 5000:5000 -it flasktry

1. Clone the repository using git.
2. Make a virtual environment using virutalenv (chatGPT provide the commands).
3. Enter the virutalenv.
4. `pip install -r requirements.txt`
5. Make a config file in `child_bot/` with the following format - 

```
config.py

GEMINI_API_KEY = "YOUR API KEY"
UPLOAD_FOLDER = 'uploads'

class APIConfig:
    API_TITLE = "SaathiAPI"
    API_VERSION = "0.0.1"
    OPENAPI_VERSION = "3.0.3"
    OPENAPI_URL_PREFIX = "/"
    OPENAPI_SWAGGER_UI_PATH = "/docs"
    OPENAPI_SWAGGER_UI_URL = "https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/3.24.2/"

```
6. Load the Google Cloud Provider Private Key as a file called `gcp_key.json`.
7. `mkdir uploads` in the root directory of the application.

