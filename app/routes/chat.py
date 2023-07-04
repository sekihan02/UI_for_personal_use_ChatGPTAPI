import os
import ast
# import base64
import requests
from urllib.parse import unquote
from flask import Blueprint, render_template
from flask import Flask, request, jsonify
from flask import current_app as app
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
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
    'api_key': '',
    'bing_search_v7_subscription_key': '',
    'bing_search_v7_endpoint': 'https://api.bing.microsoft.com',
    'search_service_name': 'txt-search',
    'index_name': 'azureblob-index-pdf',
    'strage_search_key': '',
}

# Making Recommendationsのチェック取得
should_recommend = False  # Initial value
# Making Wiki Recommendationsのチェック取得
should_recommend_wiki = False  # Initial value
# Making Bing Search Recommendationsのチェック取得
should_recommend_bing = False  # Initial value
# Making Bing Recommendationsのチェック取得
should_recommend_rec_bing = False  # Initial value
# Enable Strage Searchのチェック取得
should_strage_search = False  # Initial value

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
    # 追加
    settings['bing_search_v7_subscription_key'] = data['bing_search_v7_subscription_key']
    settings['bing_search_v7_endpoint'] = data['bing_search_v7_endpoint']
    settings['search_service_name'] = data['search_service_name']
    settings['index_name'] = data['index_name']
    settings['strage_search_key'] = data['strage_search_key']
    
    return jsonify({'status': 'success'})

@chat_bp.route('/update_recommendation', methods=['POST'])
def update_recommendation():
    global should_recommend
    data = request.json
    should_recommend = data['should_recommend']
    # app.logger.info(f"Updated should_recommend: {should_recommend}")  # Debugging statement
    return jsonify({'status': 'success'})

@chat_bp.route('/update_wiki_recommendation', methods=['POST'])
def update_wiki_recommendation():
    global should_recommend_wiki
    data = request.json
    should_recommend_wiki = data['should_recommend_wiki']
    # app.logger.info(f"Updated should_recommend_wiki: {should_recommend_wiki}")  # Debugging statement
    return jsonify({'status': 'success'})

# 追加
@chat_bp.route('/update_bing_recommendation', methods=['POST'])
def update_bing_recommendation():
    global should_recommend_bing
    data = request.json
    should_recommend_bing = data['should_recommend_bing']
    # app.logger.info(f"Updated should_recommend_bing: {should_recommend_bing}")  # Debugging statement
    return jsonify({'status': 'success'})

@chat_bp.route('/update_rec_bing_recommendation', methods=['POST'])
def update_rec_bing_recommendation():
    global should_recommend_rec_bing
    data = request.json
    should_recommend_rec_bing = data['should_recommend_rec_bing']
    return jsonify({'status': 'success'})

@chat_bp.route('/update_strage_search', methods=['POST'])
def update_strage_search():
    global should_strage_search
    data = request.json
    should_strage_search = data['should_strage_search']
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

# 8件のメッセージを記憶するように設定
memory = SimpleMemory(max_length=8)

@chat_bp.route('/get_response', methods=['POST'])
def get_response():
    global should_recommend
    global should_recommend_wiki
    global should_recommend_bing  # 追加
    global should_recommend_rec_bing  # 追加
    global should_strage_search  # 追加

    recommendations = ""
    rec_bing_search = ""
    strage_search = ""
    bing_search = ""
    wiki_search = ""
    # app.logger.info(f"In get_response, should_recommend: {should_recommend}")  # Debugging statement

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

        # return jsonify({'response': response['res'], 'recommendations': recommendations})

    # Bing Suggestのチェックがあったら
    if should_recommend_rec_bing:
        word_list_template = """
        以下が回答を3つのキーワードに分割した例です。
        ---
        回答: - 寿司
        - ラーメン
        - カレーライス
        - ピザ
        - 焼肉
        キーワード: 寿司 ラーメン カレーライス
        ---
        ---
        回答: 織田信長は、戦国時代の日本で活躍した武将・戦国大名です。信長は、尾張国の織田家の当主として生まれ、若い頃から戦国時代の混乱を乗り越えて勢力を拡大しました。政治的な手腕も備えており、国内の統一を目指し、戦国大名や寺社などとの同盟を結びました。彼の統一政策は、後の豊臣秀吉や徳川家康による天下統一に繋がっていきました。
        信長の死は、本能寺の変として知られています。彼は家臣の明智光秀によって襲撃され、自害に追い込まれました。しかし、彼の業績や影響力は、その後の日本の歴史に大きく残りました。
        キーワード: 織田信長 戦国時代 本能寺
        ---
        回答:{response}
        キーワード"""

        # プロンプトテンプレートの生成
        word_list_temp = PromptTemplate(
            input_variables=["response"], 
            template=word_list_template
        )

        # LLMChainの準備
        word_list_chain = LLMChain(
            llm=llm, 
            prompt=word_list_temp, 
            output_key="keywords"
        )

        keyword_recchain = SequentialChain(
            chains=[word_list_chain],
            input_variables=["response"], 
            output_variables=["keywords"],
            verbose=True
        )
        keywords = keyword_recchain({"response": response["res"]})
        # 文字列をPythonのリストに変換
        keyword_list = keywords["keywords"].split(' ')
        
        bing_template = """あなたは回答と検索結果の内容を入力として受け取り、回答と検索結果を参考に次にするべき質問を5以上生成してください。
        生成結果の先頭は必ず順番に1. 2. と数字を必ず記載して生成してください。
        回答:{response}
        検索結果の内容:{bing_search}
        質問"""
        
        # プロンプトテンプレートの生成
        bing_temp = PromptTemplate(
            input_variables=["response", "bing_search"], 
            template=bing_template
        )

        # LLMChainの準備
        bing_chain = LLMChain(
            llm=llm, 
            prompt=bing_temp, 
            output_key="summary_list"
        )

        summary_recchain = SequentialChain(
            chains=[bing_chain],
            input_variables=["response", "bing_search"], 
            output_variables=["summary_list"],
            verbose=True
        )

        # 各キーワードについてBing検索を実行し、結果の要約する
        results = get_bing_search_results_for_keywords(keyword_list, num_results=3, lang='ja-JP')
        
        # キーワードごとにスニペットをグループ化
        grouped_results = {}
        for result in results:
            keyword = result['keyword']
            snippet = result['snippet']
            
            # キーワードがgrouped_resultsにない場合は追加
            if keyword not in grouped_results:
                grouped_results[keyword] = []
            
            # キーワードに対応するリストにスニペットを追加
            grouped_results[keyword].append(snippet)

        # 各キーワードのスニペットを、セパレーターを使って連結
        concatenated_snippets_list = []
        separator = " ---- "  # 区切り文字として意味のある文字列を選択
        for keyword, snippets in grouped_results.items():
            concatenated_snippets = separator.join(snippets)
            concatenated_snippets_list.append(concatenated_snippets)
            
        summary_bing = summary_recchain({"response": response["res"], "bing_search": concatenated_snippets_list})
        
        rec_bing_search = ["次に推奨される質問は次のようなものが考えられます。"] + summary_bing["summary_list"].split('\n')
        # rec_bing_search = ["次に推奨される質問は次のようなものが考えられます。"] + "てすと\nです\ntest\ntest\ntest".split('\n')

        # return jsonify({'response': response['res'], 'rec_bing_search': rec_bing_search})

    # Bing Searchのチェックがあったら
    if should_recommend_bing:    
        word_list_template = """
        以下が回答を3つのキーワードに分割した例です。
        ---
        回答: - 寿司
        - ラーメン
        - カレーライス
        - ピザ
        - 焼肉
        キーワード: 寿司 ラーメン カレーライス
        ---
        ---
        回答: 織田信長は、戦国時代の日本で活躍した武将・戦国大名です。信長は、尾張国の織田家の当主として生まれ、若い頃から戦国時代の混乱を乗り越えて勢力を拡大しました。政治的な手腕も備えており、国内の統一を目指し、戦国大名や寺社などとの同盟を結びました。彼の統一政策は、後の豊臣秀吉や徳川家康による天下統一に繋がっていきました。
        信長の死は、本能寺の変として知られています。彼は家臣の明智光秀によって襲撃され、自害に追い込まれました。しかし、彼の業績や影響力は、その後の日本の歴史に大きく残りました。
        キーワード: 織田信長 戦国時代 本能寺
        ---
        回答:{response}
        キーワード"""

        # プロンプトテンプレートの生成
        word_list_temp = PromptTemplate(
            input_variables=["response"], 
            template=word_list_template
        )

        # LLMChainの準備
        word_list_chain = LLMChain(
            llm=llm, 
            prompt=word_list_temp, 
            output_key="keywords"
        )

        keyword_recchain = SequentialChain(
            chains=[word_list_chain],
            input_variables=["response"], 
            output_variables=["keywords"],
            verbose=True
        )
        keywords = keyword_recchain({"response": response["res"]})
        # 文字列をPythonのリストに変換
        keyword_list = keywords["keywords"].split(' ')
        
        bing_template = """あなたは検索結果の内容を入力として受け取り、要約を最大で5つ箇条書きで生成してください。
        生成結果の先頭は必ず順番に1. 2. と数字を必ず記載して生成してください。
        検索結果の内容:{bing_search}
        要約"""
        
        # プロンプトテンプレートの生成
        bing_temp = PromptTemplate(
            input_variables=["bing_search"], 
            template=bing_template
        )

        # LLMChainの準備
        bing_chain = LLMChain(
            llm=llm, 
            prompt=bing_temp, 
            output_key="summary_list"
        )

        summary_recchain = SequentialChain(
            chains=[bing_chain],
            input_variables=["bing_search"], 
            output_variables=["summary_list"],
            verbose=True
        )

        # 各キーワードについてBing検索を実行し、結果の要約する
        results = get_bing_search_results_for_keywords(keyword_list, num_results=3, lang='ja-JP')
        
        # キーワードごとにスニペットをグループ化
        grouped_results = {}
        for result in results:
            keyword = result['keyword']
            snippet = result['snippet']
            
            # キーワードがgrouped_resultsにない場合は追加
            if keyword not in grouped_results:
                grouped_results[keyword] = []
            
            # キーワードに対応するリストにスニペットを追加
            grouped_results[keyword].append(snippet)

        # 各キーワードのスニペットを、セパレーターを使って連結
        concatenated_snippets_list = []
        separator = " ---- "  # 区切り文字として意味のある文字列を選択
        for keyword, snippets in grouped_results.items():
            concatenated_snippets = separator.join(snippets)
            concatenated_snippets_list.append(concatenated_snippets)
            
        summary_bing = summary_recchain({"bing_search": concatenated_snippets_list})
        
        bing_search = ["関連ワードを調査しました。"] + summary_bing["summary_list"].split('\n')

        # return jsonify({'response': response['res'], 'bing_search': bing_search})

    # WikiSearchのMaking Wiki Searchのチェックがあったら
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

        # return jsonify({'response': response['res'], 'wiki_search': wiki_search})
        
    if should_strage_search:
        search_service_name = settings['search_service_name']
        index_name = settings['index_name']
        api_key = settings['strage_search_key']

        # Create a client
        credential = AzureKeyCredential(api_key)
        endpoint = f"https://{search_service_name}.search.windows.net"
        search_client = SearchClient(endpoint, index_name, credential)

        # Get the keyword from the user
        keyword = response["res"]

        # Search the PDFs with the keyword
        results = search_client.search(search_text=keyword)

        # Check if any results were found
        starage_str = []
        if not results:
            print("No results found.")
        else:
            # Print the first 2 results
            for i, result in enumerate(results):
                if i >= 2:  # Stop after printing 2 results
                    break
                # Get the encoded URL
                encoded_path = result['metadata_storage_path']
                # URL decode the path
                decoded_path = unquote(encoded_path)
                # Extract the file name from the path
                file_name = os.path.basename(decoded_path)
                str_ = f"Text: {result['content']}\n" + f"Found PDF: {file_name}\n"
                starage_str.append(str_)
        # # Check if any results were found
        # if not results:
        #     print("No results found.")
        # else:
        #     # Print the first 2 results
        #     for i, result in enumerate(results):
        #         if i >= 2:  # Stop after printing 2 results
        #             break
        #         # Get the encoded URL
        #         encoded_path = result['metadata_storage_path']
        #         # Correct the padding for Base64 decoding
        #         padding = 4 - len(encoded_path) % 4
        #         encoded_path += "=" * padding
        #         # Base64 decode the URL
        #         decoded_bytes = base64.b64decode(encoded_path)
        #         decoded_path = decoded_bytes.decode('utf-8')
        #         # URL decode the path
        #         decoded_path = unquote(decoded_path)
        #         # Extract the file name from the path
        #         file_name = os.path.basename(decoded_path)
        #         print(f"Found PDF: {file_name}")
        #         print(f"Text: {result['content']}\n")

        strage_search = ["Strageから関連ワードを調べました。"] + starage_str
        
    # return jsonify({'response': response["res"]})
    return jsonify({'response': response["res"], 'wiki_search': wiki_search, 'bing_search': bing_search, 'rec_bing_search': rec_bing_search, 'recommendations': recommendations, 'strage_search': strage_search})

def get_bing_search_results_for_keywords(keywords, num_results=3, lang='ja-JP'):
    """
    与えられたキーワードのリストに対し、各キーワードについてBingで検索し、検索結果を取得する。

    Parameters
    ----------
    keywords : list of str
        検索するキーワードのリスト
    num_results : int, optional
        各キーワードに対して取得する検索結果の数 (default is 3)
    lang : str, optional
        使用する言語 (default is 'ja' for Japanese)

    Returns
    -------
    all_results : list of dict
        各キーワードについて取得した検索結果を含む辞書のリスト。
        各辞書はキーワード、検索結果のタイトル、URL、概要を含む。
    """
    subscription_key = settings['bing_search_v7_subscription_key']
    endpoint = settings['bing_search_v7_endpoint'].rstrip('/') + "/v7.0/search"
    all_results = []

    for keyword in keywords:
        params = {'q': keyword, 'count': num_results, 'mkt': lang}
        headers = {'Ocp-Apim-Subscription-Key': subscription_key}
        try:
            response = requests.get(endpoint, headers=headers, params=params)
            response.raise_for_status()

            json_response = response.json()
            results = []
            if 'webPages' in json_response:
                for item in json_response['webPages']['value']:
                    results.append({
                        'keyword': keyword,
                        'name': item['name'],
                        'url': item['url'],
                        'snippet': item['snippet']
                    })
            else:
                print(f"No web pages found for keyword {keyword}")
                
            all_results.extend(results)
        except Exception as ex:
            print(f"Error for keyword {keyword}: {str(ex)}")

    # params = {'q': keywords, 'count': num_results, 'mkt': lang}
    # headers = {'Ocp-Apim-Subscription-Key': subscription_key}
    # try:
        # response = requests.get(endpoint, headers=headers, params=params)
        # response.raise_for_status()

        # json_response = response.json()
        # results = []
        # if 'webPages' in json_response:
            # for item in json_response['webPages']['value']:
                # results.append({
                    # 'keyword': keywords,
                    # 'name': item['name'],
                    # 'url': item['url'],
                    # 'snippet': item['snippet']
                # })
        # else:
            # print(f"No web pages found for keyword {keyword}")
        # all_results.extend(results)
    # except Exception as ex:
        # print(f"Error for keyword {keyword}: {str(ex)}")
        
    return all_results


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