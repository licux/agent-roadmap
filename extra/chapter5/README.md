# MCPを利用したAIエージェントを構築しよう

MCPの公式Python SDKを利用してMCPサーバーを自作し、それをStrands Agentsで実装したAIエージェントから利用します。自作のMCPサーバーと既製のMCPサーバーを組み合わせて、「**料理レシピアシスタント**」エージェントを構築します。

## ハンズオンの内容

ユーザーから「**30分以内で作れる和食を3つ提案して**」といった自然言語での指示を受けると、レシピデータベースから条件に合うものを検索し、その内容をまとめてMarkdownファイルとして書き出すAIエージェントを実装します。

このAIエージェントを実現するために、2つのMCPサーバーを利用します。

- **recipe-assistant**: レシピデータベースからレシピを検索するツールを実装した、自作のMCPサーバー
- **Filesystem MCPサーバー**: ローカルファイルの読み書きを行う、既製のMCPサーバー

1つのAIエージェントが2つのMCPサーバーのツールを使い分け、献立や買い物リストといった成果物を生成していきます。

本ハンズオンで作成するファイルは次の通りです。ファイル名の先頭の番号は作成する順番を表しており、`1_server.py`で作ったMCPサーバーを`2_agent.py`と`3_gui.py`から利用します。

| ファイル | 内容 |
| --- | --- |
| `recipes.json` | レシピデータベース（架空のレシピ7件） |
| `1_server.py` | 自作のMCPサーバー「recipe-assistant」 |
| `2_agent.py` | 2つのMCPサーバーを利用する「料理レシピアシスタント」エージェント |
| `3_gui.py` | Streamlitでチャット画面を実装した「料理レシピアシスタント」 |

MCPという共通プロトコルに従って実装したサーバーは、対応するホストであればどこからでも同じように利用できます。本ハンズオンではStrands Agentsから利用しますが、同じサーバーをClaude Codeなど他のMCPホストから利用することもできます。

## 事前準備

ハンズオンはGitHub Codespacesを使用して実施します。以下の準備を行ってから進めてください。

| 参照先 |
| :---- |
| Appendix. A 「Anthropic APIキーの取得」 |
| Appendix. B 「ハンズオン環境の構築」 |

本ハンズオンではAnthropic社のAPIを直接利用するため、実行に応じてAPI利用料が発生します。目安は数十円程度になりますが、詳細はAppendix. Aを参照してください。

はじめにuvを使ってPythonプロジェクトを作成します。Codespacesのターミナルを開いて、以下のコマンドを入力してください。以降のコマンドは、特に断りがない限りすべて`chapter5/recipe-agent`ディレクトリで実行します。

```bash
# コマンド
mkdir -p /workspaces/agent-roadmap/chapter5
cd /workspaces/agent-roadmap/chapter5

uv init recipe-agent --python 3.14 --no-package
cd recipe-agent
```

次に、Appendix. B.5を参照し、`.env`ファイルを作成しておいてください。`.env`には次の内容を記載します。

```text
# .env
ANTHROPIC_API_KEY=<Anthropic APIキー>
MODEL_NAME=<モデル名>
```

続いてuvを利用して、本ハンズオンで使用するパッケージをインストールします。以下のコマンドをターミナルで実行してください。また、プロジェクト作成時に生成された`.gitignore`ファイルに、「.env」を必ず追記してください。

```bash
# コマンド
uv add mcp==1.29.1 "strands-agents[anthropic]"==1.50.1 anthropic==0.120.0 python-dotenv==1.2.2
echo ".env" >> .gitignore
```

3章で導入したパッケージに加えて、MCPの公式Python SDKである`mcp`もインストールしています。

- MCP Python SDK: https://github.com/modelcontextprotocol/python-sdk

また、今回利用する既製MCPサーバーの起動にNode.jsが必要になります。Codespacesではあらかじめ用意されているので、以下のコマンドで存在を確認しておいてください。何らかのバージョン情報が表示されれば問題ありません。

```bash
# コマンド
node -v
```

## 自作MCPサーバーの実装

それでは、自作のレシピ検索MCPサーバーを実装しましょう。サーバー名は`recipe-assistant`とし、レシピを検索する`search_recipes`と、レシピのIDを指定して詳細情報を取得する`get_recipe_detail`の2つのツールを作成していきます。2つのツールはどちらも`1_server.py`という1つのファイルに実装します。

### サンプルデータの準備

ツールが参照するレシピのデータベースを作成します。以下のコマンドを実行して、ファイルを作成してください。

```bash
# コマンド（chapter5/recipe-agent で実行）
touch recipes.json
```

作成が完了したら、ファイルを開いて、料理レシピ7件を記載してください。

```json
// recipe-agent/recipes.json
[
    {"id":"R001","name":"鶏むね肉のグリル","genre":"和食","cooking_time_min":20,"ingredients":["鶏むね肉","塩","オリーブオイル"]},
    {"id":"R002","name":"カプレーゼ","genre":"洋食","cooking_time_min":10,"ingredients":["トマト","モッツァレラ","バジル"]},
    {"id":"R003","name":"麻婆豆腐","genre":"中華","cooking_time_min":25,"ingredients":["豆腐","豚ひき肉","豆板醤"]},
    {"id":"R004","name":"鮭のホイル焼き","genre":"和食","cooking_time_min":25,"ingredients":["鮭","しめじ","玉ねぎ"]},
    {"id":"R005","name":"カルボナーラ","genre":"洋食","cooking_time_min":15,"ingredients":["スパゲッティ","卵","ベーコン"]},
    {"id":"R006","name":"野菜炒め","genre":"中華","cooking_time_min":15,"ingredients":["キャベツ","豚肉","ごま油"]},
    {"id":"R007","name":"豚の生姜焼き","genre":"和食","cooking_time_min":20,"ingredients":["豚ロース","生姜","醤油"]}
]
```

各レシピは、`id`（レシピID）、`name`（料理名）、`genre`（ジャンル）、`cooking_time_min`（調理時間）、`ingredients`（食材）の5つのフィールドを持ちます。

### MCPサーバーの実装

それでは、MCPサーバーを実装していきます。以下のコマンドを実行して、サーバーのコードを記載するファイルを作成してください。

```bash
# コマンド（chapter5/recipe-agent で実行）
touch 1_server.py
```

作成が完了したらファイルを開き、コードを書いていきます。以降は、1つのファイルのコードを5つのブロックに区切って順番に説明していきます。「(1/5)」のような番号はブロックの順番を表しているので、上から順にファイルへ追記していってください。

まずは、必要なライブラリのインポートとMCPサーバーの初期化です。

```python
# recipe-agent/1_server.py (1/5)
# 必要なライブラリのインポート
import json
from pathlib import Path
from mcp.server.fastmcp import FastMCP

# MCPサーバーの初期化（"recipe-assistant"はサーバー名）
mcp = FastMCP("recipe-assistant")
```

MCPの公式Python SDKに含まれる`FastMCP`を利用して、MCPサーバーのインスタンスを生成します。`FastMCP`は、MCPサーバーを動かすために必要な通信処理やツールの仕様定義を内部で引き受けてくれる仕組みで、開発者はツールの本体ロジックの実装に集中できます。引数の「recipe-assistant」はサーバー名で、ホスト側でこのMCPサーバーを識別するために使われます。

次に、`recipes.json`をMCPサーバー起動時に1度だけ読み込みます。読み込んだリストをモジュールレベルの変数`RECIPES`として保持し、ツールの呼び出しごとに何度もファイルを開かないようにしています。

```python
# recipe-agent/1_server.py (2/5)
# recipes.jsonを起動時に一度だけ読み込み
RECIPES = json.loads((Path(__file__).parent / "recipes.json").read_text(encoding="utf-8"))
```

ここからがMCPサーバーの中核となる、ツールの定義です。`search_recipes`（条件に合うレシピを検索するツール）と`get_recipe_detail`（レシピIDから詳細を取得するツール）の2つを実装します。

まずは1つ目のツール、`search_recipes`です。料理のジャンルと調理時間を受け取り、それらをもとに、データベースから該当するレシピの概要を一覧で返す実装になっています。

```python
# recipe-agent/1_server.py (3/5)
# ツールの定義（@mcp.tool() でMCPツールとして公開される）
@mcp.tool()
def search_recipes(genre: str = "", max_minutes: int = 0) -> str:
    """ジャンル(和食/洋食/中華)や調理時間でレシピを検索する。概要のみ返すので、材料などの詳細はget_recipe_detailで取得すること。"""
    # 引数で渡されたフィルタ条件を順に適用
    hits = RECIPES
    if genre:
        hits = [r for r in hits if r["genre"] == genre]
    if max_minutes > 0:
        hits = [r for r in hits if r["cooking_time_min"] <= max_minutes]
    # 一覧では概要だけを返す（材料は詳細取得側で）
    summary = [
        {"id": r["id"], "name": r["name"], "genre": r["genre"], "cooking_time_min": r["cooking_time_min"]}
        for r in hits
    ]
    return json.dumps(summary, ensure_ascii=False)
```

関数にデコレータ`@mcp.tool()`を付けると、その関数がそのままMCPサーバーのツールとして公開されます。Strands Agentsの`@tool`と同様に、docstring（関数の冒頭に書いた説明文）がツールの説明として呼び出し側のLLMに渡される仕組みとなっています。

次に、2つ目のツールである`get_recipe_detail`を、同じ`1_server.py`に続けて実装します。レシピIDを受け取り、そのレシピの材料を含む詳細情報を返すシンプルな内容になっています。

```python
# recipe-agent/1_server.py (4/5)
@mcp.tool()
def get_recipe_detail(recipe_id: str) -> str:
    """レシピIDから1件の詳細情報(材料を含む)を取得する。"""
    recipe = next((r for r in RECIPES if r["id"] == recipe_id), None)
    if not recipe:
        return f"レシピ{recipe_id}は見つかりません"
    return json.dumps(recipe, ensure_ascii=False)
```

ここで意識したいのは、**2つのツールで役割を分担している**点です。`search_recipes`は概要（ID、料理名、ジャンル、調理時間）だけを返し、材料などの細かい情報は2つ目の`get_recipe_detail`で取得する設計にしています。AIエージェントは「まず一覧で候補を絞り込み、必要なものだけ詳細を取りに行く」という段階的な動き方ができます。ツールの呼び出し回数は増えますが、候補から外れたレシピの詳細情報まで毎回受け取らずに済むため、1回の応答に含まれるデータ量を抑えられます。

最後はMCPサーバーの起動部分になります。`mcp.run()`メソッドを実行することで、MCPサーバーは標準入出力（stdio方式）で起動します。

```python
# recipe-agent/1_server.py (5/5)
# このファイルを直接実行したときにMCPサーバーをstdio方式で起動
if __name__ == "__main__":
    mcp.run()
```

5.2で説明したように、stdio方式はクライアントがサブプロセスとしてMCPサーバーを起動し、標準入出力を介してメッセージをやりとりする方式です。本ハンズオンでは一貫してこの方式を使います。

これで自作のMCPサーバーは完成し、`1_server.py`への記載はここまでです。

なお、この時点で以下のコマンドでMCPサーバーを起動してみても、ターミナルには何も表示されません。

```bash
# コマンド（chapter5/recipe-agent で実行）
uv run 1_server.py
```

これは、stdio方式で動くMCPサーバーが、標準入出力（stdin/stdout）をクライアントとの通信路として使う仕組みになっているためです。MCPサーバーは標準入力にクライアントからのリクエストが届くのを待っている状態で、リクエストが届けばプロトコルに沿った応答を標準出力に書き出します。ターミナルから直接起動した場合はまだ何もリクエストが送られていないため、何も表示されないというわけです。確認できたら **Ctrl + C** キーで終了してください。

## MCPサーバーを利用するAIエージェントの実装

ここから、本ハンズオンの目的である料理レシピアシスタントエージェントを実装していきます。ここまでで実装してきた自作MCPサーバーの`recipe-assistant`に、既製MCPサーバーのFilesystem MCPサーバーを加え、両者のツールを利用するAIエージェントをStrands Agentsを使って構築します。

Filesystem MCPサーバーは、MCP公式のリファレンスサーバーの1つで、ローカルディレクトリ内のファイルの読み書きや検索を行うツールを提供します。Node.jsで実装されており、`@modelcontextprotocol/server-filesystem`というnpmパッケージとして公開されています。

- Filesystem MCPサーバー: https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem

### AIエージェントの実装

料理レシピアシスタントエージェントを実装するために、以下のコマンドを実行してファイルを作成してください。

```bash
# コマンド（chapter5/recipe-agent で実行）
touch 2_agent.py
```

作成できたら、ファイルを開いてコードを記載していきましょう。先ほどと同様に、コードを5つのブロックに区切って順番に説明します。まずは、必要なライブラリのインポートと環境変数の読み込みです。

```python
# recipe-agent/2_agent.py (1/5)
# 必要なライブラリのインポート
import os
from pathlib import Path
from mcp import stdio_client, StdioServerParameters
from strands import Agent
from strands.models.anthropic import AnthropicModel
from strands.tools.mcp import MCPClient
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()
MODEL_ID = os.getenv("MODEL_NAME")
```

Strands Agentsで実装したAIエージェントからMCPサーバーに接続するために、Strands Agentsから提供されている`MCPClient`クラスと、MCP公式SDKの`stdio_client`関数、`StdioServerParameters`クラスを利用します。

次に、Filesystem MCPサーバーがファイルの書き出し先として使う`output`ディレクトリを、AIエージェント実行時に存在しなければ自動的に作成されるようにします。`exist_ok=True`を付けているので、2回目以降に実行してもエラーにはなりません。

```python
# recipe-agent/2_agent.py (2/5)
# Filesystem MCPサーバーは起動時に許可ディレクトリの存在を確認するため、無ければ作成しておく
Path("output").mkdir(exist_ok=True)
```

続いて、2つのMCPサーバーへの接続設定を記載していきます。

```python
# recipe-agent/2_agent.py (3/5)
# MCPサーバーとの通信路（transport）を作る関数を定義（MCPClientが必要なタイミングで内部から呼び出し、サーバーをサブプロセスとして起動する）
def create_recipe_transport():
    # 自作のrecipe-assistant MCPサーバー（同じディレクトリの1_server.pyをサブプロセスで起動）
    return stdio_client(StdioServerParameters(command="uv", args=["run", "1_server.py"]))

def create_filesystem_transport():
    # 既製のFilesystem MCPサーバー（npxで取得して./outputを許可ディレクトリに指定）
    return stdio_client(StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-filesystem", "./output"],
    ))

recipe_client = MCPClient(create_recipe_transport)
fs_client = MCPClient(create_filesystem_transport)
```

ここでは、それぞれのMCPサーバーとの通信路（transport）を作る処理を、別々の関数として定義しています。`stdio_client`関数に起動コマンドを渡すと、そのコマンドをサブプロセスとして起動し、標準入出力を通じてやりとりするための通信路が作られます。自作の`recipe-assistant`は、`1_server.py`をuvで実行してサブプロセスとして起動します。Filesystem MCPサーバーの方も同じくサブプロセスとして起動しますが、こちらはnpxを使ってnpmパッケージをダウンロードしながら立ち上げる、という違いがあります。

この時点ではまだMCPサーバーは起動していません。関数そのものを`MCPClient`に渡しておき、AIエージェントがツールを必要とするタイミングで`MCPClient`が内部から呼び出す、という仕組みになっています。

次に、モデルとシステムプロンプトを定義していきます。

```python
# recipe-agent/2_agent.py (4/5)
# 利用するモデルの指定
model = AnthropicModel(
    model_id=MODEL_ID,
    max_tokens=4096,
)

# システムプロンプトの定義
SYSTEM_PROMPT = """あなたは料理レシピアシスタントです。
recipe-assistantから取得したレシピ情報をもとに、output/ディレクトリにMarkdown形式の献立や買い物リストを作成・更新します。"""
```

システムプロンプトには、**recipe-assistantを情報源とすること**と、**outputディレクトリにMarkdown形式で実行結果を書き出すこと**の2点を伝えています。AIエージェントはこれを踏まえて、ユーザーの依頼に応じてレシピ検索のツールとファイル書き込みのツールを組み合わせて実行します。

最後に、AIエージェントを作成して実行する部分になります。

```python
# recipe-agent/2_agent.py (5/5)
# MCPClientをそのままtoolsに渡すと、Agentがライフサイクル（起動・終了）を自動管理する
agent = Agent(
    model=model,
    system_prompt=SYSTEM_PROMPT,
    tools=[recipe_client, fs_client],
)

# エージェントの実行
agent("30分以内で作れる和食を3つ提案して、output/mealplan.md に保存してください")
```

`Agent`の`tools`引数には、MCPクライアントのインスタンスである`recipe_client`、`fs_client`をそのまま渡すことができます。先ほど定義した`create_recipe_transport`、`create_filesystem_transport`は、AIエージェントがツールを必要としたタイミングでMCPクライアントから呼び出され、MCPサーバーがサブプロセスとして起動します。起動したMCPサーバーからMCPクライアントがツール一覧を取得し、それらをAIエージェントが自分のツールとして利用する、という流れになります。MCPサーバーの終了も含めたライフサイクルはAIエージェント側が管理するため、開発者がそれを意識する必要はありません。Strands Agentsではこの書き方をManaged Integrationと呼んでいます。

- Strands Agents - Integration Approaches: https://strandsagents.com/docs/user-guide/concepts/tools/mcp-tools/#integration-approaches

もう1つ重要なのは、**`recipe_client`と`fs_client`を区別せず、`tools`に並べてAIエージェントに渡している**点です。AIエージェントから見れば、自作したMCPサーバーが提供するツールも、既製のMCPサーバーが提供するツールも、すべて同じように扱うことができます。このように、MCPクライアントがMCPサーバーごとの違いを吸収してくれるため、開発者は「どのMCPサーバーがどんなツールを持つか」を気にせずにMCPサーバーを利用できます。

これで`2_agent.py`への記載は完了です。

### 実装したAIエージェントの実行

コードの記載が完了したら、以下のコマンドからAIエージェントを実行してください。

```bash
# コマンド（chapter5/recipe-agent で実行）
uv run 2_agent.py
```

このコマンドを実行すると、AIエージェントと一緒に2つのMCPサーバーもサブプロセスとして自動的に起動されるため、MCPサーバーを別ターミナルで起動する必要はありません。これはstdio方式で動くMCPサーバーの特徴で、サーバーが常駐する必要があるstreamable HTTP方式のMCPサーバーとは異なる動作です。

正常にAIエージェントが実行されると、最初に以下のようなメッセージが表示されます。

```text
# 出力結果 (1/2)
Secure MCP Filesystem Server running on stdio
Client does not support MCP Roots, using allowed directories set from server args: [ '/workspaces/agent-roadmap/chapter5/recipe-agent/output' ]
```

1文目の「**Secure MCP Filesystem Server running on stdio**」は、Filesystem MCPサーバーがサブプロセスで起動したことを伝えるログで、これからMCPサーバーとstdio方式で通信することの確認になります。

2文目の「**Client does not support MCP Roots, 〜**」は、5.2で紹介したMCPのRoots機能にクライアントが対応していないため、Filesystem MCPサーバー起動時に指定した`output`ディレクトリが許可ディレクトリとして使われる旨のメッセージになっています。

以降は、AIエージェントの実行結果がストリーミングで表示されていきます。実際の実行例が以下になります（LLMの出力のため、実行するたびに内容は異なります）。

```text
# 出力結果 (2/2)
かしこまりました！まず、30分以内の和食レシピを検索します。
Tool #1: search_recipes
[05/16/26 14:32:39] INFO Processing request of type CallToolRequest server.py:727
3件のレシピが見つかりました！次に、3件の詳細情報を同時に取得します。
Tool #2: get_recipe_detail
Tool #3: get_recipe_detail
Tool #4: get_recipe_detail
[05/16/26 14:32:44] INFO Processing request of type CallToolRequest server.py:727
INFO Processing request of type CallToolRequest server.py:727
INFO Processing request of type CallToolRequest server.py:727
詳細が揃いました！次に `output/` ディレクトリを作成し、Markdownファイルを保存します。
Tool #5: create_directory
Tool #6: write_file
`output/mealplan.md` に保存完了しました！✅

---

## 📋 提案した献立まとめ

| # | 料理名 | 調理時間 | 主な材料 |
|---|--------|----------|----------|
| 1 | 🍗 鶏むね肉のグリル | 20分 | 鶏むね肉・塩・オリーブオイル |
| 2 | 🐟 鮭のホイル焼き | 25分 | 鮭・しめじ・玉ねぎ |
| 3 | 🥩 豚の生姜焼き | 20分 | 豚ロース・生姜・醤油 |

3品ともバランスよく、**魚・鶏・豚**と異なるたんぱく質が揃っています。週の献立としてそのままお使いいただけます。買い物リストの作成もできますので、必要であればお知らせください！
```

AIエージェントが以下の流れで動いていることが分かります。

1. `recipe-assistant`のツール`search_recipes`を、ジャンルを和食、調理時間最大30分の条件で呼び出して、レシピの候補を取得
2. 必要に応じてツール`get_recipe_detail`で材料情報を取得
3. Filesystem MCPサーバーのツールを呼び出し、提案内容を`output/mealplan.md`として保存

AIエージェントの実行が完了すると、`output`ディレクトリに`mealplan.md`というファイルができていることを確認してください。ターミナル上に出力された実行結果を要約したものがファイルに出力されています。

ここまでで、自作MCPサーバーと既製MCPサーバーを組み合わせたAIエージェントが動くところまで確認できました。

## Streamlitによるフロントエンドの実装

AIエージェントが完成したので、Streamlitを使ってチャット画面を作成し、ブラウザ上でAIエージェントを利用できるようにしましょう。Streamlitの基本的な使い方は3章のハンズオンで説明しているので、ここでは差分を中心に説明します。

以下のコマンドを実行してStreamlitをインストールし、必要なファイルを作成してください。

```bash
# コマンド（chapter5/recipe-agent で実行）
uv add streamlit==1.60.0
touch 3_gui.py
```

ファイルの作成が完了したら`3_gui.py`を開き、これから説明するコードを記載してください。コードの序盤は`2_agent.py`とほぼ同じです。最初のライブラリのインポート部分では、`asyncio`と`streamlit`のインポートが追加されています。

```python
# recipe-agent/3_gui.py (1/5)
# 必要なライブラリのインポート
import os
import asyncio
from pathlib import Path
import streamlit as st
from mcp import stdio_client, StdioServerParameters
from strands import Agent
from strands.models.anthropic import AnthropicModel
from strands.tools.mcp import MCPClient
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()
MODEL_ID = os.getenv("MODEL_NAME")

# Filesystem MCPサーバーは起動時に許可ディレクトリの存在を確認するため、無ければ作成しておく
Path("output").mkdir(exist_ok=True)

# MCPサーバーとの通信路（transport）を作る関数を定義（MCPClientが必要なタイミングで内部から呼び出し、サーバーをサブプロセスとして起動する）
def create_recipe_transport():
    return stdio_client(StdioServerParameters(command="uv", args=["run", "1_server.py"]))

def create_filesystem_transport():
    return stdio_client(StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-filesystem", "./output"],
    ))
```

続いて、AIエージェントの生成部分です。ここでは`2_agent.py`と書き方が少し異なり、AIエージェントを生成する処理を`init_agent`という関数に切り出し、`@st.cache_resource`というデコレータを付けています。関数の中身そのものは`2_agent.py`で書いたものとほぼ同じです。

```python
# recipe-agent/3_gui.py (2/5)
# Streamlitは操作のたびにスクリプト全体が再実行されるため、@st.cache_resourceでMCPクライアントとエージェントを1度だけ生成し、サブプロセスを使い回す
@st.cache_resource
def init_agent():
    # 自作と既製の2つのMCPサーバーへの接続を作成
    recipe_client = MCPClient(create_recipe_transport)
    fs_client = MCPClient(create_filesystem_transport)

    # MCPClientをそのままtoolsに渡すと、Agentがライフサイクル（起動・終了）を自動管理する
    agent = Agent(
        model=AnthropicModel(model_id=MODEL_ID, max_tokens=4096),
        system_prompt="あなたは料理レシピアシスタントです。recipe-assistantから取得したレシピ情報をもとに、outputディレクトリにMarkdown形式の献立や買い物リストを作成・更新します。",
        tools=[recipe_client, fs_client],
    )
    return agent

agent = init_agent()
```

Streamlitはユーザー操作のたびにスクリプト全体を再実行するため、このデコレータが無いとMCPクライアントもAIエージェントも毎回作り直され、MCPサーバーのサブプロセスが起動・終了を繰り返してしまいます。`@st.cache_resource`は関数の戻り値をキャッシュして使い回すため、初回起動時に立ち上げたサブプロセスをそのまま使い続けることができます。また、AIエージェントのインスタンスも使い回されるため、会話履歴はAIエージェント自身が保持し続けます。

ここから、Streamlitによるフロントエンドの実装部分になります。まずは、ページタイトルの表示と会話履歴の初期化、そして保存された会話履歴の画面への表示部分の実装です。3章でも説明していますが、`st.session_state`オブジェクトは、Streamlitがスクリプトの再実行をまたいで値を保持しておくための領域です。会話履歴をここに格納しておくことで、画面を表示し直しても過去のやりとりが残り続けます。

続く`for`文は、`st.session_state`オブジェクトから会話履歴を1件ずつ画面に表示する処理です。`st.chat_message`オブジェクトに「user」または「assistant」を渡すと、それぞれに対応した吹き出しで表示されます。アシスタントの応答では、呼び出されたツール名も表示しています。

```python
# recipe-agent/3_gui.py (3/5)
# ページタイトルの表示
st.title("🍳 料理レシピアシスタント")

# Streamlitは操作のたびにスクリプト全体が再実行されるため、session_stateで会話履歴を保持
if "messages" not in st.session_state:
    st.session_state.messages = []

# 保存済みの会話履歴を再表示
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        for name in msg.get("tool_names", []):
            st.write(f"🔧 ツール実行: {name}")
        st.markdown(msg["content"])
```

次に、AIエージェントをストリーミング実行して、画面にリアルタイム表示する関数を定義します。

```python
# recipe-agent/3_gui.py (4/5)
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

`agent.stream_async`メソッドはAIエージェントの応答を非同期のイベントとして順次返します。イベントの種類が「data」であれば生成中のテキストを画面に追記し、「current_tool_use」であれば実行されたツール名をstatusコンポーネントに書き込みます。

最後に、ユーザーの入力を受け取ってAIエージェントを呼び出す部分です。

```python
# recipe-agent/3_gui.py (5/5)
# ユーザー入力の処理
if prompt := st.chat_input("レシピや献立について相談してください"):
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
```

`st.chat_input`オブジェクトで受け取ったユーザーの入力を画面に表示したあと、`st.status`オブジェクトでAIエージェントの実行状態を表示するstatusコンポーネントを作成し、`asyncio.run`メソッドで`run_agent`関数を呼び出します。AIエージェントの応答は`st.session_state`オブジェクトに追加されるので、次の入力後も会話が画面に残り続けます。

これでフロントエンドの実装は完了し、`3_gui.py`への記載はここまでです。

### 動作確認

以下のコマンドを実行してStreamlitを起動してみましょう。

```bash
# コマンド（chapter5/recipe-agent で実行）
uv run streamlit run 3_gui.py
```

Streamlitが起動すると、ターミナルにローカルホストのURL「`http://localhost:8501`」が表示されます。これをCmdキー（Windowsの場合はCtrlキー）を押下した状態でクリックすると、ブラウザの新しいタブでアプリケーションを開くことができます。

チャット入力欄に「**30分以内で作れる洋食を3つ提案して、recipeplan.mdに保存して**」のように入力すると、AIエージェントがツールを実行しながらストリーミングで回答し、フロントエンドにリアルタイムで表示されます。また、実行完了後に`output`ディレクトリを見ると、指定したファイル名で実行結果が保存されていることが確認できます。

動作確認後にアプリケーションを終了する際は、まずブラウザのアプリケーションを開いているタブを閉じ、Streamlitを起動しているターミナルで **Ctrl + C** キーを押下してください。

## 次のステップ

以上で、MCPを利用したAIエージェント構築のハンズオンは完了です。MCPの公式Python SDKを使ってレシピ検索MCPサーバーを自作し、既製のFilesystem MCPサーバーと組み合わせて、献立を提案してファイルに書き出す料理レシピアシスタントエージェントを構築しました。AIエージェントから見ると自作のMCPサーバーも既製のMCPサーバーも同じように扱えること、そしてstdio方式のMCPサーバーはAIエージェントの実行に合わせて自動的に起動・終了することを確認できました。

本ハンズオンで自作したMCPサーバーは、Strands Agents以外のMCPホストからもそのまま利用できます。たとえばClaude Codeを利用している場合は、`chapter5/recipe-agent`ディレクトリで以下のコマンドを実行すると`recipe-assistant`を登録でき、Claude Codeとの会話の中で`search_recipes`や`get_recipe_detail`が呼び出されるようになります。MCPサーバー側のコードは何も変えていません。このように、MCPという共通のプロトコルに沿って実装したサーバーは、ホストが変わっても同じものを再利用できます。

```bash
# コマンド（chapter5/recipe-agent で実行）
claude mcp add recipe-assistant -- uv run --directory $(pwd) 1_server.py
```

また、`extra/chapter6/`には、ガードレールとHuman-in-the-Loopを組み込んだAIエージェントのハンズオンを用意しています。あわせて取り組んでみてください。
