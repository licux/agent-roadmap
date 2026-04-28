# 必要なライブラリのインポート
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

# ツールの定義
@tool
def get_weather(city: str = "Tokyo") -> str:
    """指定した都市の現在の天気を取得する。デフォルトは東京。"""
    # Geocoding APIで都市名から緯度・経度を取得してから天気を取得する
    geocoding_url = "https://geocoding-api.open-meteo.com/v1/search?" + urllib.parse.urlencode({
        "name": city,
        "count": 1,
        "language": "ja",
        "format": "json",
    })

    try:
        with urllib.request.urlopen(geocoding_url, timeout=10) as res:
            location_data = json.loads(res.read())
        results = location_data.get("results") or []
        if not results:
            return f"{city} の位置情報を取得できませんでした。"

        location = results[0]
        weather_url = "https://api.open-meteo.com/v1/forecast?" + urllib.parse.urlencode({
            "latitude": location["latitude"],
            "longitude": location["longitude"],
            "current_weather": "true",
        })
        with urllib.request.urlopen(weather_url, timeout=10) as res:
            weather_data = json.loads(res.read())
    except (urllib.error.URLError, json.JSONDecodeError):
        return "天気情報の取得に失敗しました。"

    return json.dumps(
        {
            "city": city,
            "resolved_name": location["name"],
            "current_weather": weather_data["current_weather"],
        },
        ensure_ascii=False,
    )

@tool
def search_events() -> str:
    """開催中のイベント一覧を返す。"""
    # ローカルのCSVファイルからイベント情報を読み込む
    with open('event_data.csv', 'r', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    return f"イベント({len(rows)}件):\n{rows}"

# 利用するモデルの指定
model = AnthropicModel(
    model_id="claude-sonnet-4-6",
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
