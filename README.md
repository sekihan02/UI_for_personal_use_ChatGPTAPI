# ChatGPTを使用するためのUI

質問に回答するだけだけど一応LangChainで動くようにしてる<br>
現状チャットするだけの機能しかない<br>
Azure Openai には非対応

- ModelにOpenai APIで使用したいモデル名を指定してください
- Tempratureにはモデルの創造性を指定してください
- API KEYにはOpenai APIで発行した自分のAPIを指定してください
- Ctrl+Enterで送信
- Enterで改行
- 背景色の切り替え機能
- 短期記憶を追加

![UI_for　_GPT_to_chat.gif](./UI_for_GPT_to_chat.gif)

## 次の推奨質問の表示

Making Recommendationsにチェックを入れると
そのあとに入力したメッセージの回答の次のメッセージとしておすすめの質問をいくつか生成します。

推奨質問はクリックすると自動で入力欄に入力されます。

![UI_for_GPT_to_chat_recomend](./UI_for_GPT_to_chat_recomend.gif)
