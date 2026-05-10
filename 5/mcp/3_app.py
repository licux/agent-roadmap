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
MODEL_ID = os.getenv("CLAUDE_MODEL_ID", "claude-sonnet-4-6")

# Streamlitは操作のたびにスクリプト全体が再実行されるため、@st.cache_resourceでMCPクライアントとエージェントを1度だけ生成し、サブプロセスを使い回す
@st.cache_resource
def init_agent():
    # Filesystem MCPサーバーは起動時に許可ディレクトリの存在を確認するため、無ければ作成しておく
    Path("output").mkdir(exist_ok=True)

    # 自作と既存の2つのMCPサーバーへの接続を作成
    recipe_client = MCPClient(lambda: stdio_client(
        StdioServerParameters(command="python", args=["1_server.py"])
    ))
    fs_client = MCPClient(lambda: stdio_client(
        StdioServerParameters(
            command="npx",
            args=["-y", "@modelcontextprotocol/server-filesystem", "./output"],
        )
    ))

    # MCPClientをそのままtoolsに渡すと、Agentがライフサイクル（起動・終了）を自動管理する
    agent = Agent(
        model=AnthropicModel(model_id=MODEL_ID, max_tokens=4096),
        system_prompt="あなたは料理アドバイザーです。recipe-assistantから取得したレシピ情報をもとに、output/ディレクトリにMarkdown形式の献立や買い物リストを作成・更新します。",
        tools=[recipe_client, fs_client],
    )
    return agent

agent = init_agent()

# ページタイトルの表示
st.title("🍳 料理レシピアシスタント")

# サイドバーにoutput/ディレクトリの内容を表示（filesystem MCPサーバーが書き出した結果が確認できる）
with st.sidebar:
    st.header("output/")
    output_dir = Path("output")
    files = sorted(output_dir.glob("*.md")) if output_dir.exists() else []
    if files:
        for f in files:
            with st.expander(f"📄 {f.name}"):
                st.markdown(f.read_text(encoding="utf-8"))
    else:
        st.write("（まだファイルがありません）")

# Streamlitは操作のたびにスクリプト全体が再実行されるため、session_stateで会話履歴を保持
if "messages" not in st.session_state:
    st.session_state.messages = []

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

    # サイドバーのoutput/一覧を最新化するため再描画（会話履歴はsession_stateに残るので消えない）
    st.rerun()
