from flask import Flask
from web.routes import routes
from config import SECRET_KEY

app = Flask(__name__)
app.secret_key = SECRET_KEY

app.register_blueprint(routes)

if __name__ == "__main__":
    app.run(debug=True)
