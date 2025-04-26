from enum import Enum

# 定数宣言
UTF8BOM_START_BYTE = "\ufeff"


# 基底クラス: TableColumns
class TableColumns(Enum):
    @classmethod
    def column_names(cls):
        return [col.value for col in cls]

    @classmethod
    def column_count(cls):
        return len(cls)


# 文字列テーブルカラム定義
class STRING_TABLE_COLUMNS(TableColumns):
    string_id = "string_id"
    string_type = "string_type"
    text_body = "text_body"


# UIテーブルカラム定義
class UI_TABLE_COLUMNS(TableColumns):
    string_id = "string_id"
    total_byte_size = "total_byte_size"
    byte_size = "byte_size"
    data_type = "data_type"


# 翻訳テーブルカラム定義
class TRANSLATE_TABLE_COLUMNS(TableColumns):
    string_id = "string_id"
    string_type = "string_type"
    text_body = "text_body"
    translate_text_body = "translate_text_body"
    latest_status = "latest_status"
    before_status = "before_status"


class TRANSLATE_STATUS(Enum):
    未翻訳 = "未翻訳"
    要確認 = "要確認"
    翻訳済み = "翻訳済み"
    翻訳不要 = "翻訳不要"
    削除 = "削除"


TRANSLATE_SHEET_NAME = "シート1"
META_SHEET_NAME = "シート2"
ORDER_SHEET_NAME = "シート3"
ARCHIVE_SHEET_NAME = "アーカイブ"


# アーカイブテーブルカラム定義
class ARCHIVE_TABLE_COLUMNS(TableColumns):
    string_id = "string_id"
    string_type = "string_type"
    text_body = "text_body"
    translate_text_body = "translate_text_body"
    latest_status = "latest_status"
    before_status = "before_status"
    archive_date = "archive_date"  # アーカイブ日時
