# お出かけプランナーにフロントエンドとWeb検索を追加しよう

書籍の3.3節（`chapter3/`）で構築した「**お出かけプランナー**」エージェントを発展させます。Streamlitでチャット画面を追加してブラウザから対話できるようにし、さらにイベント検索をWeb検索APIに置き換えて、実際のイベント情報をもとにプランを提案できるようにします。

> **書籍との対応について**
> 本READMEの内容は、書籍には掲載しきれなかったものになります。書籍の3.3節のハンズオン（`chapter3/README.md`）を終えていることを前提に、そこで作成した`strands-handson`プロジェクトにファイルを追加していきます。

## ハンズオンの内容

`chapter3/`で作成したお出かけプランナーは、ターミナルで1回の質問に答えるだけのものでした。本ハンズオンでは、これを次の2段階で拡張します。

1. **Streamlitでフロントエンドを実装**: チャット画面を追加し、ブラウザ上で会話を続けながらプランを相談できるようにします
2. **Web検索ツールを使ったイベント検索**: 架空のイベント情報（`event_data.csv`）の代わりに、Web検索API「Tavily」でリアルタイムのイベント情報を取得します

本ハンズオンで作成するファイルは次の通りです。

| ファイル        | 内容                                                    |
| --------------- | ------------------------------------------------------- |
| `3_gui.py`      | Streamlitでチャット画面を実装した「お出かけプランナー」 |
| `4_appendix.py` | イベント検索をTavilyによるWeb検索に置き換えた発展版     |

## 事前準備

本ハンズオンは、書籍の3.3節で作成した`strands-handson`プロジェクトの続きとして進めます。まだの場合は、先に`chapter3/README.md`の「事前準備」から「ツールの実装」までを完了させてください。`.env`ファイルの作成と、`strands-agents[anthropic]`などのパッケージのインストールはそこで済ませている前提です。

Codespacesのターミナルを開いて、以下のコマンドでプロジェクトのディレクトリに移動しておいてください。以降のコマンドはすべてこのディレクトリで実行します。

```bash
# コマンド
cd /workspaces/agent-roadmap/chapter3/strands-handson
```

なお、手順をなぞらずにコードを動かしたい場合は、本リポジトリの`extra/chapter3/strands-handson/`に完成したコード一式（`event_data.csv`や`pyproject.toml`を含む）を置いています。このディレクトリで`.env.example`をもとに`.env`を作成し、`uv sync`コマンドを実行すれば、`uv run streamlit run 3_gui.py`または`uv run streamlit run 4_appendix.py`でそのまま起動できます。ただし、`4_appendix.py`の実行にはTavilyのAPIキーが必要です。後述の「発展: Web検索ツールを使ったイベント検索」の事前準備を参照して、`.env`に`TAVILY_API_KEY`も設定してください。

## Streamlitでフロントエンドを実装

`chapter3/`で実装したお出かけプランナーは、ターミナル上で実行して結果を確認するものでした。ここでは、フロントエンドを追加し、ブラウザ上で対話的にエージェントを利用できるようにします。

### AIエージェントのフロントエンドフレームワーク

実装したエージェントを広く利用してもらうために、フロントエンド（チャット画面などのUI）を設けたアプリケーション化が必要なことが多いです。本ハンズオンでは、Streamlitというフロントエンドフレームワークを使ってチャット画面を実装します。

Streamlitは、**PythonだけでWebアプリケーションを構築できる**オープンソースのフレームワークです。チャットの入力欄やボタン、グラフといったUIの部品がPythonの関数として用意されており、HTML/CSS/JavaScriptを書くことなく、チャット画面やダッシュボードを作成できます。通常のPythonスクリプトを書く感覚でフロントエンドを構築できるため、エージェントの動作確認やプロトタイプを素早く形にできるのが最大の強みです。

- Streamlit: https://streamlit.io/

### フロントエンドの実装

それでは実際にフロントエンドを実装していきましょう。まずは、uvを利用してStreamlitをインストールし、必要なファイルを作成します。

```bash
# コマンド
uv add streamlit==1.60.0
touch 3_gui.py
```

`3_gui.py`を開き、コードを記載していきます。ツールとモデル、システムプロンプトの定義までは`2_travel_agent.py`と同じです。`asyncio`と`streamlit`のインポートが追加されています。

```python
# strands-handson/3_gui.py (1/5)
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
    """東京の天気予報を取得する。当日を含む16日分の予報と現在の天気を返す。"""
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
```

ここからはStreamlitによるチャット画面の実装になります。まず、ページタイトルの表示と会話履歴の初期化、AIエージェントの作成を行います。

Streamlitは、ユーザーが操作するたびにスクリプト全体を先頭から再実行します。そのため、通常の変数に入れたデータは再実行のたびに失われてしまいます。`st.session_state`オブジェクトは、Streamlitがページの再表示をまたいでデータを保持するための領域で、ここでは2種類の会話履歴を保持しています。`messages`は画面表示用の履歴、`history`はAIエージェント自身の履歴（ツール呼び出しなども含む完全な履歴）です。

AIエージェントも再実行のたびに作り直されるため、`2_travel_agent.py`とは異なり、保存しておいた`history`を`messages`引数に渡して会話履歴を復元しています。これにより、AIエージェントは前のターンの内容を踏まえて応答できます。

```python
# strands-handson/3_gui.py (2/5)
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
```

次に、保存された会話履歴を画面に表示する部分の実装です。`st.session_state`オブジェクトに保持されている会話履歴の各メッセージを、順に表示しています。`st.chat_message`オブジェクトは、メッセージのrole（「user」か「assistant」）に応じて吹き出しの見た目を自動で切り替えます。また、エージェントの応答では、実行されたツールの名前を応答内容の上に表示しています。

```python
# strands-handson/3_gui.py (3/5)
# 保存済みの会話履歴を再表示
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        for name in msg.get("tool_names", []):
            st.write(f"🔧 ツール実行: {name}")
        st.markdown(msg["content"])
```

エージェントをストリーミング実行して、画面にリアルタイム表示する`run_agent`関数を定義します。

```python
# strands-handson/3_gui.py (4/5)
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
```

`agent.stream_async`メソッドは、エージェントの応答を非同期のイベントのストリームとして返します。受け取ったイベントの種類に応じて、「data」であれば生成されたテキストを画面にリアルタイムに表示し、「current_tool_use」であれば実行されたツールの名前をstatusコンポーネント（処理状況を表示する領域）に表示します。すべてのイベントを処理し終えたら、「完了」に更新してstatusコンポーネントを折りたたみます。

最後に、ユーザーの入力を受け取ってエージェントを呼び出す部分です。

```python
# strands-handson/3_gui.py (5/5)
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
```

`st.chat_input`オブジェクトでユーザーの入力を受け取り、ユーザーのメッセージを画面に表示します。次に`st.status`オブジェクトでstatusコンポーネントを作成し、`asyncio.run`メソッドで`run_agent`関数を実行しています。

応答が返ってきたら、表示用の履歴（`messages`）に応答内容とツール名を追加し、AIエージェントの履歴（`agent.messages`）を`history`に保存します。どちらも`st.session_state`オブジェクトに保存されるため、次の入力後も過去の会話が画面に残り続け、AIエージェントも会話の流れを踏まえて応答できます。

### 動作確認

`3_gui.py`のコードは以上になります。以下のコマンドでStreamlitを起動してみましょう。

```bash
# コマンド
uv run streamlit run 3_gui.py
```

Streamlitが起動すると、ターミナルにローカルホストのURL「`http://localhost:8501`」が表示されます。これをCmdキー（Windowsの場合はCtrlキー）を押下した状態でクリックすると、ブラウザの新しいタブでアプリケーションを開くことができます。

チャット入力欄に「**明日お出かけしたいんだけど、おすすめのプランは？**」のように入力すると、エージェントがツールを実行しながらストリーミングで回答を返す様子を確認できます。

動作確認後にアプリケーションを終了する際は、まずブラウザのアプリケーションを開いているタブを閉じ、Streamlitを起動しているターミナルで **Ctrl + C** キーを押下してください。

## 発展: Web検索ツールを使ったイベント検索

ここまでのハンズオンでは、APIキーの取得にかかる手間を省くために、イベント情報をローカルのCSVファイルとして用意しました。しかし実際のエージェント開発では、Web検索ツールを使ってリアルタイムの情報を取得するケースが一般的です。

`4_appendix.py`は、Web検索API「Tavily」を使って`search_events`をWeb検索に置き換えたコードです。Tavilyは開発者向けに無料枠が提供されているWeb検索APIで、APIキーを取得すればすぐに利用できます。あわせて、`get_weather`も都市名を指定できるように拡張しています。

- Tavily: https://www.tavily.com/

### 事前準備

Tavilyのサイトでアカウントを作成し、APIキーを取得してください。取得したAPIキーを`.env`に追記します。

```text
# .env
ANTHROPIC_API_KEY=<Anthropic APIキー>
MODEL_NAME=<モデル名>
TAVILY_API_KEY=<Tavily APIキー>
```

次に、Tavilyのクライアントライブラリをインストールし、ファイルを作成します。

```bash
# コマンド
uv add tavily-python==0.7.26
touch 4_appendix.py
```

### コードの変更点

`4_appendix.py`は`3_gui.py`をベースにしており、Streamlitによるチャット画面の実装は同じです。ここでは`3_gui.py`からの変更点のみを説明します。

ライブラリのインポートに`date`と`TavilyClient`が追加され、環境変数から読み込んだAPIキーでTavilyのクライアントを生成しています。

```python
# strands-handson/4_appendix.py (1/4)
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
```

`get_weather`は都市名を引数で受け取るようにしています。Open-Meteo Geocoding APIで都市名から緯度経度を取得し、その座標で天気予報を取得します。docstringに「英語の都市名で指定すること」と記載しているため、AIエージェントはユーザーが日本語で都市名を伝えても英語に変換してツールを呼び出します。

```python
# strands-handson/4_appendix.py (2/4)
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
```

`search_events`は、AIエージェントが決めた検索キーワードでTavilyのWeb検索を実行し、直近30日以内の検索結果を最大5件返します。

```python
# strands-handson/4_appendix.py (3/4)
@tool
def search_events(query: str) -> str:
    """指定したキーワードでイベント情報をWeb検索する。"""
    # Tavily APIでWeb検索を実行
    result = tavily_client.search(query, max_results=5, days=30)
    return json.dumps(result["results"], ensure_ascii=False)
```

システムプロンプトには`date.today()`を埋め込んでいます。「明日」「今週末」のような相対的な日付指定を、AIエージェントが正しく解釈して検索できるようにするためです。あわせてページタイトルも変更しています。

```python
# strands-handson/4_appendix.py (4/4)
# システムプロンプトの定義
SYSTEM_PROMPT = f"""あなたはお出かけプランナーです。
今日の日付は {date.today()} です。
ユーザーの希望に合わせて、天気と最新のイベント情報をもとにお出かけプランを提案してください。"""

# ページタイトルの表示
st.title("🗺️ お出かけプランナー (Tavily)")
```

以降のStreamlitによるチャット画面の実装は`3_gui.py`と同じです。コード全体は本リポジトリの`extra/chapter3/strands-handson/4_appendix.py`を参照してください。

### 動作確認

以下のコマンドでStreamlitを起動します。

```bash
# コマンド
uv run streamlit run 4_appendix.py
```

チャット入力欄に「**今週末に大阪でお出かけしたいんだけど、おすすめのプランは？**」のように入力すると、東京以外の都市の天気とWeb検索で取得した最新のイベント情報をもとに、お出かけプランが提案されます。

## 次のステップ

以上で、お出かけプランナーの発展編のハンズオンは完了です。Streamlitによるチャット画面の追加と、Web検索ツールへの置き換えを通して、書籍で構築したAIエージェントを段階的に拡張できることを確認しました。ツールの中身を差し替えてもAIエージェント側のコードはほとんど変わらないこと、そしてフロントエンドを加えるだけで実際に使えるアプリケーションの形になることを体験できたと思います。

`extra/`ディレクトリには、MCPサーバーと連携するエージェント（`chapter5/`）や、ガードレールとHuman-in-the-Loopを組み込んだエージェント（`chapter6/`）のハンズオンも用意しています。あわせて取り組んでみてください。
