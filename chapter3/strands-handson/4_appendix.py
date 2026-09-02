# 必要なライブラリのインポート
import os
import urllib.request
import urllib.parse
import json
from datetime import date
import streamlit as st
import asyncio
from strands import Agent, tool
from strands.models.anthropic import AnthropicModel
from tavily import TavilyClient
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()
MODEL_ID = os.getenv("MODEL_NAME")

tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

# ツールの定義
@tool
def get_weather(city: str = "Tokyo") -> str:
    """指定した都市の天気予報を取得する。cityは英語の都市名で指定すること（例: Tokyo, Osaka, Sapporo）。当日を含む16日分の予報と現在の天気を返す。"""
    # Open-Meteo Geocoding API（無料・キー不要）で都市名から緯度経度を取得
    geo_params = urllib.parse.urlencode({"name": city, "count": 1, "language": "ja"})
    with urllib.request.urlopen(f"https://geocoding-api.open-meteo.com/v1/search?{geo_params}") as res:
        geo = json.loads(res.read())
    if not geo.get("results"):
        return f"{city}の位置情報が見つかりませんでした"
    lat = geo["results"][0]["latitude"]
    lon = geo["results"][0]["longitude"]

    # Open-Meteo API（無料・キー不要）で天気予報を取得
    params = urllib.parse.urlencode({
        "latitude": lat,
        "longitude": lon,
        "current_weather": "true",
        "daily": "weather_code,temperature_2m_max,temperature_2m_min",
        "timezone": "Asia/Tokyo",
        "forecast_days": 16,
    })
    with urllib.request.urlopen(f"https://api.open-meteo.com/v1/forecast?{params}") as res:
        data = json.loads(res.read())

    # 現在の天気と日別予報をまとめて返す
    return json.dumps({
        "current_weather": data["current_weather"],
        "daily": data["daily"],
    }, ensure_ascii=False)

@tool
def search_events(query: str) -> str:
    """指定したキーワードでイベント情報をWeb検索する。"""
    # Tavily APIでWeb検索を実行
    result = tavily_client.search(query, max_results=5, days=30)
    return json.dumps(result["results"], ensure_ascii=False)

# 利用するモデルの指定
model = AnthropicModel(
    model_id=MODEL_ID,
    max_tokens=4096
)

# システムプロンプトの定義
SYSTEM_PROMPT = f"""あなたはお出かけプランナーです。
今日の日付は {date.today()} です。
ユーザーの希望に合わせて、天気と最新のイベント情報をもとにお出かけプランを提案してください。"""

# ページタイトルの表示
st.title("🗺️ お出かけプランナー (Tavily)")

# Streamlitは操作のたびにスクリプト全体が再実行されるため、session_stateで会話履歴を保持。
# ・st.session_state.messages : 表示用の会話履歴
# ・st.session_state.history : エージェントの会話履歴
if "messages" not in st.session_state:
    st.session_state.messages = []
if "history" not in st.session_state:
    st.session_state.history = []

# エージェントは再実行のたびに生成されるため、保存しておいた会話履歴をmessages引数で復元する。
agent = Agent(
    model=model,
    system_prompt=SYSTEM_PROMPT,
    tools=[get_weather, search_events],
    messages=st.session_state.history.copy(),
)

# 保存済みの会話履歴を再表示
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        for name in msg.get("tool_names", []):
            st.write(f"🔧 ツール実行: {name}")
        st.markdown(msg["content"])

# エージェントをストリーミング実行し、UIにリアルタイムに表示
async def run_agent(query: str, status, response_area):
    text = ""
    tool_names = []

    # エージェントのストリーミング出力を逐次処理
    async for event in agent.stream_async(query):
        if "data" in event:
            # 生成されたテキストをリアルタイムに表示
            text += event["data"]
            response_area.markdown(text.replace("<br>", "\n"))
        elif "current_tool_use" in event:
            # エージェントがツールを呼び出したらステータスに表示
            name = event["current_tool_use"].get("name", "")
            if name and name not in tool_names:
                tool_names.append(name)
                status.write(f"🔧 ツール実行: {name}")

    # ストリーミング完了後、ステータスを更新
    status.update(label="完了", state="complete", expanded=False)
    return text.replace("<br>", "\n"), tool_names

# ユーザー入力の処理
if prompt := st.chat_input("お出かけの相談をしてください"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    # ユーザーのメッセージを表示
    with st.chat_message("user"):
        st.markdown(prompt)

    # エージェントの応答を表示
    with st.chat_message("assistant"):
        # st.statusで処理中の状態をユーザーに伝える
        status = st.status("考え中...", expanded=True)
        response_area = st.empty()
        accumulated_text, tool_names = asyncio.run(run_agent(prompt, status, response_area))

        # 次回再表示時に復元できるように会話履歴に保存
        st.session_state.messages.append({
            "role": "assistant",
            "content": accumulated_text,
            "tool_names": tool_names,
        })

        # エージェントの会話履歴（ツール呼び出し等も含む完全な履歴）を保存し、
        # 次のターンでmessages引数として復元できるようにする
        st.session_state.history = agent.messages