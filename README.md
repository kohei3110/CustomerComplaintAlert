# 顧客クレームに対する可視化・アラート サンプル

このリポジトリは、顧客クレームを可視化し、アラートを送信するためのサンプルプロジェクトです。Azure Event HubとAzure Blob Storageを使用して、クレームデータを収集および処理します。

## 機能

- Azure Event Hubからのイベントの受信
- Azure Blob Storageからのデータの取得
- クレームデータの解析と可視化
- 一定の条件を満たした場合のアラート送信

## 使用技術

- Python 3.12
- FastAPI
- Azure Event Hub
- Azure Blob Storage
- Pandas
- OpenPyxl

## アーキテクチャ

![アーキテクチャ図](./images/components.png)

## セットアップ

1. リポジトリをクローンします。
    ```sh
    git clone https://github.com/yourusername/customer-complaintalert.git
    cd customer-complaintalert
    ```

2. 必要な依存関係をインストールします。
    ```sh
    poetry install
    ```

3. `.env`ファイルを作成し、必要な環境変数を設定します。
    ```env
    EVENT_HUB_CONNECTION_STR=your_event_hub_connection_string
    EVENT_HUB_NAME=your_event_hub_name
    BLOB_STORAGE_CONNECTION_STR=your_blob_storage_connection_string
    ```

4. アプリケーションを起動します。
    ```sh
    uvicorn presentation.controllers.entry:app --host 0.0.0.0 --port 8000
    ```

## ローカルでの確認コマンド

```sh
uvicorn presentation.controllers.entry:app --reload
```