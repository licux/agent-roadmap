# p.90 ADK for Kotlin のバージョンについて

**種別**: `update` ／ **最終更新**: 2026-09-15

[← 一覧に戻る](README.md)

## 本書の記述

> 2026年7月時点では、Python、TypeScript、Go、Java に加え、Kotlin にも対応しています。
>
> — 3.1.3 Google Agent Development Kit（p.90）

## 更新内容

本書執筆時点で ADK for Kotlin のバージョンは v0.1.0（2026年5月21日リリース）でしたが、**2026年9月9日に v1.0 に到達**しました。

v1.0 では Kotlin Multiplatform（KMP）をコアに据え、ADK Python / ADK Java との機能パリティが
取れています。階層的なマルチエージェント構成、コンテキストの圧縮、Human-in-the-Loop の承認、
KSP を用いたアノテーションベースのツール定義、セッションの再開などが利用でき、
Java との相互運用も一次サポートされました。Android 向けにはオンデバイス推論と、
Android アーキテクチャコンポーネントによる永続化の拡張が用意されています。

なお、各言語版のリリース時期は次のとおりです。ADK は Python から始まりましたが、
本書の執筆時点ですでに5言語すべてが提供されていました。

| 言語             | 初出                                | 2026年9月時点           |
| ---------------- | ----------------------------------- | ----------------------- |
| Python           | 2025年4月（Google Cloud Next 2025） | 2.0 ベータ              |
| Go               | 2025年11月                          | 2.0                     |
| TypeScript       | 2025年12月                          | 2.0 GA                  |
| Java             | 2025年（1.0.0 は2026年4月）         | 1.0 系                  |
| Kotlin / Android | 2026年5月（0.1.0）                  | **1.0（2026年9月9日）** |

## 参考

- [Agent Development Kit 公式サイト](https://adk.dev/)（2026-09-15 参照）
- [Announcing ADK for Kotlin 1.0 - Google Developers Blog](https://developers.googleblog.com/announcing-adk-for-kotlin-10-building-production-ready-ai-agents-in-kotlin-android-and-beyond/)
- [Announcing ADK for Kotlin and ADK for Android 0.1.0 - Google Developers Blog](https://developers.googleblog.com/adk-kotlin-android-building-ai-agents/)

本項は、次の記事でいただいたご指摘をきっかけに追記しました。ありがとうございました。

- [ymd65536 さんのブログ記事](https://ymd65536.hatenablog.com/entry/2026/09/12/122042)
