# Strands AgentsでAIエージェントを構築しよう

Strands Agentsを使って、天気予報と開催中のイベント情報をもとにお出かけプランを提案する「**お出かけプランナー**」エージェントを構築します。最小構成のエージェントから始め、2つのツールを追加して、AIエージェントが自律的にツールを使い分ける様子を確認します。

> **書籍との対応について**
> 本READMEは書籍の3.3節に掲載しているハンズオンの内容です。このエージェントにStreamlitでチャット画面を追加し、イベント検索をWeb検索に置き換える発展編は、書籍には掲載しきれなかったため`extra/chapter3/`に付録として公開しています。

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

また、あわせてAppendix. B.5を参照し、`.env`ファイルを作成しておいてください。`.env`には次の内容を記載します。

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

`2_travel_agent.py`にコードを記載していきます。以降は、1つのファイルのコードを5つのブロックに区切って順番に説明していきます。「(1/5)」のような番号はブロックの順番を表しているので、上から順にファイルへ追記していってください。

まず、必要なライブラリをインポートし、環境変数を読み込みます。

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

## 次のステップ

以上で、書籍に掲載しているStrands Agentsのハンズオンは完了です。数行のコードから始め、ツールを実装し、システムプロンプトを指定するだけで、天気とイベント情報を組み合わせてお出かけプランを提案するAIエージェントを構築できました。ここで構築したお出かけプランナーはシンプルな例ですが、ツールとシステムプロンプトを追加、変更するだけで、さまざまな用途に応用できます。

`extra/chapter3/`には、このお出かけプランナーの続きとして、Streamlitによるチャット画面の追加と、イベント検索をWeb検索に置き換える発展編のハンズオンを用意しています。本ハンズオンで作成したプロジェクトにそのまま追記していく構成になっているので、ぜひ続けて取り組んでみてください。

また、`extra/`ディレクトリには、MCPサーバーと連携するエージェント（`chapter5/`）や、ガードレールとHuman-in-the-Loopを組み込んだエージェント（`chapter6/`）のハンズオンも用意しています。あわせて取り組んでみてください。
