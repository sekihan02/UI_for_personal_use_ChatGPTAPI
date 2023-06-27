from flask import Flask
from .routes.chat import chat_bp

app = Flask(__name__)
app.register_blueprint(chat_bp)

# debugモード　本番時には以下コード削除
if __name__ == "__main__":
    app.run(debug=True)