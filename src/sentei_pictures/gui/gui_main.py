"""
GUI版メインエントリーポイント
tkinterベースのグラフィカルユーザーインターフェースを起動する
"""

import sys

from .main_window import MainWindow


def main():
    """GUI版のメインエントリーポイント"""
    try:
        app = MainWindow()
        app.run()
    except KeyboardInterrupt:
        print("\nGUIアプリケーションを終了します。")
        sys.exit(0)
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
