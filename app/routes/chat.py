import os
from flask import Blueprint, render_template
from flask import Flask, request, jsonify
from flask import current_app as app
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

# Making Recommendationsのチェック取得
should_recommend = False  # Initial value

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

@chat_bp.route('/update_recommendation', methods=['POST'])
def update_recommendation():
    global should_recommend
    data = request.json
    should_recommend = data['should_recommend']
    app.logger.info(f"Updated should_recommend: {should_recommend}")  # Debugging statement
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
    global should_recommend
    app.logger.info(f"In get_response, should_recommend: {should_recommend}")  # Debugging statement

    # get the user's message from the POST request
    message = request.get_json()['message']

    # data = request.json
    # message = data['message']

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

    # RecommendのMaking Recommendationsのチェックがあったら
    if should_recommend:
        rec_template = """あなたは回答を入力として受け取り、その回答を元に次に質問したり、問い合わせたりした方がいい質問を5つ箇条書きで生成してください
        回答:{response}
        質問"""

        # プロンプトテンプレートの生成
        rec_temp = PromptTemplate(
            input_variables=["response"], 
            template=rec_template
        )

        # LLMChainの準備
        rec_chain = LLMChain(
            llm=llm, 
            prompt=rec_temp, 
            output_key="recommend"
        )

        res_recchain = SequentialChain(
            chains=[rec_chain],
            input_variables=["response"], 
            output_variables=["recommend"],
            verbose=True
        )
        q_recommend = res_recchain({"response": response["res"]})
        recommendations = ["次に推奨される質問は次のようなものが考えられます。"] + q_recommend["recommend"].split('\n')

        return jsonify({'response': response['res'], 'recommendations': recommendations})


    return jsonify({'response': response["res"]})
