"""
メインウィンドウ
アプリケーションの起動画面
"""

import tkinter as tk
from tkinter import ttk

from .choice_window import ChoiceWindow
from .reduce_window import ReduceWindow


class MainWindow:
    """メインウィンドウクラス"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("写真処理ユーティリティ")
        self.root.geometry("400x300")
        self.root.resizable(False, False)

        # ウィンドウを画面中央に配置
        self._center_window()

        self._setup_widgets()

    def _center_window(self):
        """ウィンドウを画面中央に配置"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def _setup_widgets(self):
        """ウィジェットを設定"""
        # メインフレーム
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # タイトル
        title_label = ttk.Label(main_frame, text="写真処理ユーティリティ", font=("", 16, "bold"))
        title_label.pack(pady=(0, 20))

        # 説明
        desc_label = ttk.Label(main_frame, text="実行したい機能を選択してください", font=("", 10))
        desc_label.pack(pady=(0, 30))

        # ボタンフレーム
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(expand=True)

        # 画像軽量化ボタン
        reduce_button = ttk.Button(
            button_frame, text="画像軽量化", command=self._open_reduce_window, width=20
        )
        reduce_button.pack(pady=10)

        # 選定画像コピーボタン
        choice_button = ttk.Button(
            button_frame, text="選定画像コピー", command=self._open_choice_window, width=20
        )
        choice_button.pack(pady=10)

        # 終了ボタン
        exit_button = ttk.Button(
            button_frame, text="終了", command=self._exit_app, width=20
        )
        exit_button.pack(pady=(20, 10))

        # ボタンの説明
        help_frame = ttk.Frame(main_frame)
        help_frame.pack(fill=tk.X, pady=(20, 0))

        help_text = """
・画像軽量化: JPEG画像のリサイズと品質調整
・選定画像コピー: 選択した画像の元ファイルをコピー
        """.strip()

        help_label = ttk.Label(
            help_frame, text=help_text, font=("", 9), foreground="gray"
        )
        help_label.pack()

    def _open_reduce_window(self):
        """画像軽量化ウィンドウを開く"""
        ReduceWindow(self.root)

    def _open_choice_window(self):
        """選定画像コピーウィンドウを開く"""
        ChoiceWindow(self.root)

    def _exit_app(self):
        """アプリケーションを終了"""
        self.root.quit()

    def run(self):
        """アプリケーションを実行"""
        self.root.mainloop()
