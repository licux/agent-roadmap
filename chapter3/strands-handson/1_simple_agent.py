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