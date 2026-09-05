# Strands AgentsでAIエージェントを構築しよう

Strands Agentsを使って、天気予報と開催中のイベント情報をもとにお出かけプランを提案する「**お出かけプランナー**」エージェントを構築します。最小構成のエージェントから始め、ツールの追加、Streamlitによるチャット画面の実装、Web検索ツールへの置き換えと、段階的に拡張していきます。

> **書籍との対応について**
> 「事前準備」から「お出かけプランナーの実装」（`2_travel_agent.py`）までは書籍の3.3節に掲載している内容です。「Streamlitでフロントエンドを実装」（`3_gui.py`）以降は、書籍には掲載しきれなかった内容を、付録として公開しています。

## ハンズオンの内容

ユーザーが「明日お出かけしたいので、おすすめのプランを教えて」のように相談すると、天気予報と開催中のイベント情報を調べて、その日のお出かけプランを提案してくれるAIエージェントを作成します。これを実現するために、次の2つのツールを用意します。

- `get_weather`: 天気予報を取得するツール
- `search_events`: イベント情報を検索するツール

Strands Agentsはモデル駆動型のフレームワークです。利用するモデル（LLM）を選び、AIエージェントへの指示（システムプロンプト）とツールを与えるだけで、処理の流れを細かく定義しなくてもAIエージェントが動きます。

本ハンズオンで作成するファイルは次の通りです。

| ファイル            | 内容                                                    |
| ------------------- | ------------------------------------------------------- |
| `1_simple_agent.py` | 最小構成のAIエージェント                                |
| `2_travel_agent.py` | 2つのツールを持つ「お出かけプランナー」                 |
| `event_data.csv`    | `search_events`ツールが参照する架空のイベント情報       |
| `3_gui.py`          | Streamlitでチャット画面を実装した「お出かけプランナー」 |
| `4_appendix.py`     | イベント検索をTavilyによるWeb検索に置き換えた発展版     |

## 事前準備

ハンズオンはGitHub Codespacesを使用して実施します。以下の準備を行ってから進めてください。

| 参照先                                  |
| :-------------------------------------- |
| Appendix. A 「Anthropic APIキーの取得」 |
| Appendix. B 「ハンズオン環境の構築」    |

本ハンズオンではAnthropic社のAPIを直接利用するため、実行に応じてAPI利用料が発生します。目安は数十円程度になりますが、詳細はAppendix. Aを参照してください。

はじめにuvを使ってPythonプロジェクトを作成し、必要なパッケージをインストールします。Codespacesのターミナルを開いて、以下のコマンドを入力してください。

```bash
# コマンド
mkdir -p /workspaces/agent-roadmap/chapter3
cd /workspaces/agent-roadmap/chapter3

uv init strands-handson --python 3.14 --no-package
cd strands-handson
```

## 最小構成のAIエージェントの実装

Strands Agentsは数行のコードでAIエージェントを実装できるフレームワークです。まずは最小構成のAIエージェントでそのシンプルさを体験します。

ターミナルで以下のコマンドを実行して、コードを記載するためのファイルを作成します。

```bash
# コマンド
touch 1_simple_agent.py
```

また、併せてAppendix. B.5を参照し、`.env`ファイルを作成しておいてください。`.env`には次の内容を記載します。

```text
# .env
ANTHROPIC_API_KEY=<Anthropic APIキー>
MODEL_NAME=<モデル名>
```

次にuvを利用して、本節で使用するパッケージをインストールします。以下のコマンドをターミナルで実行してください。また、プロジェクト作成時に生成された`.gitignore`ファイルに、「.env」を必ず追記してください。

```bash
# コマンド
uv add "strands-agents[anthropic]"==1.50.1 anthropic==0.120.0 python-dotenv==1.2.2
echo ".env" >> .gitignore
```

`strands-agents[anthropic]`は、Strands Agents本体に加えてAnthropicモデルプロバイダーの依存関係もインストールするための指定です。ここではライブラリ間の互換性を確保するために、バージョンを固定しています。

ここまで完了したら、作成した`1_simple_agent.py`を開き、以下のコードを記述してください。

```python
# strands-handson/1_simple_agent.py
# 必要なライブラリのインポート
import os
from strands import Agent
from strands.models.anthropic import AnthropicModel
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()
MODEL_ID = os.getenv("MODEL_NAME")

# 利用するモデルの指定
model = AnthropicModel(
    model_id=MODEL_ID,
    max_tokens=4096
)

# エージェントを作成して実行
agent = Agent(model=model)
agent("こんにちは！あなたはどんなことができますか？")
```

コードの記載が完了したら、ターミナルで以下のコマンドを実行します。

```bash
# コマンド
uv run 1_simple_agent.py
```

すると、以下のような応答がストリーミングで表示されます（LLMの出力のため、実行するたびに内容は異なります）。

```text
# 出力結果
こんにちは！😊

私にできることをご紹介します：

## 💬 会話・相談
- 日常的な会話や雑談
- 悩み相談のサポート

## 📝 文章・ライティング
- 文章の作成・添削・要約
- メール、レポート、企画書などの作成

<中略>

## ⚠️ できないこと
- リアルタイムの情報取得（ネット検索）
- 画像の生成
- 個人情報の調査

---

何かお手伝いできることはありますか？気軽に聞いてください！🙌
```

ここで、コードの流れを確認しましょう。まず必要なライブラリをインポートし、`load_dotenv`関数を使って、`.env`ファイルからAPIキーと、利用するLLMのモデルIDを環境変数に読み込みます。次に、Strands Agentsが提供する`AnthropicModel`クラスに、環境変数から読み込んだモデルIDを渡して、AIエージェントを生成しています。生成したAIエージェントに文字列を渡せば回答が返ってきます。

## ツールの実装

さて、ここからは「お出かけプランナー」に必要な2つのツール（天気予報を取得するツールと、イベント情報を検索するツール）を実装し、AIエージェントから利用できるようにしていきます。

まず、ツールがない状態でのAIエージェントの限界を確認しましょう。`1_simple_agent.py`の最終行を以下のように変更します。

```python
# strands-handson/1_simple_agent.py（最終行）
agent("今日の東京の天気を教えて")
```

変更が完了したら、もう一度`1_simple_agent.py`を実行してください。すると、以下のような応答が表示されます。

```text
# 出力結果
申し訳ありませんが、私はリアルタイムの情報にアクセスする機能を持っていないため、**今日の東京の天気**をお伝えすることができません。

---

🌤 **天気を確認する方法：**
- **Google** で「東京 天気」と検索
- [**気象庁**](https://www.jma.go.jp/) のウェブサイト
- **天気予報アプリ**（Yahoo!天気、ウェザーニュースなど）

---

ぜひこれらをご利用ください！他にお手伝いできることがあればお知らせください。😊
```

このように、AIエージェントは何らかの回答を返しますが、リアルタイムの天気情報にアクセスする手段がないため、正確な情報を提供することはできません。こうしたLLMの知識だけでは対応できないタスクに対しては、モデルの手足となって外部の情報取得や処理を担うツールが必要です。

それでは、ツール付きのAIエージェントを実装していきましょう。まず、以下のコマンドを実行して、必要なファイルを作成します。

```bash
# コマンド
touch event_data.csv 2_travel_agent.py
```

`event_data.csv`には、AIエージェントが参照する架空のイベント情報を以下のように記載します。ここでは、お出かけプランナーエージェントの対応エリアは東京に絞っています。

```csv
# strands-handson/event_data.csv
area,name,genre,description
渋谷,ネオトーキョーナイトマーケット,グルメ,渋谷駅周辺の屋外会場で開催。世界各国の屋台フードが集結するナイトマーケット
渋谷,シブヤネオンアートコレクション,アート,渋谷の商業施設内で開催。ネオンを使った現代アートの展示イベント
新宿,新宿シネマカーニバル,エンタメ,新宿の映画館で開催。名作から新作まで特別上映とトークショーの映画祭
新宿,トワイライトフードパレード,グルメ,新宿中央公園の屋外会場で開催。夕方から始まるフードフェスティバル
下北沢,ストリートビンテージコレクション,ショッピング,下北沢の商店街の店舗内で開催。古着やビンテージ雑貨の大型セールイベント
下北沢,シモキタメロディさんぽ,音楽,下北沢エリアの屋外ステージ各所で開催。街を歩きながら楽しむ音楽イベント
```

`2_travel_agent.py`にコードを記載していきます。まず、必要なライブラリをインポートし、環境変数を読み込みます。

```python
# strands-handson/2_travel_agent.py (1/5)
# 必要なライブラリのインポート
import os
import csv
import urllib.parse
import urllib.request
import json
from strands import Agent, tool
from strands.models.anthropic import AnthropicModel
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()
MODEL_ID = os.getenv("MODEL_NAME")
```

次に、1つ目のツールである`get_weather`を実装します。`get_weather`は、Open-Meteo APIを呼び出してリアルタイムの天気情報を取得するツールです。Open-Meteo APIは無料で利用でき、APIキーも不要です。Strands Agentsでは、Pythonの関数に`@tool`デコレータを付けるだけでツールを定義できます。関数のdocstringがツールの説明としてモデルに渡されるため、AIエージェントはこの説明をもとに「いつこのツールを使うべきか」を判断します。

```python
# strands-handson/2_travel_agent.py (2/5)
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
```

`params`変数に、Open-Meteo APIを実行するために必要な情報を格納しています。今回の対応エリアは東京に限定するので、`latitude`（緯度）、`longitude`（経度）を東京の代表的な座標（東京都庁舎）に指定します。また、`daily`で取得する天気予報の内容を指定し、`forecast_days`を16にすることで、当日を含む16日分の情報を取得できるようにしています。

この`params`変数をURLに埋め込んで、`urllib.request.urlopen`メソッドを利用してAPIを実行し、結果を整形して返しています。これで1つ目のツールの実装は完了です。

続いて、2つ目のツールを実装します。`search_events`は、先ほど作成した`event_data.csv`を読み込んで架空のイベント情報を返すツールです。外部APIだけでなくローカルファイルへのアクセスもツールとして実装できます。

```python
# strands-handson/2_travel_agent.py (3/5)
@tool
def search_events() -> str:
    """開催中のイベント一覧を返す。"""
    # ローカルのCSVファイルからイベント情報を読み込む
    with open('event_data.csv', 'r', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    return f"イベント({len(rows)}件):\n{rows}"
```

これで必要なツールがそろったので、利用するモデルとシステムプロンプトを定義します。

```python
# strands-handson/2_travel_agent.py (4/5)
# 利用するモデルの指定
model = AnthropicModel(
    model_id=MODEL_ID,
    max_tokens=4096
)

# システムプロンプトの定義
SYSTEM_PROMPT = """あなたはお出かけプランナーです。
ユーザーの希望に合わせて、天気とイベント情報をもとにお出かけプランを提案してください。"""
```

システムプロンプトはAIエージェントの役割を自然言語で定義するものです。処理の手順を1つずつ指示するのではなく、「何をするエージェントなのか」というゴールと方針を渡すことで、モデルがそれに沿って自分で判断しながら動きます。

最後に、AIエージェントを生成して実行する部分を実装します。`1_simple_agent.py`との違いは、生成時にこれまで用意してきたツール（`tools`）、システムプロンプト（`system_prompt`）を渡している点です。「天気を調べてからイベントを調べる」といった処理の順序や条件分岐はいっさい書いていないことに注目してください。

```python
# strands-handson/2_travel_agent.py (5/5)
# AIエージェントの作成
agent = Agent(
    model=model,
    system_prompt=SYSTEM_PROMPT,
    tools=[get_weather, search_events],
)

# AIエージェントの実行
agent("明日お出かけしたいので、おすすめのプランを教えて")
```

それでは、実装した「お出かけプランナー」を動かしてみましょう。コードの記載が完了したら、以下のコマンドを実行してください。

```bash
# コマンド
uv run 2_travel_agent.py
```

実行が正常に完了すると、以下のような応答が表示されます。

```text
# 出力結果
もちろんです！最適なプランを提案するために、天気とイベント情報を同時に調べますね！
Tool #1: get_weather
Tool #2: search_events
情報が揃いました！明日（5月17日）の天気とイベントをもとにプランをご提案します😊

---

## ☀️ 明日の天気
- **天気：快晴** 🌞
- **最高気温：27.6℃ / 最低気温：13.5℃**
- 風も穏やかで、お出かけには絶好のコンディションです！

---

## 🗺️ おすすめお出かけプラン

### 🎵【下北沢さんぽプラン】〜音楽×ショッピングを楽しむ〜
天気が良いので、屋外を歩き回れる下北沢がぴったりです！

| 時間 | 内容 |
|------|------|
| 午前 | **ストリートビンテージコレクション**（下北沢）でお気に入りの古着・雑貨探し 🛍️ |
| 昼 | 下北沢の個性派カフェやランチを楽しむ ☕ |
| 午後〜夕方 | **シモキタメロディさんぽ**で街中の屋外ステージをめぐりながら音楽を満喫 🎶 |

<以下略>
```

実行結果を見ると、AIエージェントが自律的に`get_weather`と`search_events`を順に呼び出していることがわかります。どのツールをどの順序で使うかは開発者が指定したものではなく、AIエージェントがその場で判断した結果です。AIエージェントが天気情報とイベント情報を取得したうえで、それらを組み合わせたお出かけプランを提案していることが確認できました。

以上で、書籍に掲載しているハンズオンは完了です。ここから先は、書籍には掲載していないハンズオンになります。

## Streamlitでフロントエンドを実装

今まで実装してきたお出かけプランナーは、ターミナル上で実行して結果を確認するものでした。ここでは、フロントエンドを追加し、ブラウザ上で対話的にエージェントを利用できるようにします。

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
ユーザーの希望に合わせて、天気と最新のイベント情報をもとにお出かけプランを提案してください。"""
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

システムプロンプトには`date.today()`を埋め込んでいます。「明日」「今週末」のような相対的な日付指定を、AIエージェントが正しく解釈して検索できるようにするためです。合わせてページタイトルも変更しています。

```python
# strands-handson/4_appendix.py (4/4)
# システムプロンプトの定義
SYSTEM_PROMPT = f"""あなたはお出かけプランナーです。
今日の日付は {date.today()} です。
ユーザーの希望に合わせて、天気と最新のイベント情報をもとにお出かけプランを提案してください。"""

# ページタイトルの表示
st.title("🗺️ お出かけプランナー (Tavily)")
```

以降のStreamlitによるチャット画面の実装は`3_gui.py`と同じです。コード全体は本リポジトリの`chapter3/strands-handson/4_appendix.py`を参照してください。

### 動作確認

以下のコマンドでStreamlitを起動します。

```bash
# コマンド
uv run streamlit run 4_appendix.py
```

チャット入力欄に「**今週末に大阪でお出かけしたいんだけど、おすすめのプランは？**」のように入力すると、東京以外の都市の天気とWeb検索で取得した最新のイベント情報をもとに、お出かけプランが提案されます。

## 次のステップ

以上で、Strands Agentsを使ったAIエージェント構築のハンズオンは完了です。数行のコードから始め、ツールを実装し、システムプロンプトを指定するだけで、天気とイベント情報を組み合わせてお出かけプランを提案するAIエージェントを構築できました。さらに、Streamlitによるチャット画面の追加と、Web検索ツールへの置き換えを通して、AIエージェントを段階的に拡張できることも確認しました。ここで構築したお出かけプランナーはシンプルな例ですが、ツールとシステムプロンプトを追加、変更するだけで、さまざまな用途に応用できます。

`extra/`ディレクトリには、MCPサーバーと連携するエージェント（`chapter5/`）や、ガードレールとHuman-in-the-Loopを組み込んだエージェント（`chapter6/`）のハンズオンも用意していますので、あわせて取り組んでみてください。
