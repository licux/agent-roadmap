# 第5章ハンズオン 動作検証メモ

## MCPClient のライフサイクル管理 (with句 と Managed Integration)

### 経緯
当初は `2_client.py` / `3_app.py` ともに `ExitStack` を使って2つの MCPClient のライフサイクルを管理していたが、以下の理由で書き換えた。

- `ExitStack` を使うには `with` 句のコンテキストマネージャプロトコルから説明する必要があり、ハンズオンの本筋から逸れる
- そもそも MCPClient が2つだけなら `with A, B:` 構文で十分
- さらに調査の結果、Strands Agents には **Managed Integration** という公式推奨パターンがあり、`Agent(tools=[mcp_client, ...])` に MCPClient を直接渡すだけでライフサイクルを Agent が自動管理してくれることが判明 (`with` も `list_tools_sync()` も不要)

### 採用した書き方の使い分け

| ファイル | 採用パターン | 理由 |
|---|---|---|
| `2_client.py` (基本ハンズオン) | `with recipe_client, fs_client:` で明示管理 | MCPサーバーが**サブプロセスとして起動・終了する**というMCPの本質を、コード構造から読み取れるようにするため |
| `3_app.py` (Streamlit応用) | `Agent(tools=[recipe_client, fs_client])` のManaged Integration | Streamlitの再実行モデル下では `with` 句で囲うと毎回サーバーが再起動されてしまうため、Agent側で生存管理を任せる方が自然 |

### 書籍での説明方針

**`2_client.py` の解説で `with` を説明するときの流れ**

1. MCPサーバーは独立したサブプロセスとして動くため、起動・終了のライフサイクル管理が必要、と前置き
2. Pythonの `with` 句が「ブロックに入るときに開始処理、ブロックを抜けるときに終了処理」を自動で行う構文であることを1行で紹介
3. `with recipe_client, fs_client:` のようにカンマ区切りで複数のコンテキストマネージャを並べられることを明示
4. ブロックの中でツール一覧を取得してエージェントに渡し、ブロックを抜けた時点で2つのサーバープロセスが終了することを説明

サンプル文 (案):

> MCPClientは「コンテキストマネージャ」として実装されており、`with` 句で囲むことで**ブロック開始時にMCPサーバーをサブプロセスとして起動し、ブロックを抜けるときに自動で終了**してくれます。今回のように複数のサーバーを使う場合は、`with recipe_client, fs_client:` のようにカンマで並べて書けば、両方をまとめて管理できます。

**`3_app.py` の解説で Managed Integration に移行する流れ**

1. Streamlitは操作のたびにスクリプト全体を再実行するため、`with` ブロックで囲むと毎回サーバーが起動・終了し、応答が遅くなることを問題提起
2. 「実はStrands Agentsには、`with` を使わずにMCPClientのライフサイクルを管理する仕組みがあります」と転換
3. `Agent(tools=[recipe_client, fs_client])` のように **MCPClientをそのまま `tools` に渡す** だけで、Agent側がライフサイクルを自動管理してくれることを紹介
4. これによりStreamlitの `@st.cache_resource` と組み合わせて、エージェントとMCPサーバーをセッション間で使い回せることを説明
5. **「実はこのManaged Integrationは `2_client.py` のような単純な構成でも使えます。気になる方は `2_client.py` を `with` 句なしで書き換えて動作を確認してみてください」と一言添える** (Streamlit固有の都合だと誤解されないようにするため)

サンプル文 (案):

> 先ほどの `2_client.py` では `with` 句でMCPサーバーのライフサイクルを管理していましたが、Streamlitアプリでは少し事情が異なります。Streamlitは操作のたびにスクリプト全体を再実行するため、毎回サーバーを起動・終了するとレスポンスが遅くなってしまうのです。
>
> こうした場合に便利なのが、Strands Agentsの **Managed Integration** と呼ばれる仕組みです。`Agent(tools=[recipe_client, fs_client])` のようにMCPClientを直接 `tools` に渡せば、Agent側がライフサイクルを自動で管理してくれます。`with` 句や `list_tools_sync()` の呼び出しは不要です。
>
> なお、このManaged Integrationは `3_app.py` だけでなく、先ほどの `2_client.py` のような単純な構成でも問題なく使えます。興味があれば、`2_client.py` を `with` 句なしで書き換えてみると、コードがさらに短くなることが体験できるはずです。

### ポイント

- 2つの書き方を **「明示管理 → 自動管理」という段階的な抽象化** として提示することで、`with` の概念学習と便利機能の両方が身につく構成になる
- 第3章で `@tool` 関数を `tools=[...]` に渡したのと同じ書き方になるため、学習の連続性も保てる
- 「Strands Agents が裏で何をしているのか」を `2_client.py` で見せた上で `3_app.py` で省略するため、"魔法に見える" 抽象化を避けられる
- Managed Integrationが `3_app.py` 専用の解決策ではなく**汎用的に使える書き方**であることを明示することで、読者の応用力を養う

---

## MCPClient の factory 引数 (lambda → 名前付き関数)

### 経緯
`MCPClient` のコンストラクタは **factory function (引数なしで呼ぶと transport を返す関数)** を要求する設計になっており、Strands Agents SDK の初期コミット (2025-05-16) からこの仕様は変わっていない (lambda 不要だった旧APIは存在しない)。

当初は以下のように `lambda` で書いていた:

```python
recipe_client = MCPClient(lambda: stdio_client(
    StdioServerParameters(command="python", args=["1_server.py"])
))
```

しかしハンズオン教材としては、**`lambda` の説明が読者の認知負荷を上げる**懸念があった。すでに `with` 句 (コンテキストマネージャ) の説明も必要なため、両方を併用すると「Pythonの中級トピックを2つ同時に説明する」ことになり、本筋の MCP の話から逸れてしまう。

### 採用した方針: 名前付き関数で factory を表現

```python
# MCPサーバーを起動するための関数を定義（MCPClientが必要なタイミングで内部から呼び出す）
def start_recipe_server():
    return stdio_client(StdioServerParameters(command="python", args=["1_server.py"]))

def start_filesystem_server():
    return stdio_client(StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-filesystem", "./output"],
    ))

recipe_client = MCPClient(start_recipe_server)
fs_client = MCPClient(start_filesystem_server)
```

### この方針の利点

- **`lambda` を一切使わない**: 初学者の認知負荷を軽減
- **`with` 句は残す**: サブプロセスのライフサイクル可視化という教育価値を維持 (= `with` だけ説明すれば済む)
- **factory pattern を名前付き関数で自然に表現**: 関数名 (`start_recipe_server`) から「MCPサーバーを起動する関数」だと直感的に分かるため、"factory" という用語すら導入不要
- **コメント1行で十分**: 「この関数は MCPClient が必要なときに呼び出されます」程度の補足で意図が伝わる

### 書籍での説明方針

サンプル文 (案):

> `MCPClient` には「MCPサーバーを起動するための関数」を渡します。今回は `start_recipe_server` と `start_filesystem_server` という2つの関数を定義しました。これらは **MCPClient が必要になったタイミングで内部から呼び出される** 仕組みになっており、サブプロセスの起動を遅延させることで、`with` 句による正確なライフサイクル管理を可能にしています。

### 他の選択肢を採らなかった理由

| 選択肢 | 不採用の理由 |
|---|---|
| `lambda` のまま | lambda は初学者にとって馴染みが薄く、教材として説明コストが高い |
| `with` を完全に削除 (Managed Integration を `2_client.py` でも採用) | サブプロセスのライフサイクルが見えなくなり、MCPサーバーの動作の本質を伝えられなくなる |
| Strands Agents 自体を諦める | 第3章との連続性を失う、他フレームワークも独自のクセはあり結局トレードオフは残る |

---

## 書籍への反映候補 (まとめ)

- `2_client.py` のコード解説節:
  - **`with` 句によるライフサイクル管理** を1段落で紹介
  - **`MCPClient` に渡す関数 (factory)** の意味を1段落で紹介
  - lambda は使わず名前付き関数で表現
- `3_app.py` のコード解説節:
  - **`Managed Integration` への移行** を導入として配置
  - `with` 句が不要になる仕組みを説明
- `3_app.py` 解説の末尾:
  - 「Managed Integrationは `2_client.py` でも使える」旨の発展的な補足を1行追加
- 補足コラム候補:
  - 「`with` 句の中身 (コンテキストマネージャプロトコル) をもっと知りたい読者向けの参考リンク」
  - 「lambda 式と名前付き関数の使い分け」 (希望者向け、本文には入れない)
