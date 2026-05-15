# 必要なライブラリのインポート
import os
import csv
import urllib.error
import urllib.parse
import urllib.request
import json
from strands import Agent, tool
from strands.models.anthropic import AnthropicModel
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()
MODEL_ID = os.getenv("CLAUDE_MODEL_ID")

# ツールの定義
@tool
def get_weather() -> str:
    """東京の現在の天気を取得する。"""
    # Open-Meteo API（無料・キー不要）で東京の天気を取得
    url = "https://api.open-meteo.com/v1/forecast?latitude=35.6895&longitude=139.6917&current_weather=true"
    with urllib.request.urlopen(url) as res:
        data = json.loads(res.read())

    # 取得したデータから現在の天気情報を取り出して返す
    return json.dumps(data["current_weather"], ensure_ascii=False)

@tool
def search_events() -> str:
    """開催中のイベント一覧を返す。"""
    # ローカルのCSVファイルからイベント情報を読み込む
    with open('event_data.csv', 'r', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    return f"イベント({len(rows)}件):\n{rows}"

# 利用するモデルの指定
model = AnthropicModel(
    model_id=MODEL_ID,
    max_tokens=4096
)

# システムプロンプトの定義
SYSTEM_PROMPT = """あなたはお出かけプランナーです。
ユーザーの希望に合わせて、天気とイベント情報をもとにお出かけプランを提案してください。"""

# エージェントの作成
agent = Agent(
    model=model,
    system_prompt=SYSTEM_PROMPT,
    tools=[get_weather, search_events],
)

# エージェントの実行
agent("今日東京でお出かけしたいんだけど、おすすめのプランを教えて")
