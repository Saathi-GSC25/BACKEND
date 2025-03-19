from flask import Flask
from flask_smorest import Api

from child_bot.config import APIConfig
from child_bot.routes import child_bp

app = Flask(__name__)
app.config.from_object(APIConfig)

api = Api(app)
api.register_blueprint(child_bp)

if __name__ == "__main__":
    app.run(debug=True, threaded = True)
