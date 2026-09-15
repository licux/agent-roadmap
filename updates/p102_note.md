# p.102 Google ADKの選定基準について

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

この「唯一」は、3.1.8「フレームワークの選び方」で取り上げた**表3.3 の6つ
（OpenAI Agents SDK / ADK / Strands Agents / Microsoft Agent Framework / Mastra / LangChain）
の中では**、という意味で書いたものですが、**文中にその射程を明示していませんでした。**

言語からフレームワークを選ぶという実務の場面で読むと、範囲を限定しない断定として受け取れてしまうため、実際の状況を以下に補足します。

### Java / Kotlin — ADK 以外にも選択肢があります

とくに **Koog**（JetBrains）は、Kotlin と Java の両方に対応した AIエージェントフレームワークです。KotlinConf 2025 で発表され、**2026年5月の KotlinConf 2026 で 1.0 に到達**しています。本書の執筆時点ですでに 1.0 でした。

JVM と Kotlin Multiplatform を対象とし、ツール、ワークフロー、永続化、メモリ、OpenTelemetry によるオブザーバビリティを備えるほか、Android 上での LiteRT によるローカルモデル実行にも対応しています。

このほか、AI エージェント専用ではないものの、**LangChain4j** や **Spring AI** も Java で生成AIアプリケーションを構築するフレームワークとして広く使われており、ツール呼び出しなどAIエージェントに対応した機能を備えています。

したがって「Java、Kotlin であれば ADK が唯一」は、本書で取り上げた範囲での話であり、
Java / Kotlin 全体を見渡した記述としては不正確です。お詫びして訂正します。

## 参考

- [Koog 公式サイト（JetBrains）](https://www.jetbrains.com/koog/)（2026-09-15 参照）
- [Koog 1.0 Is Out - The JetBrains Blog](https://blog.jetbrains.com/ai/2026/05/koog-1-0-is-out-stable-core-better-interop-and-multiplatform-observability/)
- [JetBrains/koog - GitHub](https://github.com/JetBrains/koog)
- [Agent Development Kit 公式サイト](https://adk.dev/)（2026-09-15 参照）
- 本書 p.90、表3.3（p.101）

本項は、次の記事でいただいたご指摘をきっかけに追記しました。ありがとうございました。

- [ymd65536 さんのブログ記事](https://ymd65536.hatenablog.com/entry/2026/09/12/122042)
