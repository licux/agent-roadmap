# 第5章ハンズオン: MCPサーバーで作る料理レシピアシスタント

自作のMCPサーバー (レシピ検索) と、既存のFilesystem MCPサーバー (ファイル読み書き) を組み合わせて、献立や買い物リストを生成するエージェントを作るハンズオンです。

## 前提

- Python 3.10以上
- Node.js (Filesystem MCPサーバーをnpxで起動するため)
- Anthropic APIキー

## 準備

```bash
# 依存ライブラリのインストール
pip install -r requirements.txt

# .envの作成（ANTHROPIC_API_KEYを設定）
cp .env.example .env
# 必要に応じて .env を編集
```

## ステップ1: 自作MCPサーバーの単体動作確認 (MCP Inspector)

```bash
npx @modelcontextprotocol/inspector python 1_server.py
```

ブラウザでInspector UIが開くので、`search_recipes` / `get_recipe_detail` を直接呼び出して結果を確認します。

## ステップ2: コンソールでエージェントを実行

自作MCPサーバーとFilesystem MCPサーバーの両方をエージェントから利用します。

```bash
python 2_client.py
```

`output/mealplan.md` が生成されることを確認してください。

## ステップ3: Streamlitフロントで実行

```bash
streamlit run 3_app.py
```

ブラウザで開いて、自然文でレシピや献立について相談できます。サイドバーに `output/` の中身が表示されます。

## ステップ4: Claude Codeから再利用

自作MCPサーバーとFilesystem MCPサーバーを、Claude Codeにも登録して同じツールを使えるようにします。

```bash
# Claude Code本体のインストール（未インストールの場合）
npm install -g @anthropic-ai/claude-code

# 自作のrecipe-assistantをClaude Codeに登録
claude mcp add recipe-assistant -- python $(pwd)/1_server.py

# Filesystem MCPサーバーを登録（許可ディレクトリは絶対パスで指定）
claude mcp add filesystem -- npx -y @modelcontextprotocol/server-filesystem $(pwd)/output

# 登録状況の確認
claude mcp list

# Claude Codeの起動
claude
# 「30分以内の和食を3つ教えて」「output/に献立を書いて」「R001の材料を教えて」など
```

サーバーを外したいときは:

```bash
claude mcp remove recipe-assistant
claude mcp remove filesystem
```

## ファイル構成

```
.
├── .env.example          # 環境変数テンプレート
├── .gitignore
├── recipes.json          # サンプルレシピデータ (7件)
├── output/               # filesystem MCPサーバーの書き出し先
├── 1_server.py           # 自作MCPサーバー (search_recipes / get_recipe_detail)
├── 2_client.py           # Strands Agent + 2つのMCPサーバー (コンソール実行)
├── 3_app.py              # Streamlitフロント
├── requirements.txt
└── README.md
```

## 補足

- `recipes.json` は時間軸に依存しないフィールド (ジャンル・調理時間・材料) のみで構成しています。読者が自身でレシピを書き足したり差し替えたりしてもそのまま動きます。
- Filesystem MCPサーバーの許可ディレクトリは `./output` に限定しています。プロジェクト全体を許可するとエージェントがどこにでもファイルを書けてしまうため、必要最小限のスコープに絞るのが安全です。
- Claude Desktopでも同様にMCPサーバーを登録できますが、GitHub Codespaces上のサーバーをClaude Desktopから直接呼ぶにはport forwardingなどが必要なため、本書ではClaude Codeを使う構成にしています。
