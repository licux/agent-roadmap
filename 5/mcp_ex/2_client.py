# Strands Agents を使わず、Anthropic SDK と MCP SDK だけで同じことを実現する例。
# 比較のため、5/mcp/2_client.py と同じ動作をするように書いている。
#
# 実行方法（5/mcp_ex ディレクトリで）:
#   uv run python 2_client.py

import asyncio
import os
from pathlib import Path

from anthropic import Anthropic
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()
MODEL_ID = os.getenv("CLAUDE_MODEL_ID")
Path("output").mkdir(exist_ok=True)

SYSTEM_PROMPT = """あなたは料理アドバイザーです。
recipe-assistantから取得したレシピ情報をもとに、output/ディレクトリにMarkdown形式の献立や買い物リストを作成・更新します。"""

USER_PROMPT = "30分以内で作れる和食を3つ提案して、output/mealplan.md に保存してください"


async def main():
    recipe_params = StdioServerParameters(command="python", args=["../mcp/1_server.py"])
    fs_params = StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-filesystem", "./output"],
    )

    # 2つのMCPサーバーへの接続をネストしたasync withで管理
    async with stdio_client(recipe_params) as (rr, rw), \
               stdio_client(fs_params) as (fr, fw), \
               ClientSession(rr, rw) as recipe_session, \
               ClientSession(fr, fw) as fs_session:

        await recipe_session.initialize()
        await fs_session.initialize()

        # 各サーバーのツールを Anthropic API 形式に変換し、「ツール名 → 担当セッション」のマップも作る
        tool_to_session = {}
        anthropic_tools = []
        for session in [recipe_session, fs_session]:
            for t in (await session.list_tools()).tools:
                tool_to_session[t.name] = session
                anthropic_tools.append({
                    "name": t.name,
                    "description": t.description or "",
                    "input_schema": t.inputSchema,
                })

        # エージェントループ：LLM呼び出し → tool_use があれば実行して結果を返す、を繰り返す
        client = Anthropic()
        messages = [{"role": "user", "content": USER_PROMPT}]

        while True:
            response = client.messages.create(
                model=MODEL_ID,
                max_tokens=4096,
                system=SYSTEM_PROMPT,
                tools=anthropic_tools,
                messages=messages,
            )
            messages.append({"role": "assistant", "content": response.content})

            if response.stop_reason != "tool_use":
                for block in response.content:
                    if block.type == "text":
                        print(block.text)
                break

            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    print(f"Tool #{block.name}: {block.input}")
                    result = await tool_to_session[block.name].call_tool(block.name, block.input)
                    text = "".join(c.text for c in result.content if hasattr(c, "text"))
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": text,
                    })
            messages.append({"role": "user", "content": tool_results})


if __name__ == "__main__":
    asyncio.run(main())
