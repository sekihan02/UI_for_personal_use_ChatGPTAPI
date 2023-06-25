from flask import Flask
from .routes.chat import chat_bp

app = Flask(__name__)
app.register_blueprint(chat_bp)
