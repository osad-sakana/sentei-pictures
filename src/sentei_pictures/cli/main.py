"""
写真処理ユーティリティ統合メニュー
reduce.pyとchoice.pyを統合的に実行できます。
"""

import sys

from .choice import main as choice_main
from .input_handler import InputHandler
from .reduce import main as reduce_main


def print_main_menu():
    """メインメニューを表示"""
    print("=== 写真処理ユーティリティ ===")
    print()
    print("実行したいコマンドを選択してください:")
    print("  1. reduce  - 画像軽量化（リサイズ・品質調整）")
    print("  2. choice  - 選定画像のコピー")
    print("  3. exit    - 終了")
    print()


def main():
    """メインエントリーポイント"""
    while True:
        print_main_menu()

        try:
            command = input("コマンドを入力 (1/2/3 または reduce/choice/exit): ").strip().lower()
        except KeyboardInterrupt:
            print("\n終了します。")
            sys.exit(0)

        if command in ["1", "reduce"]:
            print()
            try:
                # reduce機能の対話型機能を呼び出し
                input_dir, output_dir = InputHandler.get_reduce_input()

                # reduce機能のメイン処理部分を実行
                # sys.argvを一時的に設定してreduce_main()を呼び出し
                original_argv = sys.argv
                sys.argv = ["sentei-reduce", str(input_dir), str(output_dir)]
                try:
                    reduce_main()
                finally:
                    sys.argv = original_argv

            except KeyboardInterrupt:
                print("\n処理を中止しました。")
            except Exception as e:
                print(f"エラーが発生しました: {e}")

            print()
            input("Enterキーを押して続行...")
            print()

        elif command in ["2", "choice"]:
            print()
            try:
                # choice機能の対話型機能を呼び出し
                original_dir, output_dir, selected_dir = InputHandler.get_choice_input()

                # choice機能のメイン処理部分を実行
                original_argv = sys.argv
                sys.argv = [
                    "sentei-choice",
                    str(original_dir),
                    str(output_dir),
                    str(selected_dir),
                ]
                try:
                    choice_main()
                finally:
                    sys.argv = original_argv

            except KeyboardInterrupt:
                print("\n処理を中止しました。")
            except Exception as e:
                print(f"エラーが発生しました: {e}")

            print()
            input("Enterキーを押して続行...")
            print()

        elif command in ["3", "exit", "quit"]:
            print("終了します。")
            sys.exit(0)

        else:
            print("無効な選択です。1, 2, 3 または reduce, choice, exit を入力してください。")
            print()


if __name__ == "__main__":
    main()
