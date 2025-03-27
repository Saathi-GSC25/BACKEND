from dotenv import load_dotenv
import os

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
UPLOAD_FOLDER = 'uploads'
GCP_KEY = "gcp_key.json"
PROJECT_ID = "projects-aritro"

CHILD_COLLECTION_NAME = "children"
CONV_COLLECTION_NAME = "conversations"
HABITUAL_TASKS_COLLECTION_NAME = "habitual"
LEARNING_TASKS_COLLECTION_NAME = "learning"

REDIS_SERVER_HOST="localhost"
REDIS_SERVER_PORT=6379

APP_HOST="0.0.0.0"

class APIConfig:
    API_TITLE = "SaathiAPI"
    API_VERSION = "0.0.1"
    OPENAPI_VERSION = "3.0.3"
    OPENAPI_URL_PREFIX = "/"
    OPENAPI_SWAGGER_UI_PATH = "/docs"
    OPENAPI_SWAGGER_UI_URL = "https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/3.24.2/"
    OPENAPI_REDOC_PATH = '/redocs'
    OPENAPI_REDOC_URL = 'https://cdn.jsdelivr.net/npm/redoc@2.0.0-alpha.17/bundles/redoc.standalone.js'
