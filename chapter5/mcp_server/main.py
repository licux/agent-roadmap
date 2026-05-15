# 必要なライブラリのインポート
import json
from pathlib import Path
from mcp.server.fastmcp import FastMCP

# MCPサーバーの初期化（"recipe-assistant"はサーバー名）
mcp = FastMCP("recipe-assistant")

# recipes.jsonを起動時に一度だけ読み込み
RECIPES = json.loads((Path(__file__).parent.parent / "recipes.json").read_text(encoding="utf-8"))

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

@mcp.tool()
def get_recipe_detail(recipe_id: str) -> str:
    """レシピIDから1件の詳細情報(材料を含む)を取得する。"""
    recipe = next((r for r in RECIPES if r["id"] == recipe_id), None)
    if not recipe:
        return f"レシピ{recipe_id}は見つかりません"
    return json.dumps(recipe, ensure_ascii=False)

# このファイルを直接実行したときにMCPサーバーをstdio方式で起動
if __name__ == "__main__":
    mcp.run()
