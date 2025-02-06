import sys
from dotenv import load_dotenv
import os
import pandas as pd

load_dotenv()

if not os.path.exists(".env"):
    print("Error: .env file not found.")
    sys.exit(1)

sys.path.append(".")  # srcをパスに追加してサブモジュール群をインポートできるようにする

import src.const.const as const  # 定数読み込み
from src.master.dat_master import DatMaster
from src.master.dir_master import DirMaster
from src.utils.file_util import read_file_to_string, is_definitely_formula
from src.master.sheet_master import SheetMaster
from src.utils.remaining_util import ProgressTracker


def main():
    latest_dat_path = os.getenv("LATEST_DAT_PATH")
    if not latest_dat_path:
        print("Error: LATEST_DAT_PATH not found in .env file.")
        sys.exit(1)

    latest_dir_path = os.getenv("LATEST_DIR_PATH")
    if not latest_dir_path:
        print("Error: LATEST_DIR_PATH not found in .env file.")
        sys.exit(1)

    print("update")
    latest_dat_path = os.getenv("LATEST_DAT_PATH")
    latest_dir_path = os.getenv("LATEST_DIR_PATH")

    tracker = ProgressTracker(10, description="Updating data")

    tracker.update()
    print("Reading dat file")
    dat_string = read_file_to_string(latest_dat_path)
    dat_master = DatMaster(dat_string)

    tracker.update()
    print("Reading dir file")
    dir_string = read_file_to_string(latest_dir_path)
    dir_master = DirMaster(dir_string)

    credentials_path = os.getenv("GOOGLE_CREDENTIALS_PATH")
    spreadsheet_id = os.getenv("GOOGLE_SPREADSHEET_ID")
    admin_email = os.getenv("ADMIN_EMAIL")
    sheet_master = SheetMaster(credentials_path, spreadsheet_id, admin_email)

    tracker.update()
    print("Getting meta sheet data")
    # スプレッドシートからdirのメタ情報を取得
    meta_sheet_data = sheet_master.get_sheet_data(const.META_SHEET_NAME)
    if not meta_sheet_data:
        print("Error: Failed to get meta sheet data.")
        sys.exit(1)

    # 最新dirのメタ情報を取得
    latest_dir_meta = dir_master.get_meta_data()

    # メタ情報を比較
    if meta_sheet_data[0][0] == latest_dir_meta:
        print("メタ情報に差はありません。処理を終了します")
        sys.exit(0)

    print("メタ情報に差があります。更新処理を開始します")

    tracker.update()
    print("Getting translate sheet data")
    # スプレッドシートから翻訳シートのデータを取得（古い状態として）
    translate_sheet_data = sheet_master.get_sheet_data(const.TRANSLATE_SHEET_NAME)
    if not translate_sheet_data:
        print("Error: Failed to get translate_sheet data.")
        sys.exit(1)

    old_translate_sheet_df = pd.DataFrame(
        translate_sheet_data[1:], columns=translate_sheet_data[0]
    )
    old_translate_sheet_df = old_translate_sheet_df.fillna("")
    old_translate_sheet_df[const.TRANSLATE_TABLE_COLUMNS.string_id.value] = (
        old_translate_sheet_df[
            const.TRANSLATE_TABLE_COLUMNS.string_id.value
        ].str.replace(const.UTF8BOM_START_BYTE, "")
    )

    # 最新datを元に翻訳シートと同じ形式の空のインスタンスを作成
    latest_translate_sheet_df = pd.DataFrame(columns=translate_sheet_data[0])

    # dat_masterからデータを取得してデータフレームに追加
    master_data = dat_master.get_master_data()
    for index, row in master_data.iterrows():
        string_id = str(row[const.STRING_TABLE_COLUMNS.string_id.value]).replace(
            const.UTF8BOM_START_BYTE, ""
        )
        string_type = row[const.STRING_TABLE_COLUMNS.string_type.value]
        text_body = row[const.STRING_TABLE_COLUMNS.text_body.value]
        new_row = pd.DataFrame(
            [
                {
                    const.TRANSLATE_TABLE_COLUMNS.string_id.value: string_id,
                    const.TRANSLATE_TABLE_COLUMNS.string_type.value: string_type,
                    const.TRANSLATE_TABLE_COLUMNS.text_body.value: text_body,
                    const.TRANSLATE_TABLE_COLUMNS.translate_text_body.value: "",  # 初期値
                    const.TRANSLATE_TABLE_COLUMNS.latest_status.value: const.TRANSLATE_STATUS.未翻訳.value,  # 初期値
                    const.TRANSLATE_TABLE_COLUMNS.before_status.value: const.TRANSLATE_STATUS.未翻訳.value,  # 初期値
                }
            ]
        )
        latest_translate_sheet_df = pd.concat(
            [latest_translate_sheet_df, new_row], ignore_index=True
        )

    tracker.update()
    print("Comparing dataframes")
    # pandasで差分を出力
    # 前提：string_idとstring_typeの二つがそろってキーとなる
    # 前提：キーがそろってる場合に比べるのはtext_bodyのみ
    # 前提：この差分の時点ではlatest_translate_sheet_dfに変更は加えない。それらのキーのリストをそれぞれ作成して返す
    # 比べるのは以下の点
    # ・old_translate_sheet_dfにキーはあるが、latest_translate_sheet_dfに無い場合：削除
    # ・latest_translate_sheet_dfにキーはあるが、old_translate_sheet_dfに無い場合：未翻訳
    # ・old_translate_sheet_dfとlatest_translate_sheet_df双方にキーはあるが、text_bodyの内容が違う場合：要確認
    old_translate_sheet_df_keyed = old_translate_sheet_df.set_index(
        [
            const.TRANSLATE_TABLE_COLUMNS.string_id.value,
            const.TRANSLATE_TABLE_COLUMNS.string_type.value,
        ]
    )
    latest_translate_sheet_df_keyed = latest_translate_sheet_df.set_index(
        [
            const.TRANSLATE_TABLE_COLUMNS.string_id.value,
            const.TRANSLATE_TABLE_COLUMNS.string_type.value,
        ]
    )

    deleted_keys = old_translate_sheet_df_keyed.index.difference(
        latest_translate_sheet_df_keyed.index
    )
    new_keys = latest_translate_sheet_df_keyed.index.difference(
        old_translate_sheet_df_keyed.index
    )
    common_keys = old_translate_sheet_df_keyed.index.intersection(
        latest_translate_sheet_df_keyed.index
    )
    modified_keys = common_keys[
        old_translate_sheet_df_keyed.loc[common_keys][
            const.TRANSLATE_TABLE_COLUMNS.text_body.value
        ]
        != latest_translate_sheet_df_keyed.loc[common_keys][
            const.TRANSLATE_TABLE_COLUMNS.text_body.value
        ]
    ]

    print(f"削除されたキー: {deleted_keys.tolist()}")
    print(f"新規キー: {new_keys.tolist()}")
    print(f"変更されたキー: {modified_keys.tolist()}")

    # 古い翻訳シートのlatest_statusを、キーが同じのlatest_translate_sheet_dfのbefore_statusにコピー
    merged_df = latest_translate_sheet_df.merge(
        old_translate_sheet_df[
            [
                const.TRANSLATE_TABLE_COLUMNS.string_id.value,
                const.TRANSLATE_TABLE_COLUMNS.string_type.value,
                const.TRANSLATE_TABLE_COLUMNS.latest_status.value,
            ]
        ],
        on=[
            const.TRANSLATE_TABLE_COLUMNS.string_id.value,
            const.TRANSLATE_TABLE_COLUMNS.string_type.value,
        ],
        how="left",
    )
    latest_translate_sheet_df[const.TRANSLATE_TABLE_COLUMNS.before_status.value] = (
        merged_df[const.TRANSLATE_TABLE_COLUMNS.latest_status.value + "_y"].fillna(
            const.TRANSLATE_STATUS.未翻訳.value
        )
    )

    tracker.update()
    print("Updating translate sheet dataframe")
    # 差分を元に、新しい翻訳シートのインスタンスのlatest_statusを更新
    latest_translate_sheet_df = latest_translate_sheet_df.set_index(
        [
            const.TRANSLATE_TABLE_COLUMNS.string_id.value,
            const.TRANSLATE_TABLE_COLUMNS.string_type.value,
        ]
    )

    # 削除された場合は「latest_translate_sheet_df」にキーは存在しないので、ここはコメントアウト
    # if deleted_keys:
    #     # 削除されたIDのステータスを更新
    #     latest_translate_sheet_df.loc[deleted_keys, "latest_status"] = const.TRANSLATE_STATUS.削除.value

    # 新規IDのステータスは初期値の「未翻訳」のまま

    # 変更されたデータのステータスを更新
    latest_translate_sheet_df.loc[
        modified_keys, const.TRANSLATE_TABLE_COLUMNS.latest_status.value
    ] = const.TRANSLATE_STATUS.要確認.value

    # 変更がない場合は古いステータスを維持 (before_statusからコピー)
    for key in common_keys.difference(modified_keys):
        latest_translate_sheet_df.loc[
            key, const.TRANSLATE_TABLE_COLUMNS.latest_status.value
        ] = latest_translate_sheet_df.loc[
            key, const.TRANSLATE_TABLE_COLUMNS.before_status.value
        ]

    # translate_text_bodyの内容を格納
    latest_translate_sheet_df.loc[
        common_keys, const.TRANSLATE_TABLE_COLUMNS.translate_text_body.value
    ] = old_translate_sheet_df_keyed.loc[
        common_keys, const.TRANSLATE_TABLE_COLUMNS.translate_text_body.value
    ]

    # text_bodyとtranslate_text_bodyをチェックして、必要に応じてシングルクォートを先頭に追加
    for index, row in latest_translate_sheet_df.iterrows():
        if is_definitely_formula(row[const.TRANSLATE_TABLE_COLUMNS.text_body.value]):
            latest_translate_sheet_df.loc[
                index, const.TRANSLATE_TABLE_COLUMNS.text_body.value
            ] = f"'{row['text_body']}"
        if is_definitely_formula(
            row[const.TRANSLATE_TABLE_COLUMNS.translate_text_body.value]
        ):
            latest_translate_sheet_df.loc[
                index, const.TRANSLATE_TABLE_COLUMNS.translate_text_body.value
            ] = f"'{row['translate_text_body']}"

    latest_translate_sheet_df = latest_translate_sheet_df.reset_index()

    tracker.update()
    print("Clearing sheets")
    # gs翻訳シートとgsメタシートをクリア
    sheet_master.clear_sheet(const.TRANSLATE_SHEET_NAME)
    sheet_master.clear_sheet(const.META_SHEET_NAME)
    sheet_master.clear_sheet(const.ORDER_SHEET_NAME)

    tracker.update()
    print("Updating translate sheet")
    # 新しい翻訳シートのインスタンスを元に翻訳シートを更新
    sheet_master.update_sheet(
        const.TRANSLATE_SHEET_NAME,
        [latest_translate_sheet_df.columns.tolist()]
        + latest_translate_sheet_df.values.tolist(),
    )

    tracker.update()
    print("Updating meta sheet")
    # メタシートに最新dirのメタ情報を書き込む
    sheet_master.update_sheet(const.META_SHEET_NAME, [[latest_dir_meta]])

    tracker.update()
    print("Updating order sheet")
    # オーダーシートの更新処理：最新のdatの並び順をシートに保管しておく

    # dat_masterからstring_idとstring_typeのデータを取得
    # 必要な列のみを抽出してデータフレームを作成
    order_sheet_data = master_data[
        [
            const.STRING_TABLE_COLUMNS.string_id.value,
            const.STRING_TABLE_COLUMNS.string_type.value,
        ]
    ].copy()

    # オーダーシートを更新
    sheet_master.update_sheet(
        const.ORDER_SHEET_NAME,
        [order_sheet_data.columns.tolist()] + order_sheet_data.values.tolist(),
    )
    tracker.finish()


if __name__ == "__main__":
    main()
