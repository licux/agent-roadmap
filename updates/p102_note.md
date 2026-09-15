# p.102 フレームワークの選び方について

**種別**: `note` ／ **最終更新**: 2026-09-15

[← 一覧に戻る](README.md)

## 本書の記述

> 一方、たとえばフロントエンドからバックエンドまで TypeScript で統一したい場合は、
> Mastra や VoltAgent のような TypeScript で記述することを前提に設計されたフレームワークが
> 有力な選択肢となるでしょう。また、.NET（C#）を主軸とする場合は Microsoft Agent Framework が、
> **Java、Kotlin であれば ADK が、それぞれ現状唯一の選択肢です。**
>
> — 3.1.8 フレームワークの選び方（p.102）

## 補足

本書では、開発に使うプログラミング言語を軸にフレームワークを絞り込む手順を紹介し、Java / Kotlin であれば ADK が「現状唯一の選択肢」であると記載しています。これは、本書で取り上げたフレームワークの中での話であり、Java / Kotlin に対応したものはほかにもあります。

たとえば **Koog**（JetBrains）は、Kotlin と Java の両方に対応した AI エージェントフレームワークで、どちらの言語からも同等の機能を利用できます。処理の流れをグラフとして定義でき、MCP や A2A による連携、AI エージェントの状態の保存と復元、OpenTelemetry によるトレースにも対応しています。

このほか **LangChain4j** や **Spring AI** も、Java で生成AIアプリケーションを構築するフレームワークとして広く使われています。AI エージェント専用ではありませんが、ツール呼び出しなど AI エージェントの構築に必要な機能を備えています。

なお、本書で取り上げているフレームワークは、Python や TypeScript を中心に使われている
ものから選んでいます。ほかのプログラミング言語をお使いの場合は、その言語のエコシステムも
あわせてご確認ください。

## 参考

- [Koog 公式サイト（JetBrains）](https://www.jetbrains.com/koog/)（2026-09-15 参照）
- [Koog 1.0 Is Out - The JetBrains Blog](https://blog.jetbrains.com/ai/2026/05/koog-1-0-is-out-stable-core-better-interop-and-multiplatform-observability/)
- [JetBrains/koog - GitHub](https://github.com/JetBrains/koog)
- [Agent Development Kit 公式サイト](https://adk.dev/)（2026-09-15 参照）

## 謝辞

本項は、ymd65536 さん（X: [@ymd65536](https://x.com/ymd65536)）の次の記事でいただいたご指摘をきっかけに追記しました。ありがとうございました。

- [【書評】AI時代の道しるべ、AIエージェント開発の知識地図 〜仕組みから開発、運用、ガバナンスまで〜](https://ymd65536.hatenablog.com/entry/2026/09/12/122042)
