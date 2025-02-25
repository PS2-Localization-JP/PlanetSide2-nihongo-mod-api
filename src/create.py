import sys
from dotenv import load_dotenv
import os
import pandas as pd

load_dotenv()

if os.environ.get("CI", "").lower() != "true" and  not os.path.exists(".env"):
    print("Error: .env file not found.")
    sys.exit(1)

sys.path.append(".")  # srcをパスに追加してサブモジュール群をインポートできるようにする

import src.const.const as const  # 定数読み込み
from src.master.dat_master import DatMaster
from src.master.dir_master import DirMaster
from src.master.sheet_master import SheetMaster
from src.utils.remaining_util import ProgressTracker


def main():
    print("create")
    main_tracker = ProgressTracker(7, description="Creating data")

    main_tracker.update()
    credentials_path = os.getenv("GOOGLE_CREDENTIALS_PATH")
    spreadsheet_id = os.getenv("GOOGLE_SPREADSHEET_ID")

    sheet_master = SheetMaster(credentials_path, spreadsheet_id)

    main_tracker.update()
    print("Getting translate sheet data")
    # スプレッドシートから翻訳シートのデータを取得
    translate_sheet_data = sheet_master.get_sheet_data(const.TRANSLATE_SHEET_NAME)
    if not translate_sheet_data:
        print("Error: Failed to get translate_sheet data.")
        sys.exit(1)

    translate_sheet_df = pd.DataFrame(
        translate_sheet_data[1:], columns=translate_sheet_data[0]
    )

    # translate_sheet_dfをstring_idとstring_typeをキーとした辞書に変換
    translate_init_tracker = ProgressTracker(
        len(translate_sheet_df), description="Creating translate dict"
    )
    translate_sheet_origin_dict = {}
    translate_sheet_translate_dict = {}
    for _, row in translate_sheet_df.iterrows():
        key = (
            str(row[const.STRING_TABLE_COLUMNS.string_id.value]).replace(
                const.UTF8BOM_START_BYTE, ""
            ),
            row[const.TRANSLATE_TABLE_COLUMNS.string_type.value],
        )
        translate_sheet_origin_dict[key] = row[
            const.TRANSLATE_TABLE_COLUMNS.text_body.value
        ]
        translate_sheet_translate_dict[key] = row[
            const.TRANSLATE_TABLE_COLUMNS.translate_text_body.value
        ]
        translate_init_tracker.update()

    translate_init_tracker.finish()

    main_tracker.update()
    print("Getting meta sheet data")
    # スプレッドシートからdirのメタ情報を取得
    meta_sheet_data = sheet_master.get_sheet_data(const.META_SHEET_NAME)
    if not meta_sheet_data:
        print("Error: Failed to get meta sheet data.")
        sys.exit(1)

    main_tracker.update()
    print("Getting order sheet data")
    # スプレッドシートからオーダーシートのデータを取得
    order_sheet_data = sheet_master.get_sheet_data(const.ORDER_SHEET_NAME)
    if not order_sheet_data:
        print("Error: Failed to get order sheet data.")
        sys.exit(1)
    order_sheet_df = pd.DataFrame(order_sheet_data[1:], columns=order_sheet_data[0])

    main_tracker.update()
    print("Creating dat dir file")
    dat_master = DatMaster("")
    dir_master = DirMaster("")
    dir_master.update_meta(meta_sheet_data[0][0])
    data_type = "d"

    # オーダーシートの順列を元にレコードを順次追加する
    dat_dir_init_tracker = ProgressTracker(
        len(order_sheet_df), description="Creating dat dir"
    )
    dat_records = []
    dir_records = []
    for _, row in order_sheet_df.iterrows():
        string_id = str(row[const.STRING_TABLE_COLUMNS.string_id.value]).replace(
            const.UTF8BOM_START_BYTE, ""
        )

        string_type = row[const.STRING_TABLE_COLUMNS.string_type.value]
        # translate_sheet_origin_dictからtext_bodyを取得
        text_body = translate_sheet_origin_dict.get((string_id, string_type))
        if text_body is None:
            print(
                f"Warning: text_body not found for string_id={string_id}, string_type={string_type}"
            )
            text_body = ""  # 空文字で処理を続行
        dat_records.append(
            {
                const.STRING_TABLE_COLUMNS.string_id.value: string_id,
                const.STRING_TABLE_COLUMNS.string_type.value: string_type,
                const.STRING_TABLE_COLUMNS.text_body.value: text_body,
            }
        )
        dir_records.append(
            {
                const.UI_TABLE_COLUMNS.string_id.value: string_id,
                const.UI_TABLE_COLUMNS.data_type.value: data_type,
            }
        )
        dat_dir_init_tracker.update()
    dat_dir_init_tracker.finish()

    dat_master.add_records(dat_records)
    dir_master.add_records(dir_records)

    main_tracker.update()
    print("Updating byte sizes")
    # 翻訳シートからlatest_statusが「翻訳済み」のstring_idとstring_typeのリストを取得
    translated_rows = translate_sheet_df[
        translate_sheet_df[const.TRANSLATE_TABLE_COLUMNS.latest_status.value]
        == const.TRANSLATE_STATUS.翻訳済み.value
    ]
    translated_ids = translated_rows[
        [
            const.TRANSLATE_TABLE_COLUMNS.string_id.value,
            const.TRANSLATE_TABLE_COLUMNS.string_type.value,
        ]
    ].to_dict(orient="records")

    # dat_masterのデータをstring_idとstring_typeをキーとした辞書に変換
    dat_master_data = dat_master.get_master_data()
    dat_master_dict = {}  # ここで初期化
    dat_dict_init_tracker = ProgressTracker(
        len(dat_master_data), description="Creating dat dict"
    )
    for index, row in dat_master_data.iterrows():  # loopはiterrows()でOK
        key = (
            str(row[const.STRING_TABLE_COLUMNS.string_id.value]).replace(
                const.UTF8BOM_START_BYTE, ""
            ),
            row[const.STRING_TABLE_COLUMNS.string_type.value],
        )
        dat_master_dict[key] = index  # indexだけ保持
        dat_dict_init_tracker.update()
    dat_dict_init_tracker.finish()

    # translated_idsの各行について、dat_masterのtext_bodyをtranslate_sheetのtranslate_text_bodyで置き換える
    translate_tracker = ProgressTracker(
        len(translated_ids), description="Replace translate text"
    )
    for row in translated_ids:  # translated_idsをloop
        key = (row["string_id"], row["string_type"])
        index = dat_master_dict.get(key)  # get()で高速lookup
        if index is not None:  # keyが存在する場合のみ処理
            # translate_sheet_translate_dictからtranslate_text_bodyを取得
            translate_text_body = translate_sheet_translate_dict.get(
                key
            )  # get()で高速lookup
            if translate_text_body is not None:  # text_bodyが存在する場合のみ処理
                # dat_masterのtext_bodyを更新
                dat_master.get_master_data().loc[
                    index, const.STRING_TABLE_COLUMNS.text_body.value
                ] = translate_text_body
            else:
                print(f"Warning: translate_text_body not found for key={key}")
        else:
            print(f"Warning: key={key} not found in dat_master_dict")
        translate_tracker.update()
    translate_tracker.finish()

    dir_master.update_byte_sizes(dat_master)

    main_tracker.update()
    print("Dumping master data")
    # ja_jp_data.datとja_jp_data.dirをダンプして処理を終了
    # TODO github action時に、リリースされるように適時以下を修正
    jp_dat_path = "data/output/translation_file/ja_jp_data.dat"
    jp_dir_path = "data/output/translation_file/ja_jp_data.dir"

    # ディレクトリが存在しない場合は作成する
    os.makedirs(os.path.dirname(jp_dat_path), exist_ok=True)
    os.makedirs(os.path.dirname(jp_dir_path), exist_ok=True)

    dat_master.dump_master_data(jp_dat_path)
    dir_master.dump_master_data(jp_dir_path)

    main_tracker.finish()


if __name__ == "__main__":
    main()
