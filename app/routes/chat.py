import os
from flask import Blueprint, render_template
from flask import Flask, request, jsonify
import openai

from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chains import SequentialChain


chat_bp = Blueprint('chat', __name__)

# Global settings for model and temperature
settings = {
    'model': 'gpt-3.5-turbo-0613',
    'temperature': 0.8,
    'api_key': ''
}

@chat_bp.route("/")
def index():
    return render_template('index.html')

@chat_bp.route('/update_settings', methods=['POST'])
def update_settings():
    data = request.json
    settings['model'] = data['model']
    temperature = float(data['temperature'])
    if 0.0 <= temperature <= 1.0:
        settings['temperature'] = temperature
    else:
        return jsonify({'status': 'error', 'message': 'Temperature must be between 0.0 and 1.0'})

    settings['api_key'] = data['api_key']
    return jsonify({'status': 'success'})

class SimpleMemory:
    def __init__(self, max_length=10):
        self.memory = []
        self.max_length = max_length

    # メモリから会話を取得
    def get(self):
        return self.memory

    # メモリにメッセージを追加
    def add(self, message):
        self.memory.append(message)

        # メモリの長さが最大値を超えた場合は、最古のメッセージを削除
        if len(self.memory) > self.max_length:
            self.memory = self.memory[-self.max_length:]

    # ユーザーとAIのメッセージをペアとしてメモリに追加
    def add_pair(self, message, response):
        self.add("User: " + message)
        self.add("AI: " + response)

# 5件のメッセージを記憶するように設定
memory = SimpleMemory(max_length=5)

@chat_bp.route('/get_response', methods=['POST'])
def get_response():
    data = request.json
    message = data['message']

    # 以前の会話をメモリから取得
    past_conversation = memory.get()

    # Get the response from the GPT model
    openai.api_key = settings['api_key']
    os.environ["OPENAI_API_KEY"] = openai.api_key
    llm = ChatOpenAI(
        model_name=settings['model'],
        temperature=settings['temperature']
    )
    template = """あなたは質問に対して、回答を返してください
    質問:{question}
    回答:"""

    # プロンプトテンプレートの生成
    q_template = PromptTemplate(
        input_variables=["question"], 
        template=template
    )

    # LLMChainの準備
    q_chain = LLMChain(
        llm=llm, 
        prompt=q_template, 
        output_key="res"
    )

    res_chain = SequentialChain(
        chains=[q_chain],
        input_variables=["question"], 
        output_variables=["res"],
        verbose=True
    )
    response = res_chain({"question": "\n".join(past_conversation + ["User: "+message])})

    # メモリに新しい会話のペアを追加
    memory.add_pair(message, response["res"])

    return jsonify({'response': response["res"]})
