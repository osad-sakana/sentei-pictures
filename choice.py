"""
選定画像コピースクリプト
選定したファイルと同じ名前の元画像をコピーします。
"""

import shutil
import sys
from pathlib import Path


def print_usage():
    """使用方法を表示"""
    print("使用方法:")
    print("  1. 対話型: poetry run python choice.py")
    print(
        "  2. コマンドライン: poetry run python choice.py "
        "<本体の画像があるパス> <選定後のファイルを保存するパス> <選定したファイルがあるパス>"
    )
    print("")
    print("例:")
    print("  poetry run python choice.py")
    print(
        "  poetry run python choice.py /path/to/original /path/to/selected "
        "/path/to/reduced"
    )


def is_image_file(filename):
    """画像ファイルかどうかを判定"""
    image_extensions = {
        ".jpg",
        ".jpeg",
        ".JPG",
        ".JPEG",
        ".png",
        ".PNG",
        ".gif",
        ".GIF",
        ".bmp",
        ".BMP",
    }
    return Path(filename).suffix.lower() in {ext.lower() for ext in image_extensions}


def find_matching_file(filename, search_dir):
    """ファイル名に一致するファイルを検索（大文字小文字・拡張子を考慮）"""
    base_name = Path(filename).stem

    # まず完全一致を試す
    if (search_dir / filename).exists():
        return search_dir / filename

    # 拡張子違いや大文字小文字違いを検索
    for file_path in search_dir.iterdir():
        if (
            file_path.is_file()
            and file_path.stem == base_name
            and is_image_file(file_path.name)
        ):
            return file_path

    # 大文字小文字を無視して検索
    for file_path in search_dir.iterdir():
        if (
            file_path.is_file()
            and file_path.stem.lower() == base_name.lower()
            and is_image_file(file_path.name)
        ):
            return file_path

    return None


def get_user_input():
    """ユーザーから入力を取得"""
    print("=== 選定画像コピースクリプト ===")
    print()

    while True:
        original_path = input("本体の画像があるパスを入力: ").strip()
        if not original_path:
            print("パスを入力してください。")
            continue

        original_dir = Path(original_path)
        if not original_dir.exists():
            print(f"エラー: 指定されたパスが存在しません: {original_path}")
            continue
        if not original_dir.is_dir():
            print(f"エラー: 指定されたパスはディレクトリではありません: {original_path}")
            continue
        break

    while True:
        output_path = input("選定後のファイルを保存するパスを入力: ").strip()
        if not output_path:
            print("パスを入力してください。")
            continue

        output_dir = Path(output_path)
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
            break
        except Exception as e:
            print(f"エラー: 出力ディレクトリを作成できません: {e}")
            continue

    while True:
        selected_path = input("選定したファイルがあるパスを入力: ").strip()
        if not selected_path:
            print("パスを入力してください。")
            continue

        selected_dir = Path(selected_path)
        if not selected_dir.exists():
            print(f"エラー: 指定されたパスが存在しません: {selected_path}")
            continue
        if not selected_dir.is_dir():
            print(f"エラー: 指定されたパスはディレクトリではありません: {selected_path}")
            continue
        break

    return original_dir, output_dir, selected_dir


def main():
    # コマンドライン引数がある場合は従来通り
    if len(sys.argv) == 4:
        original_dir = Path(sys.argv[1])
        output_dir = Path(sys.argv[2])
        selected_dir = Path(sys.argv[3])

        # ディレクトリの存在チェック
        if not original_dir.exists() or not original_dir.is_dir():
            print(f"エラー: 本体の画像ディレクトリが存在しません: {original_dir}")
            sys.exit(1)

        if not selected_dir.exists() or not selected_dir.is_dir():
            print(f"エラー: 選定したファイルのディレクトリが存在しません: {selected_dir}")
            sys.exit(1)

        # 出力ディレクトリの作成
        output_dir.mkdir(parents=True, exist_ok=True)
    elif len(sys.argv) == 1:
        # 引数がない場合は対話型
        original_dir, output_dir, selected_dir = get_user_input()
    else:
        print("エラー: 引数の数が正しくありません。")
        print_usage()
        sys.exit(1)

    # 選定されたファイルを取得
    selected_files = []
    for file_path in selected_dir.iterdir():
        if file_path.is_file() and is_image_file(file_path.name):
            selected_files.append(file_path.name)

    if not selected_files:
        print(f"選定されたファイルが見つかりませんでした: {selected_dir}")
        sys.exit(0)

    print(f"{len(selected_files)}個の選定されたファイルを処理します...")

    success_count = 0
    not_found_files = []

    for i, selected_filename in enumerate(selected_files, 1):
        print(f"[{i}/{len(selected_files)}] {selected_filename} に対応する元画像を検索中...")

        # 対応する元画像を検索
        original_file = find_matching_file(selected_filename, original_dir)

        if original_file:
            output_file = output_dir / original_file.name
            try:
                shutil.copy2(original_file, output_file)
                print(f"  → {original_file.name} をコピーしました")
                success_count += 1
            except Exception as e:
                print(f"  → エラー: {original_file} のコピーに失敗しました: {e}")
        else:
            print("  → 対応する元画像が見つかりませんでした")
            not_found_files.append(selected_filename)

    print(f"\n完了: {success_count}/{len(selected_files)}個のファイルをコピーしました。")

    if not_found_files:
        print(f"\n見つからなかったファイル ({len(not_found_files)}個):")
        for filename in not_found_files:
            print(f"  - {filename}")


if __name__ == "__main__":
    main()
