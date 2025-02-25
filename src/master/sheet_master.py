import os
import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account


class SheetMaster:
    def __init__(self, credentials_path, spreadsheet_id, admin_email=None):
        """
        :param spreadsheet_id: 操作対象のスプレッドシートID
        :param admin_email: 管理者のメールアドレス
        :param credentials_path: ローカル実行時に利用するサービスアカウント認証ファイルのパス
        """
        self.spreadsheet_id = spreadsheet_id
        self.admin_email = admin_email
        self.credentials_path = credentials_path  # ローカル用の認証ファイルパス
        self.protected_sheets = {}  # 保護されたシート名とIDの辞書
        self.service = self._get_sheets_service()

    def _get_credentials(self):
        """
        環境変数 "CI" の値により認証方法を切り替え
          - CI環境の場合: google.auth.default() を利用（Workload Identity Federation経由）
          - ローカルの場合: credentials_path から認証ファイルを読み込む
        """
        creds = None
        if os.environ.get("CI", "").lower() == "true":
            # CI環境（例: GitHub Actions で Workload Identity Federation がセットアップ済みの場合）
            creds, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/spreadsheets"])
        else:
            if os.path.exists(self.credentials_path):
                creds = service_account.Credentials.from_service_account_file(
                    self.credentials_path,
                    scopes=["https://www.googleapis.com/auth/spreadsheets"],
                )
        return creds

    def _get_sheets_service(self):
        try:
            creds = self._get_credentials()
            service = build("sheets", "v4", credentials=creds)
            return service
        except HttpError as error:
            print(f"An error occurred: {error}")
            print(f"Details: {error.content}")
            return None

    def protect_sheet(self, sheet_name):
        """シートを保護する"""
        if not self.service:
            print("Error: Google Sheets service not initialized.")
            return
        # 管理者メールアドレスが設定されていない場合は、保護しない
        if not self.admin_email:
            print("Warning: Admin email not set. Sheet will not be protected.")
            return
        try:
            # シートIDを取得
            sheet_id = self._get_sheet_id(sheet_name)
            if sheet_id is None:
                print(f"Sheet '{sheet_name}' not found.")
                return

            # 認証情報からサービスアカウントのメールアドレスを取得
            creds = self._get_credentials()
            service_account_email = getattr(creds, "service_account_email", None)

            body = {
                "requests": [
                    {
                        "addProtectedRange": {
                            "protectedRange": {
                                "range": {"sheetId": sheet_id},
                                "editors": {
                                    "users": (
                                        [self.admin_email, service_account_email]
                                        if self.admin_email and service_account_email
                                        else ([service_account_email] if service_account_email else [])
                                    ),
                                    "groups": [],
                                    "domainUsersCanEdit": False,
                                },
                                "warningOnly": False,
                                "requestingUserCanEdit": True,  # サービスアカウントは常に編集可能
                            }
                        }
                    }
                ]
            }
            # 保護設定を適用
            response = (
                self.service.spreadsheets()
                .batchUpdate(spreadsheetId=self.spreadsheet_id, body=body)
                .execute()
            )
            # 保護されたシートの情報を保存
            self.protected_sheets[sheet_name] = sheet_id
            print(f"Sheet '{sheet_name}' protected successfully.")
            return response
        except HttpError as error:
            print(f"An error occurred: {error}")
            return None

    def unprotect_sheet(self, sheet_name):
        """シートの保護を解除する"""
        if not self.service:
            print("Error: Google Sheets service not initialized.")
            return

        # 管理者権限があるか確認
        if not self.admin_email or not self.is_admin():
            print(f"Error: Sheet '{sheet_name}' can only be unprotected by administrators.")
            return None

        try:
            # シートIDを取得
            sheet_id = self._get_sheet_id(sheet_name)
            if sheet_id is None:
                print(f"Sheet '{sheet_name}' not found.")
                return
            # 保護設定を検索
            protection_id = self._get_protection_id(sheet_id)
            if protection_id is None:
                print(f"No protection found for sheet '{sheet_name}'.")
                return
            # 保護解除リクエストを作成
            body = {"requests": [{"deleteProtectedRange": {"protectedRangeId": protection_id}}]}
            # 保護解除を実行
            response = (
                self.service.spreadsheets()
                .batchUpdate(spreadsheetId=self.spreadsheet_id, body=body)
                .execute()
            )
            # 保護されたシートの情報を削除
            if sheet_name in self.protected_sheets:
                del self.protected_sheets[sheet_name]
            print(f"Sheet '{sheet_name}' unprotected successfully.")
            return response
        except HttpError as error:
            print(f"An error occurred: {error}")
            return None

    def _get_sheet_id(self, sheet_name):
        """シート名からシートIDを取得する"""
        try:
            spreadsheet = (
                self.service.spreadsheets()
                .get(spreadsheetId=self.spreadsheet_id)
                .execute()
            )
            sheets = spreadsheet.get("sheets", [])
            for sheet in sheets:
                if sheet["properties"]["title"] == sheet_name:
                    return sheet["properties"]["sheetId"]
            return None
        except HttpError as error:
            print(f"An error occurred: {error}")
            return None

    def _get_protection_id(self, sheet_id):
        """シートIDから保護設定IDを取得する"""
        try:
            spreadsheet = (
                self.service.spreadsheets()
                .get(spreadsheetId=self.spreadsheet_id)
                .execute()
            )
            sheets = spreadsheet.get("sheets", [])
            for sheet in sheets:
                if sheet["properties"]["sheetId"] == sheet_id:
                    for protected_range in sheet.get("protectedRanges", []):
                        return protected_range["protectedRangeId"]
            return None
        except HttpError as error:
            print(f"An error occurred: {error}")
            return None

    def update_sheet(self, sheet_name, data):
        """シートを更新する"""
        if not self.service:
            print("Error: Google Sheets service not initialized.")
            return

        # シートが保護されているか確認
        if sheet_name in self.protected_sheets:
            # 管理者権限があるか確認
            if not self.admin_email or not self.is_admin():
                print(f"Error: Sheet '{sheet_name}' is protected. Only administrators can update it.")
                return None

        try:
            body = {"values": data}
            result = (
                self.service.spreadsheets()
                .values()
                .update(
                    spreadsheetId=self.spreadsheet_id,
                    range=sheet_name,
                    valueInputOption="USER_ENTERED",
                    body=body,
                )
                .execute()
            )
            print(f"{sheet_name} sheet updated successfully.")
            return result
        except HttpError as error:
            print(f"An error occurred: {error}")
            return None

    def clear_sheet(self, sheet_name):
        """シートをクリアする"""
        if not self.service:
            print("Error: Google Sheets service not initialized.")
            return

        # シートが保護されているか確認
        if sheet_name in self.protected_sheets:
            # 管理者権限があるか確認
            # admin_email が設定されていない場合も許可しない
            if not self.admin_email or not self.is_admin():
                print(f"Error: Sheet '{sheet_name}' is protected. Only administrators can clear it.")
                return None

        try:
            result = (
                self.service.spreadsheets()
                .values()
                .clear(spreadsheetId=self.spreadsheet_id, range=sheet_name)
                .execute()
            )
            print(f"{sheet_name} sheet cleared successfully.")
            return result
        except HttpError as error:
            print(f"An error occurred: {error}")
            return None

    def get_sheet_data(self, sheet_name):
        """シートのデータを取得する"""
        if not self.service:
            print("Error: Google Sheets service not initialized.")
            return None

        try:
            result = (
                self.service.spreadsheets()
                .values()
                .get(spreadsheetId=self.spreadsheet_id, range=sheet_name)
                .execute()
            )
            return result.get("values", [])
        except HttpError as error:
            print(f"An error occurred: {error}")
            return None

    def is_admin(self):
        """管理者権限があるか確認する"""
        if not self.admin_email:
            return False
        creds = self._get_credentials()
        service_account_email = getattr(creds, "service_account_email", None)
        return service_account_email == self.admin_email if service_account_email else False
