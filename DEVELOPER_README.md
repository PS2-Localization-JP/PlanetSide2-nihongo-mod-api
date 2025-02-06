# 開発者向け情報

このドキュメントでは、このプロジェクトを開発する上で必要な情報を提供します。

## 環境変数

以下の環境変数を設定する必要があります。

*   `LATEST_DAT_PATH`: 最新の`.dat`ファイルのパス (例: `c:/SteamLibrary/steamapps/common/PlanetSide 2/Locale/en_us_data.dat`)
*   `LATEST_DIR_PATH`: 最新の`.dir`ファイルのパス (例: `c:/SteamLibrary/steamapps/common/PlanetSide 2/Locale/en_us_data.dir`)
*   `ADMIN_EMAIL`: 管理者のメールアドレス
*   `GOOGLE_CREDENTIALS_PATH`: Google Cloudの認証情報ファイルのパス (例: `planetside2jp-translate.json`)
*   `GOOGLE_SPREADSHEET_ID`: GoogleスプレッドシートのID

これらの環境変数は、`.env`ファイルに記述します。

例:

```
LATEST_DAT_PATH=c:/SteamLibrary/steamapps/common/PlanetSide 2/Locale/en_us_data.dat
LATEST_DIR_PATH=c:/SteamLibrary/steamapps/common/PlanetSide 2/Locale/en_us_data.dir
ADMIN_EMAIL=your_email@example.com
GOOGLE_CREDENTIALS_PATH=planetside2jp-translate.json
GOOGLE_SPREADSHEET_ID=your_spreadsheet_id
```

## Google Cloud 認証情報

Google Sheets APIを使用するには、Google Cloudの認証情報が必要です。

1.  Google Cloud Consoleでプロジェクトを作成します。
2.  サービスアカウントを作成し、JSON形式の認証情報をダウンロードします。
3.  ダウンロードしたJSONファイルを`GOOGLE_CREDENTIALS_PATH`で指定します。

## planetside2jp-translate.json (サンプル)

このファイルには、Google Cloudのサービスアカウントの認証情報が含まれています。

```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "your-private-key-id",
  "private_key": "-----BEGIN PRIVATE KEY-----\nyour-private-key\n-----END PRIVATE KEY-----\n",
  "client_email": "your-service-account@your-project-id.iam.gserviceaccount.com",
  "client_id": "your-client-id",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project-id.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}
```

**注意**

*   `private_key`は機密情報なので、安全に保管してください。
*   このファイルは、Gitリポジトリにコミットしないでください。
