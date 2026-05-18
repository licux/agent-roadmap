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
MODEL_ID = os.getenv("MODEL_NAME")

# ツールの定義
@tool
def get_weather() -> str:
    """東京の天気予報を取得する。今日から16日先までの予報と現在の天気を返す。"""
    # Open-Meteo API（無料・キー不要）で東京の天気を取得
    params = urllib.parse.urlencode({
        "latitude": 35.6895,
        "longitude": 139.6917,
        "current_weather": "true",
        "daily": "weather_code,temperature_2m_max,temperature_2m_min",
        "timezone": "Asia/Tokyo",
        "forecast_days": 16,
    })
    url = f"https://api.open-meteo.com/v1/forecast?{params}"
    with urllib.request.urlopen(url) as res:
        data = json.loads(res.read())

    # 現在の天気と日別予報をまとめて返す
    return json.dumps({
        "current_weather": data["current_weather"],
        "daily": data["daily"],
    }, ensure_ascii=False)

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
agent("明日でお出かけしたいんだけど、おすすめのプランを教えて")
