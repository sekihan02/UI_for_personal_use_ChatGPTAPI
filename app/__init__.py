from flask import Flask, render_template
from .routes.chat import chat_bp
from .routes.text_correction import text_correction_bp  # Add this line
import logging

app = Flask(__name__)
app.register_blueprint(chat_bp)
# @app.route('/text_correction')
# def text_correction():
#     return render_template('text_correction.html')
app.register_blueprint(text_correction_bp)  # Add this line

app.logger.setLevel(logging.DEBUG)  # ログレベルをDEBUGに設定

stream_handler = logging.StreamHandler()

# debugモード　本番時には以下コード削除
if __name__ == "__main__":
    app.run(debug=True)