# PlanetSide 2 日本語翻訳データ管理ツール

[![GitHub issues](https://img.shields.io/github/issues/nusashi/PlanetSide2-nihongo-mod-api?style=flat-square)](https://github.com/nusashi/PlanetSide2-nihongo-mod-api/issues)
[![GitHub license](https://img.shields.io/github/license/nusashi/PlanetSide2-nihongo-mod-api?style=flat-square)](https://github.com/nusashi/PlanetSide2-nihongo-mod-api/blob/main/LICENSE)

このリポジトリは、[PlanetSide 2 日本語化MOD管理ツール](https://github.com/nusashi/PlanetSide2-nihongo-mod-ui)で使用する翻訳データを生成・管理するためのツールを提供します。
Google スプレッドシートと連携し、翻訳データの差分検出、.datファイルおよび.dirファイルの生成を自動化します。

## 特徴

*   **スプレッドシート連携**: Google スプレッドシートを翻訳データのマスターとして利用。
*   **差分検出**: ゲームファイルの更新を検出し、スプレッドシートとの差分を抽出。
*   **自動生成**: 翻訳データファイル (.dat) とインデックスファイル (.dir) を自動生成。
*   **容易なメンテナンス**: スプレッドシートを編集するだけで、翻訳データを更新可能。

## Daybreak Game Company への感謝

長年にわたり、PlanetSide 2 という素晴らしいゲームを提供し続けてくださっている Daybreak Game Company に深く感謝いたします。

## 謝辞

初期の日本語化MOD開発から、長年にわたるメンテナンス、そして新たなフォントの導入まで、PlanetSide 2の日本語プレイ環境の礎を築いてくださった、spoon氏、besuda氏、take8763氏に心より感謝申し上げます。

## ライセンス

*   **翻訳データ**: CC0 (クリエイティブ・コモンズ ゼロ)
    *   以前のMODの翻訳データと、新規に翻訳・修正したデータを含みます。
    *   誰でも自由に利用・改変・再配布できます。

*   **プログラム**: MIT License
    *   ソースコードを自由に利用・改変・再配布できます。
    *   詳細は [LICENSE](https://github.com/nusashi/PlanetSide2-nihongo-mod-api/blob/main/LICENSE) ファイルをご覧ください。


## 免責事項

*   本MODは、Daybreak Game Company LLC (以下、Daybreak) が提供する PlanetSide 2 の非公式MODであり、Daybreak とは一切関係ありません。
*   PlanetSide 2 は Daybreak の登録商標であり、関連する全てのアートワーク、ストーリー、スクリーンショット、ゲーム内データなどの表現物は Daybreak の知的財産です。
*   本MODは、Daybreak が許諾する範囲内でこれらの表現物を使用していますが、Daybreak は本MODの内容についていかなる保証も行いません。
*   本MODの使用、インストール、または本MODに関連する利用に起因するいかなる損害 (データの損失、ゲームの不具合、アカウントの停止などを含むがこれらに限定されない) についても、Daybreak および本MODの開発者は一切の責任を負いません。
*   本MODの使用は自己責任でお願いします。
*   本MODの導入によって生じたいかなる問題についても、Daybreakへの問い合わせは行わないでください。

## 使い方

1.  **環境構築**
    *   必要なライブラリのインストール
        ```
        pip install -r requirements.txt
        ```
    *   `.env`ファイルの設定 詳細は[DEVELOPER_README.md](https://github.com/nusashi/PlanetSide2-nihongo-mod-api/blob/main/DEVELOPER_README.md)ファイルをご覧ください。
2.  **実行方法**
    *   `create.py`の実行方法: スプレッドシートから翻訳データを取得し、`.dat`ファイルと`.dir`ファイルを作成します。
    *   `update.py`の実行方法: 既存の`.dat`ファイルと`.dir`ファイルを読み込み、スプレッドシートのデータと比較して差分を検出し、スプレッドシートを更新します。

## 生成されるファイルについて

*   `ja_jp_data.dat`ファイル: 翻訳されたテキストデータ
*   `ja_jp_data.dir`ファイル: テキストデータのメタ情報

## 更新履歴

*   2025/2/7 v0.0.1      初版リリース

## バグ報告・要望

バグ報告や要望は、[Issues](https://github.com/nusashi/PlanetSide2-nihongo-mod-api/issues)からお知らせいただくか、以下の連絡先までご連絡ください。

*   不具合・質問: ぬさし([https://x.com/nusashi](https://x.com/nusashi))、seigo2016([https://x.com/seigo2018](https://x.com/seigo2018))
*   翻訳について: mossy([https://x.com/Mossstone_1mzn9](https://x.com/Mossstone_1mzn9))


Copyright © 2025 PlanetSide2 日本語化MOD 開発チーム
