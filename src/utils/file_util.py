import chardet
import re


def detect_encoding(file_path):
    """
    ファイルのエンコーディングを自動検出し、検出されたエンコーディングを返す。
    Args:
        file_path (str): ファイルのパス。
    Returns:
        str: 検出されたエンコーディング。検出に失敗した場合はNone。
    """
    encodings = ["utf-8", "utf-8-sig", "latin-1"]
    for encoding in encodings:
        try:
            with open(file_path, "rb") as f:
                raw_data = f.read()
                result = chardet.detect(raw_data)
                if result["encoding"]:
                    return result["encoding"]
        except UnicodeDecodeError:
            continue
    return None


def read_file_to_string(file_path, encoding="utf-8"):
    with open(file_path, "r", encoding="utf-8") as f:  # エンコードを強制的にutf-8に
        return f.read()


def split_line(line, num_cols, sep="\t"):
    parts = line.split(sep)
    if len(parts) <= num_cols:
        return parts
    return parts[: num_cols - 1] + [sep.join(parts[num_cols - 1 :])]


def is_definitely_formula(text):
    """文字列が数式として解釈される可能性が高いか判定する。

    Args:
        text: 判定する文字列。

    Returns:
        bool: 数式として解釈される可能性が高い場合はTrue、そうでない場合はFalse。
    """
    if not isinstance(text, str):
        return False

    # スプレッドシートの数式で使われる可能性のあるパターンを検出
    patterns = [
        r"^[=+]?.+%",  #  `=` または `+` で始まり、少なくとも1つの文字があり、`%` を含む
        r"#count\(\[.+\]\)",  # `#count([` と `])` で囲まれたパターン
        r"^[=+][A-Za-z0-9\s:]+",  # `=` または `+` で始まり、英数字、空白、コロンを含む (例: `=Loyalty:`)
        r"^'.+'",  # シングルクォートで囲まれた文字列
    ]

    for pattern in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True

    return False
