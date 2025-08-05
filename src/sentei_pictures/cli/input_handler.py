"""
ユーザー入力処理機能
対話型入力の処理を行う
"""

from pathlib import Path
from typing import Tuple


class InputHandler:
    """ユーザー入力を処理するクラス"""

    @staticmethod
    def get_directory_input(prompt: str, create_if_missing: bool = False) -> Path:
        """
        ディレクトリパスを入力取得

        Args:
            prompt: 入力プロンプト
            create_if_missing: 存在しない場合に作成するか

        Returns:
            Path: 検証済みディレクトリパス
        """
        while True:
            path_str = input(f"{prompt}: ").strip()
            if not path_str:
                print("パスを入力してください。")
                continue

            path = Path(path_str)

            if create_if_missing:
                try:
                    path.mkdir(parents=True, exist_ok=True)
                    return path
                except Exception as e:
                    print(f"エラー: ディレクトリを作成できません: {e}")
                    continue
            else:
                if not path.exists():
                    print(f"エラー: 指定されたパスが存在しません: {path_str}")
                    continue
                if not path.is_dir():
                    print(f"エラー: 指定されたパスはディレクトリではありません: {path_str}")
                    continue
                return path

    @staticmethod
    def get_reduce_input() -> Tuple[Path, Path]:
        """reduce機能用の入力を取得"""
        print("=== 画像軽量化スクリプト ===")
        print()

        input_dir = InputHandler.get_directory_input("ソースファイルのパスを入力")
        output_dir = InputHandler.get_directory_input(
            "出力先のパスを入力", create_if_missing=True
        )

        return input_dir, output_dir

    @staticmethod
    def get_choice_input() -> Tuple[Path, Path, Path]:
        """choice機能用の入力を取得"""
        print("=== 選定画像コピースクリプト ===")
        print()

        original_dir = InputHandler.get_directory_input("本体の画像があるパスを入力")
        output_dir = InputHandler.get_directory_input(
            "選定後のファイルを保存するパスを入力", create_if_missing=True
        )
        selected_dir = InputHandler.get_directory_input("選定したファイルがあるパスを入力")

        return original_dir, output_dir, selected_dir
