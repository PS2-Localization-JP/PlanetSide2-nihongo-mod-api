import pandas as pd
import src.const.const as const  # 定数読み込み
from src.utils.file_util import split_line
from src.utils.remaining_util import ProgressTracker


class DatMaster:
    def __init__(self, data_string):
        self.__data_string = data_string
        self.__master_data = self.__custom_dat_parser(data_string)
        self.__create_index()

    def __custom_dat_parser(self, data_string):
        if not data_string:
            return pd.DataFrame(columns=const.STRING_TABLE_COLUMNS.column_names())

        data = []
        names = const.STRING_TABLE_COLUMNS.column_names()
        tracker = ProgressTracker(
            len(data_string.splitlines()), description="Parsing dat"
        )

        new_line = "\r\n"

        for i, line in enumerate(data_string.splitlines()):
            row = split_line(line, len(names))

            # カラム数がnames以上の場合
            if len(row) > len(names):
                print(
                    f"エラー: 不正な形式の行: {line} (期待されるカラム数: {len(names)}, 実際のカラム数: {len(row)})"
                )
                continue

            # カラム数が0の場合は空文字が渡ってきた為、直前の行のtext_bodyに改行コードを追加
            if len(row) == 0 and data:
                data[-1][names[2]] += new_line
                continue

            # カラム数が1の場合は、前回のtext_bodyの続きである。
            # 直前の行のtext_bodyに改行コードを追加
            if len(row) == 1 and data:
                data[-1][names[2]] += row[0] + new_line
                continue

            # カラム数が2の場合、text_bodyに改行コードを追加
            if len(row) == 2:
                # row.extend([new_line] * (len(names) - len(row)))
                row.extend([""] * (len(names) - len(row)))

            # カラム数が3の場合、改行コードを追加
            elif len(row) == 3:
                # row[2] = row[2] + new_line if row[2] and row[2] is not None else new_line
                pass

            row_dict = dict(zip(names, row))

            # ここまでやって、text_bodyが空文字やNoneの場合は、改行コードを追加
            if row_dict.get(names[2]) is None or row_dict[names[2]] == "":
                row_dict[names[2]] = ""

            if len(row_dict) > len(names):
                print(f"エラー: 不正な形式の行: カラム数が{len(names)}以上です")
                continue

            # キーが一緒な場合
            if (
                data
                and data[-1][names[0]] == row_dict[names[0]]
                and data[-1][names[1]] == row_dict[names[1]]
            ):
                data[-1][names[2]] += row_dict[names[2]]

            # キーが違う場合
            else:
                # 代入処理
                data.append(row_dict)
            tracker.update()
        tracker.finish()

        df = pd.DataFrame(data)
        for col in names:
            if col in df.columns:
                df[col] = df[col].astype(str)
        return df

    def __create_index(self):
        if not self.__master_data.empty:
            self.__master_data.index = (
                self.__master_data[
                    [
                        const.STRING_TABLE_COLUMNS.string_id.value,
                        const.STRING_TABLE_COLUMNS.string_type.value,
                    ]
                ]
                .astype(str)
                .agg("-".join, axis=1)
            )

    def get_record(self, string_id, string_type):
        key = f"{string_id}-{string_type}"
        if key not in self.__master_data.index:
            raise ValueError(f"キーが見つかりません: {key}")
        return self.__master_data.loc[key]

    def add_record(self, string_id, string_type, text_body):
        names = const.STRING_TABLE_COLUMNS.column_names()
        key = f"{string_id}-{string_type}"
        if key in self.__master_data.index:
            raise ValueError(f"キーが重複しています: {key}")
        new_record = pd.DataFrame(
            [{names[0]: string_id, names[1]: string_type, names[2]: text_body}]
        )
        for col in new_record.columns:
            new_record[col] = new_record[col].astype(str)
        self.__master_data = pd.concat(
            [self.__master_data, new_record], ignore_index=True
        )
        self.__create_index()

    def add_records(self, records):
        names = const.STRING_TABLE_COLUMNS.column_names()
        new_records = pd.DataFrame(records, columns=names)
        for col in new_records.columns:
            new_records[col] = new_records[col].astype(str)
        self.__master_data = pd.concat(
            [self.__master_data, new_records], ignore_index=True
        )
        self.__create_index()

    def update_record(self, string_id, string_type, new_text_body):
        names = const.STRING_TABLE_COLUMNS.column_names()
        key = f"{string_id}-{string_type}"
        if key not in self.__master_data.index:
            raise ValueError(f"キーが見つかりません: {key}")
        self.__master_data.loc[key, names[2]] = new_text_body

    def dump_master_data(self, file_path):
        df = self.__master_data.reset_index()[const.STRING_TABLE_COLUMNS.column_names()]
        tracker = ProgressTracker(len(df), description="Dumping data")
        # to_csvは使用禁止
        with open(file_path, "wb") as f:
            for i, (_, row) in enumerate(df.iterrows()):
                line = "\t".join(str(x) for x in row)
                log_line = line.encode("utf-8") + ("\r\n").encode("utf-8")
                f.write(log_line)
                tracker.update()
        tracker.finish()

    def get_master_data(self):
        return self.__master_data
