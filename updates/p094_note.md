# p.94 Microsoft Agent Framework について

**種別**: `note` ／ **最終更新**: 2026-09-15

[← 一覧に戻る](README.md)

本ページに関する追加説明が2件あります。

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

本書では Microsoft Agent Framework を Semantic Kernel と AutoGen の統合という
系譜から説明しましたが、**.NET で開発する場合は、 Microsoft.Extensions.AI
との関係も押さえておくと、その位置づけが明確になります。** 読者の方からご指摘をいただいたため補足します。

Microsoft.Extensions.AI は、.NET における生成AI機能の抽象化レイヤーです。
`IChatClient`（チャット系モデルへのアクセス）と `IEmbeddingGenerator<TInput, TEmbedding>`
（埋め込み生成）を中核とし、2025年5月21日に正式リリースされています。特定のモデルプロバイダーに依存しないインターフェースを提供し、キャッシュ・テレメトリ・レートリミットといったミドルウェアを重ねられる点が特徴です。

Microsoft Agent Framework の .NET 版は、この Microsoft.Extensions.AI の上に構築されています。
Microsoft の .NET Blog には次のように記されています。

> Microsoft Agent Framework leverages established technologies to simplify agent development
> for .NET developers: **Semantic Kernel** – Provides robust orchestration;
> **AutoGen** – Enables advanced multi-agent collaboration and cutting-edge research-driven
> techniques; **Microsoft.Extensions.AI** – Delivers standardized AI building blocks for .NET.

> The flexibility to use any compatible AI model provider comes from Microsoft.Extensions.AI,
> which standardizes model access through the `IChatClient` interface.

具体的な接点は `ChatClientAgent` です。任意の `IChatClient` を受け取る設計になっているため、
OpenAI、Azure OpenAI、Microsoft Foundry、Ollama、GitHub Models といったプロバイダーを、
エージェント側のコードを変えずに差し替えられます。

.NET における AI 開発の技術スタックを整理すると、次のようになります。

```
Microsoft Agent Framework   エージェントとワークフローの層
                            （2025年10月プレビュー / 2026年4月 v1.0）
        ↑
Semantic Kernel             オーケストレーションの層（MAF に統合）
        ↑
Microsoft.Extensions.AI     モデルアクセスの抽象化層（2025年5月 GA）
        ↑
各モデルプロバイダーの SDK
```

**この関係は .NET に限った話である点にご注意ください。**
Microsoft Agent Framework v1.0 は .NET と Python の2言語で提供されていますが、Microsoft.Extensions.AI は
.NET のライブラリであり、Python 版の Microsoft Agent Framework とは関係がありません。

### 参考

- [Introducing Microsoft Agent Framework (Preview) - .NET Blog](https://devblogs.microsoft.com/dotnet/introducing-microsoft-agent-framework-preview/)
- [Microsoft.Extensions.AI libraries - Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/ai/microsoft-extensions-ai)
- [AI and Vector Data Extensions are now Generally Available (GA) - .NET Blog](https://devblogs.microsoft.com/dotnet/ai-vector-data-dotnet-extensions-ga/)

本項は、次の記事でいただいたご指摘をきっかけに追記しました。ありがとうございました。

- [ymd65536 さんのブログ記事](https://ymd65536.hatenablog.com/entry/2026/09/12/122042)

---

## Go 版の提供形態について

### 本書の記述

> Python版、.NET版、Go版で一貫したAPIが提供されているため、チームの言語スキルに応じて
> 選択できます。
>
> （注1）2026年7月時点でパブリックプレビュー。
>
> — 3.1.5 Microsoft Agent Framework（p.94）

### 補足

注釈のとおり Go 版はパブリックプレビューですが、Python 版、.NET 版とは提供形態が異なるため、選定の際は次の点にご注意ください。この状況は2026年9月時点でも変わっていません。

Go 版は `microsoft/agent-framework` ではなく、**`microsoft/agent-framework-go` という別の
リポジトリ**で開発されています。README には
「is in public preview and is currently evolving outside the core upstream codebase」
と記載されており、コア本体とは別の歩調で進んでいます。

2026年9月時点では、宣言的エージェント（Declarative agents）、RAG、CodeAct、
functional workflows が未実装です。「一貫したAPI」は設計方針としては正しいものの、
**現時点で Go 版から使える機能は Python 版・.NET 版の部分集合**とお考えください。
Go を主軸に据える場合は、必要な機能が実装済みかを事前にご確認ください。

なお v1.0 の一般提供（2026年4月3日）は .NET 版と Python 版が対象で、Go 版は含まれていません。

### 参考

- [microsoft/agent-framework-go - GitHub](https://github.com/microsoft/agent-framework-go)（2026-09-15 参照）
- [Microsoft Agent Framework Version 1.0](https://devblogs.microsoft.com/agent-framework/microsoft-agent-framework-version-1-0/)
