# 必要なライブラリのインポート
import os
import csv
import urllib.parse
import urllib.request
import json
import streamlit as st
import asyncio
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
ユーザーの希望に合わせて、天気と最新のイベント情報をもとにお出かけプランを提案してください。"""


# ページタイトルの表示
st.title("🗺️ お出かけプランナー")

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