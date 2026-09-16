# p.94 Microsoft Agent Framework についての補足

**種別**: `note` ／ **最終更新**: 2026-09-16

[← 一覧に戻る](README.md)

---

## Microsoft Agent Framework と Microsoft.Extensions.AI の関係

### 本書の記述

> Microsoft社にはもともと、LLMアプリケーションのためのエンタープライズ向けフレームワークである
> Semantic Kernel と、Microsoft Research が開発したマルチエージェントフレームワークである
> AutoGen がありました。Microsoft Agent Framework はこの両者を統合したもので、（中略）
> 対応言語は Python、.NET（C#）、Go で、2026年4月に v1.0 が一般提供されています。
>
> — 3.1.5 Microsoft Agent Framework（p.94）

### 補足

本書では、 Microsoft Agent Framework を Semantic Kernel と AutoGen の統合という系譜から説明しましたが、**.NET で開発する場合は、 Microsoft.Extensions.AIとの関係も押さえておくと、その位置づけがより明確になります。**

Microsoft.Extensions.AI は、.NET から生成AIを扱うための共通インターフェースを定めた
ライブラリで、2025年5月21日に正式リリースされました。このライブラリを利用することで、モデルの呼び出しや埋め込みの生成といった操作を、モデルの提供元によらず同じ形で書くことができます。

Microsoft Agent Framework の .NET 版は、この Microsoft.Extensions.AI の上に構築されています。.NET Blog（Microsoft の .NET 開発者向け公式ブログ）には次のように記されています。

> The flexibility to use any compatible AI model provider comes from Microsoft.Extensions.AI,
> which standardizes model access through the `IChatClient` interface.

AI エージェントがモデルを呼び出す部分は、Microsoft.Extensions.AI の `IChatClient` というインターフェースが担っています。Microsoft Agent Framework の `ChatClientAgent` クラスはこれを外から受け取る形になっているため、**使うモデルを変えるときは、渡す `IChatClient` を差し替えるだけで、AI エージェント側のコードには手を入れる必要はありません。**

つまり .NET では、**Microsoft.Extensions.AI がモデルとの接続を引き受け、その上で Microsoft Agent Framework が AI エージェントとワークフローを組み立てる**、という役割分担になっています。すでに Microsoft.Extensions.AI を使っているプロジェクトであれば、モデル接続まわりの実装はそのままに、その上に Microsoft Agent Framework を導入できます。

**この関係は .NET に限った話である点にご注意ください。**
Microsoft Agent Framework v1.0 は .NET と Python の2言語で提供されていますが、Microsoft.Extensions.AI は .NET のライブラリであり、Python 版の Microsoft Agent Framework とは関係がありません。

### 参考

- [Introducing Microsoft Agent Framework (Preview) - .NET Blog](https://devblogs.microsoft.com/dotnet/introducing-microsoft-agent-framework-preview/)
- [Microsoft.Extensions.AI libraries - Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/ai/microsoft-extensions-ai)
- [AI and Vector Data Extensions are now Generally Available (GA) - .NET Blog](https://devblogs.microsoft.com/dotnet/ai-vector-data-dotnet-extensions-ga/)

### 謝辞

本項は、ymd65536 さん（X: [@ymd65536](https://x.com/ymd65536)）の次の記事でいただいたご指摘をきっかけに追記しました。ありがとうございました。

- [【書評】AI時代の道しるべ、AIエージェント開発の知識地図 〜仕組みから開発、運用、ガバナンスまで〜](https://ymd65536.hatenablog.com/entry/2026/09/12/122042)

---

## Go 版の提供形態について

### 本書の記述

> Python版、.NET版、Go版で一貫したAPIが提供されているため、チームの言語スキルに応じて選択できます。
>
> （注1）2026年7月時点でパブリックプレビュー。
>
> — 3.1.5 Microsoft Agent Framework（p.94）

### 補足

注釈のとおり Go 版はパブリックプレビューですが、Python 版、.NET 版とは提供形態が異なるため、選定の際は次の点にご注意ください。この状況は2026年9月時点でも変わっていません。

GitHub のリポジトリが分かれており、Python 版と .NET 版は
[microsoft/agent-framework](https://github.com/microsoft/agent-framework)、Go 版は
[microsoft/agent-framework-go](https://github.com/microsoft/agent-framework-go) で開発されています。後者の README には「is in public preview and is currently evolving outside the core upstream codebase」と書かれており、**`microsoft/agent-framework` 側の開発とは切り離して進められているため、そちらに入った変更がそのまま Go 版に反映されるわけではありません。**

`microsoft/agent-framework-go` の README の Preview status には、宣言的エージェント（Declarative agents）、RAG、CodeAct、functional workflows が未提供として挙げられています。このほかにも、Handoff orchestration や Foundry-hosted deployment、DevUI など、Go SDK では未実装とされている機能があります。3つの言語で同じ考え方のAPIを提供するという方針に変わりはありませんが、**Go 版で実際に使える機能は、現時点では Python 版・.NET 版で使える機能の一部にとどまります。** Go を主軸に据える場合は、必要な機能が実装済みかどうかを事前にご確認ください。

### 参考

- [microsoft/agent-framework-go - GitHub](https://github.com/microsoft/agent-framework-go)（2026-09-16 参照）
- [Microsoft Agent Framework Version 1.0](https://devblogs.microsoft.com/agent-framework/microsoft-agent-framework-version-1-0/)
