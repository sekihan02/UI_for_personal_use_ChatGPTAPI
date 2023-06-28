import os
import ast
from flask import Blueprint, render_template
from flask import Flask, request, jsonify
from flask import current_app as app
import openai
import wikipedia

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
#  Making Wiki Recommendationsのチェック取得
should_recommend_wiki = False  # Initial value

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

@chat_bp.route('/update_wiki_recommendation', methods=['POST'])
def update_wiki_recommendation():
    global should_recommend_wiki
    data = request.json
    should_recommend_wiki = data['should_recommend_wiki']
    app.logger.info(f"Updated should_recommend_wiki: {should_recommend_wiki}")  # Debugging statement
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
memory = SimpleMemory(max_length=8)

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

    # WikiRecommendのMaking Wiki Recommendationsのチェックがあったら
    if should_recommend_wiki:
        list_template = """あなたは回答を入力として受け取り、回答を表す3つ単語に変換してください。
        以下が単語リストの生成例です。
        ---
        回答: - 寿司
        - ラーメン
        - カレーライス
        - ピザ
        - 焼肉
        単語リスト: 寿司 ラーメン カレーライス
        ---
        ---
        回答: 織田信長は、戦国時代の日本で活躍した武将・戦国大名です。信長は、尾張国の織田家の当主として生まれ、若い頃から戦国時代の混乱を乗り越えて勢力を拡大しました。政治的な手腕も備えており、国内の統一を目指し、戦国大名や寺社などとの同盟を結びました。彼の統一政策は、後の豊臣秀吉や徳川家康による天下統一に繋がっていきました。
        信長の死は、本能寺の変として知られています。彼は家臣の明智光秀によって襲撃され、自害に追い込まれました。しかし、彼の業績や影響力は、その後の日本の歴史に大きく残りました。
        単語リスト: 織田信長 戦国時代 本能寺
        ---
        回答:{response}
        単語リスト"""

        # プロンプトテンプレートの生成
        list_temp = PromptTemplate(
            input_variables=["response"], 
            template=list_template
        )

        # LLMChainの準備
        list_chain = LLMChain(
            llm=llm, 
            prompt=list_temp, 
            output_key="lang_list"
        )

        list_recchain = SequentialChain(
            chains=[list_chain],
            input_variables=["response"], 
            output_variables=["lang_list"],
            verbose=True
        )
        list_lang = list_recchain({"response": response["res"]})
        # 文字列をPythonのリストに変換
        lang_list = list_lang["lang_list"].split(' ')
        
        # wikiの単語リストの内容取得
        articles = get_wikipedia_articles_for_keywords(lang_list, num_articles=1, lang='ja')
        # 使用する最大トークン数
        # MAX_TOKENS = 4096
        MAX_TOKENS = 1000
        articles_content = [article['content'][:MAX_TOKENS] for article in articles]
        
        wiki_template = """あなたは検索結果の内容を入力として受け取り、要約を最大で5つ箇条書きで生成してください。
        生成結果の先頭は必ず順番に1. 2. と数字を必ず記載して生成してください。
        検索結果の内容:{wiki_search}
        要約"""
        
        # プロンプトテンプレートの生成
        wiki_temp = PromptTemplate(
            input_variables=["wiki_search"], 
            template=wiki_template
        )

        # LLMChainの準備
        wiki_chain = LLMChain(
            llm=llm, 
            prompt=wiki_temp, 
            output_key="summary_list"
        )

        summary_recchain = SequentialChain(
            chains=[wiki_chain],
            input_variables=["wiki_search"], 
            output_variables=["summary_list"],
            verbose=True
        )
        summary_wiki = summary_recchain({"wiki_search": articles_content})
        
        wiki_search = ["関連ワードを調査しました。"] + summary_wiki["summary_list"].split('\n')

        return jsonify({'response': response['res'], 'wiki_search': wiki_search})

    return jsonify({'response': response["res"]})


def get_wikipedia_articles_for_keywords(keywords, num_articles=3, lang='ja'):
    """
    与えられたキーワードのリストに対し、各キーワードについてWikipedia記事を検索し、記事の情報を取得する。

    Parameters
    ----------
    keywords : list of str
        検索するキーワードのリスト
    num_articles : int, optional
        各キーワードに対して取得する記事の数 (default is 3)
    lang : str, optional
        使用する言語 (default is 'ja' for Japanese)

    Returns
    -------
    all_articles : list of dict
        各キーワードについて取得した記事の情報を含む辞書のリスト。
        各辞書はキーワード、タイトル、URL、記事の全文を含む。
    -------
    articles = get_wikipedia_articles_for_keywords(keywords)
    for article in articles:
        print('キーワード: ', article['keyword'])
        print('タイトル: ', article['title'])
        print('URL: ', article['url'])
        print('内容: ', article['content'])
        print('\n')
    """
    
    wikipedia.set_lang(lang)  # 言語を設定
    all_articles = []  # 全記事情報を保持するリスト

    for keyword in keywords:  # 各キーワードに対して
        try:
            titles = wikipedia.search(keyword, results=num_articles)  # キーワードでWikipediaを検索
            articles = []
            
            for title in titles:  # 取得した各タイトルに対して
                page = wikipedia.page(title)  # ページ情報を取得
                articles.append({  # 記事情報を辞書として追加
                    'keyword': keyword,  # 検索キーワード
                    'title': title,  # 記事のタイトル
                    'url': page.url,  # 記事のURL
                    'content': page.content  # 記事の全文
                })
            all_articles.extend(articles)  # 全記事情報リストに追加
        except wikipedia.DisambiguationError as e:  # 曖昧さ回避ページがヒットした場合のエラーハンドリング
            print(f"DisambiguationError for keyword {keyword}: {e.options}")  # エラーメッセージを出力
        
    return all_articles  # 全記事情報を返す
