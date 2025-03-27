from flask import Flask
from flask_smorest import Api
from redis import Redis
from flask_session.redis import RedisSessionInterface

from config import APP_HOST, REDIS_SERVER_HOST, REDIS_SERVER_PORT, APIConfig
from child_api.routes import child_bp
from parent_api.routes import parent_bp
from common_api.routes import common_bp, common_habitual_bp, common_learning_bp

app = Flask(__name__)

app.config.from_object(APIConfig)

redis = Redis(host=REDIS_SERVER_HOST, port=REDIS_SERVER_PORT)
app.session_interface = RedisSessionInterface(app, client=redis)

api = Api(app)
api.register_blueprint(child_bp)
api.register_blueprint(parent_bp)
api.register_blueprint(common_bp)
api.register_blueprint(common_habitual_bp)
api.register_blueprint(common_learning_bp)


if __name__ == "__main__":
    app.run(host=APP_HOST, debug=True, threaded = True)
