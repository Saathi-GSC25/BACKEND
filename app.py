from flask import Flask
from flask_smorest import Api

from config import APIConfig
from child_bot.routes import child_bp
from parent_bot.routes import parent_bp
from info.routes import info_bp

app = Flask(__name__)
app.config.from_object(APIConfig)

api = Api(app)
api.register_blueprint(child_bp)
api.register_blueprint(parent_bp)
api.register_blueprint(info_bp)

if __name__ == "__main__":
    app.run(host= "0.0.0.0", debug=True, threaded = True)
