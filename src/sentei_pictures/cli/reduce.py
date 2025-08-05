"""
画像軽量化CLI
JPEGファイルを指定した品質で圧縮して保存します。
"""

import sys
from pathlib import Path

from ..core.file_matcher import FileMatcher
from ..core.image_processor import ImageProcessor
from .input_handler import InputHandler


def print_usage():
    """使用方法を表示"""
    print("使用方法:")
    print("  1. 対話型: sentei-reduce")
    print("  2. コマンドライン: sentei-reduce <画像があるパス> <軽量化した画像を保存するパス>")
    print("")
    print("例:")
    print("  sentei-reduce")
    print("  sentei-reduce /path/to/original /path/to/reduced")


def main():
    """reduce機能のメインエントリーポイント"""
    # コマンドライン引数がある場合は従来通り
    if len(sys.argv) == 3:
        input_dir = Path(sys.argv[1])
        output_dir = Path(sys.argv[2])

        # 入力ディレクトリの存在チェック
        if not input_dir.exists() or not input_dir.is_dir():
            print(f"エラー: 入力ディレクトリが存在しません: {input_dir}")
            sys.exit(1)

        # 出力ディレクトリの作成
        output_dir.mkdir(parents=True, exist_ok=True)
    elif len(sys.argv) == 1:
        # 引数がない場合は対話型
        input_dir, output_dir = InputHandler.get_reduce_input()
    else:
        print("エラー: 引数の数が正しくありません。")
        print_usage()
        sys.exit(1)

    # JPEGファイルを検索
    jpeg_files = FileMatcher.get_jpeg_files(input_dir)

    if not jpeg_files:
        print(f"JPEGファイルが見つかりませんでした: {input_dir}")
        sys.exit(0)

    print(f"{len(jpeg_files)}個のJPEGファイルを処理します...")

    # 画像プロセッサーを初期化
    processor = ImageProcessor()
    success_count = 0

    for i, input_file in enumerate(jpeg_files, 1):
        output_file = output_dir / input_file.name
        print(f"[{i}/{len(jpeg_files)}] {input_file.name} を処理中...")

        if processor.process_image(input_file, output_file):
            success_count += 1

    print(f"完了: {success_count}/{len(jpeg_files)}個のファイルを軽量化しました。")


if __name__ == "__main__":
    main()
