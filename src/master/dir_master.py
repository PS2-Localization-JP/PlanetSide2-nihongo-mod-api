import pandas as pd
import src.const.const as const  # 定数読み込み
from src.utils.file_util import split_line
from src.utils.remaining_util import ProgressTracker


class DirMaster:
    def __init__(self, data_string):
        if not data_string:
            self.__meta_data = ""
            self.__master_data = pd.DataFrame(
                columns=const.UI_TABLE_COLUMNS.column_names()
            )
        else:
            self.__meta_data = self.__parse_meta_data(data_string)
            self.__master_data = self.__custom_dir_parser(data_string)

    def __parse_meta_data(self, data_string):
        meta_lines = []
        for line in data_string.splitlines():
            if line.startswith("##"):
                meta_lines.append(line)
        return "\n".join(meta_lines)

    def __custom_dir_parser(self, data_string):
        if not data_string:
            return pd.DataFrame(columns=const.UI_TABLE_COLUMNS.column_names())

        data = []
        names = const.UI_TABLE_COLUMNS.column_names()
        tracker = ProgressTracker(
            len(data_string.splitlines()), description="Parsing dir"
        )
        for line in data_string.splitlines():
            if line.startswith("##"):
                continue
            row = split_line(line, len(names))
            if len(row) != len(names):
                if len(row) != len(names) and row[0] != "":
                    print(
                        f"エラー: 不正な形式の行: {line} (期待されるカラム数: {len(names)}, 実際のカラム数: {len(row)})"
                    )
                    continue
            if row[0] != "":
                row_dict = dict(zip(names, row))
                data.append(row_dict)
            tracker.update()
        tracker.finish()
        df = pd.DataFrame(data)
        print(df)
        return df

    def add_record(self, string_id, data_type):
        names = const.UI_TABLE_COLUMNS.column_names()
        new_record = pd.DataFrame(
            [
                {names[0]: string_id, names[3]: data_type}
            ],  # byte_size, total_byte_size は後でupdate
            columns=names,  # カラム順序を保証
        )
        for col in new_record.columns:
            new_record[col] = new_record[col].astype(str)
        self.__master_data = pd.concat(
            [self.__master_data, new_record], ignore_index=True
        )

    def add_records(self, records):
        names = const.UI_TABLE_COLUMNS.column_names()
        new_records = pd.DataFrame(records, columns=names)
        for col in new_records.columns:
            new_records[col] = new_records[col].astype(str)
        self.__master_data = pd.concat(
            [self.__master_data, new_records], ignore_index=True
        )

    def update_meta(self, meta_string):
        self.__meta_data = meta_string

    def update_byte_sizes(self, dat_master):
        tracker = ProgressTracker(
            len(self.__master_data), description="Updating byte sizes"
        )

        start_byte = 3  # 3 は utf-8 BOM の \ufeff に相当するバイト数

        dat_master_data = dat_master.get_master_data()
        for dir_index, dir_row in self.__master_data.iterrows():
            if dir_index < len(dat_master_data):
                dat_row = dat_master_data.iloc[dir_index]
                text = "\t".join(
                    [
                        str(
                            dat_row[const.STRING_TABLE_COLUMNS.string_id.value]
                        ).replace(const.UTF8BOM_START_BYTE, "")
                    ]
                    + [
                        str(dat_row[name])
                        for name in const.STRING_TABLE_COLUMNS.column_names()[1:]
                    ]
                )
                # if text.endswith("\r\n"):
                #     text = text[:-2]
                byte_size = len(text.encode("utf-8"))

                self.__master_data.loc[
                    dir_index, const.UI_TABLE_COLUMNS.total_byte_size.value
                ] = start_byte
                self.__master_data.loc[
                    dir_index, const.UI_TABLE_COLUMNS.byte_size.value
                ] = byte_size

                start_byte += byte_size + 2  # + 2は改行コードのバイト数

            tracker.update()
        tracker.finish()

    def dump_master_data(self, file_path):
        df = self.__master_data.reset_index()[const.UI_TABLE_COLUMNS.column_names()]
        tracker = ProgressTracker(len(df), description="Dumping data")

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(self.__meta_data + "\n")
            for _, row in df.iterrows():
                f.write("\t".join(str(x) for x in row) + "\n")
                tracker.update()
        tracker.finish()

    def get_master_data(self):
        return self.__master_data

    def get_meta_data(self):
        return self.__meta_data
