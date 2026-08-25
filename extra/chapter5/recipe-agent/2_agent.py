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

# Filesystem MCPサーバーは起動時に許可ディレクトリの存在を確認するため、無ければ作成しておく
Path("output").mkdir(exist_ok=True)

# MCPサーバーを起動するための関数を定義（MCPClientが必要なタイミングで内部から呼び出す）
def start_recipe_server():
    # 自作のrecipe-assistant MCPサーバー（同じディレクトリの1_server.pyをサブプロセスで起動）
    return stdio_client(StdioServerParameters(command="uv", args=["run", "1_server.py"]))

def start_filesystem_server():
    # 既存のFilesystem MCPサーバー（npxで取得して./outputを許可ディレクトリに指定）
    return stdio_client(StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-filesystem", "./output"],
    ))

recipe_client = MCPClient(start_recipe_server)
fs_client = MCPClient(start_filesystem_server)

# 利用するモデルの指定
model = AnthropicModel(
    model_id=MODEL_ID,
    max_tokens=4096,
)

# システムプロンプトの定義
SYSTEM_PROMPT = """あなたは料理レシピアシスタントです。
recipe-assistantから取得したレシピ情報をもとに、output/ディレクトリにMarkdown形式の献立や買い物リストを作成・更新します。"""

# MCPClientをそのままtoolsに渡すと、Agentがライフサイクル（起動・終了）を自動管理する
agent = Agent(
    model=model,
    system_prompt=SYSTEM_PROMPT,
    tools=[recipe_client, fs_client],
)

# エージェントの実行
agent("30分以内で作れる和食を3つ提案して、output/mealplan.md に保存してください")
