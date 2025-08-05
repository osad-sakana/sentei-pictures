"""
選定画像コピーCLI
選定したファイルと同じ名前の元画像をコピーします。
"""

import shutil
import sys
from pathlib import Path

from ..core.file_matcher import FileMatcher
from .input_handler import InputHandler


def print_usage():
    """使用方法を表示"""
    print("使用方法:")
    print("  1. 対話型: sentei-choice")
    print(
        "  2. コマンドライン: sentei-choice <本体の画像があるパス> " "<選定後のファイルを保存するパス> <選定したファイルがあるパス>"
    )
    print("")
    print("例:")
    print("  sentei-choice")
    print("  sentei-choice /path/to/original /path/to/selected /path/to/reduced")


def main():
    """choice機能のメインエントリーポイント"""
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
        original_dir, output_dir, selected_dir = InputHandler.get_choice_input()
    else:
        print("エラー: 引数の数が正しくありません。")
        print_usage()
        sys.exit(1)

    # 選定されたファイルを取得
    selected_files = FileMatcher.get_image_files(selected_dir)

    if not selected_files:
        print(f"選定されたファイルが見つかりませんでした: {selected_dir}")
        sys.exit(0)

    print(f"{len(selected_files)}個の選定されたファイルを処理します...")

    success_count = 0
    not_found_files = []

    for i, selected_file in enumerate(selected_files, 1):
        print(f"[{i}/{len(selected_files)}] {selected_file.name} に対応する元画像を検索中...")

        # 対応する元画像を検索
        original_file = FileMatcher.find_matching_file(selected_file.name, original_dir)

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
            not_found_files.append(selected_file.name)

    print(f"\n完了: {success_count}/{len(selected_files)}個のファイルをコピーしました。")

    if not_found_files:
        print(f"\n見つからなかったファイル ({len(not_found_files)}個):")
        for filename in not_found_files:
            print(f"  - {filename}")


if __name__ == "__main__":
    main()
