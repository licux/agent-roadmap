# p.90 ADK for Kotlin のバージョンについて

**種別**: `update` ／ **最終更新**: 2026-09-15

[← 一覧に戻る](README.md)

## 本書の記述

> 2026年7月時点では、Python、TypeScript、Go、Java に加え、Kotlin にも対応しています。
>
> — 3.1.3 Google Agent Development Kit（p.90）

## 更新内容

本書執筆時点で ADK for Kotlin のバージョンは v0.1.0（2026年5月21日リリース）でしたが、**2026年9月9日に v1.0 に到達**しました。

v1.0 では、**ADK の Python 版、Java 版と同じことが Kotlin でも一通りできる**ようになっています。階層的なマルチエージェント構成、Human-in-the-Loop による承認、長い対話のコンテキスト圧縮、中断したセッションの再開などが利用できます。
また、ツールの定義も、アノテーションを付けるだけで済むようになりました。

Kotlin 版ならではの強化も2点あります。1つは **Java からの利用が正式にサポート**されたこと、もう1つは Kotlin Multiplatform をコアに据えたことで、**Android アプリ内でオンデバイス推論を動かせる**ようになったことです。サーバーサイドの JVM アプリケーションから Android 端末まで、同じ書き方でエージェントを構築できます。

## 参考

- [Agent Development Kit 公式サイト](https://adk.dev/)（2026-09-15 参照）
- [Announcing ADK for Kotlin 1.0 - Google Developers Blog](https://developers.googleblog.com/announcing-adk-for-kotlin-10-building-production-ready-ai-agents-in-kotlin-android-and-beyond/)
- [Announcing ADK for Kotlin and ADK for Android 0.1.0 - Google Developers Blog](https://developers.googleblog.com/adk-kotlin-android-building-ai-agents/)

本項は、次の記事でいただいたご指摘をきっかけに追記しました。ありがとうございました。

- [ymd65536 さんのブログ記事](https://ymd65536.hatenablog.com/entry/2026/09/12/122042)
