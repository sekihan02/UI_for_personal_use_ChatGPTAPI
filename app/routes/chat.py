import os
from flask import Blueprint, render_template
from flask import Flask, request, jsonify
import openai

from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chains import SequentialChain
from langchain.memory import SimpleMemory


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
    settings['temperature'] = float(data['temperature'])
    settings['api_key'] = data['api_key']
    return jsonify({'status': 'success'})

@chat_bp.route('/get_response', methods=['POST'])
def get_response():
    data = request.json
    message = data['message']

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
    response = res_chain({"question":message})

    return jsonify({'response': response["res"]})
