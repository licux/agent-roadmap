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
MODEL_ID = os.getenv("CLAUDE_MODEL_ID")

# Filesystem MCPサーバーは起動時に許可ディレクトリの存在を確認するため、無ければ作成しておく
Path("output").mkdir(exist_ok=True)

# 自作のrecipe-assistant MCPサーバーへの接続設定（同じディレクトリの1_server.pyをサブプロセスで起動）
recipe_client = MCPClient(lambda: stdio_client(
    StdioServerParameters(command="python", args=["1_server.py"])
))

# 既存のFilesystem MCPサーバーへの接続設定（npxで取得して./outputを許可ディレクトリに指定）
fs_client = MCPClient(lambda: stdio_client(
    StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-filesystem", "./output"],
    )
))

# 利用するモデルの指定
model = AnthropicModel(
    model_id=MODEL_ID,
    max_tokens=4096,
)

# システムプロンプトの定義
SYSTEM_PROMPT = """あなたは料理アドバイザーです。
recipe-assistantから取得したレシピ情報をもとに、output/ディレクトリにMarkdown形式の献立や買い物リストを作成・更新します。"""

# 2つのMCPサーバーをwith句でまとめて起動・終了（ブロックを抜けるとサブプロセスが終了する）
with recipe_client, fs_client:
    # 両サーバーから提供されているツールを取得して結合
    tools = recipe_client.list_tools_sync() + fs_client.list_tools_sync()

    # エージェントの作成（自作ツールと既存ツールを区別せず1つのリストで渡す）
    agent = Agent(
        model=model,
        system_prompt=SYSTEM_PROMPT,
        tools=tools,
    )

    # エージェントの実行
    agent("30分以内で作れる和食を3つ提案して、output/mealplan.md に保存してください")
