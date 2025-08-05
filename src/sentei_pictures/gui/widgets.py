"""
GUI共通ウィジェット
ディレクトリ選択、プログレス表示などの再利用可能なコンポーネント
"""

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Optional


class DirectorySelector(ttk.Frame):
    """ディレクトリ選択ウィジェット"""

    def __init__(
        self,
        parent: tk.Widget,
        label_text: str,
        initial_path: str = "",
        create_if_missing: bool = False,
    ):
        super().__init__(parent)
        self.create_if_missing = create_if_missing
        self._path_var = tk.StringVar(value=initial_path)
        self._setup_widgets(label_text)

    def _setup_widgets(self, label_text: str):
        """ウィジェットを設定"""
        # ラベル
        ttk.Label(self, text=label_text).grid(row=0, column=0, sticky="w", pady=(0, 5))

        # パス入力フレーム
        path_frame = ttk.Frame(self)
        path_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        path_frame.columnconfigure(0, weight=1)

        # パス入力フィールド
        self.path_entry = ttk.Entry(path_frame, textvariable=self._path_var, width=50)
        self.path_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))

        # 参照ボタン
        ttk.Button(path_frame, text="参照", command=self._browse_directory).grid(
            row=0, column=1
        )

        self.columnconfigure(0, weight=1)

    def _browse_directory(self):
        """ディレクトリ参照ダイアログを開く"""
        initial_dir = self._path_var.get() or str(Path.home())
        directory = filedialog.askdirectory(initialdir=initial_dir)
        if directory:
            self._path_var.set(directory)

    def get_path(self) -> Optional[Path]:
        """選択されたパスを取得"""
        path_str = self._path_var.get().strip()
        if not path_str:
            return None

        path = Path(path_str)

        if self.create_if_missing:
            try:
                path.mkdir(parents=True, exist_ok=True)
                return path
            except Exception as e:
                messagebox.showerror("エラー", f"ディレクトリを作成できません: {e}")
                return None
        else:
            if not path.exists():
                messagebox.showerror("エラー", f"指定されたパスが存在しません: {path_str}")
                return None
            if not path.is_dir():
                messagebox.showerror("エラー", f"指定されたパスはディレクトリではありません: {path_str}")
                return None
            return path

    def set_path(self, path: str):
        """パスを設定"""
        self._path_var.set(path)


class ProgressWindow:
    """プログレス表示ウィンドウ"""

    def __init__(self, parent: tk.Widget, title: str = "処理中..."):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title(title)
        self.window.geometry("500x300")
        self.window.resizable(True, True)

        # ウィンドウを親の中央に配置
        self.window.transient(parent)
        self.window.grab_set()

        self._setup_widgets()
        self.is_cancelled = False

    def _setup_widgets(self):
        """ウィジェットを設定"""
        # メインフレーム
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # プログレスバー
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            main_frame, mode="determinate", variable=self.progress_var
        )
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))

        # ステータスラベル
        self.status_var = tk.StringVar(value="準備中...")
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var)
        self.status_label.pack(pady=(0, 10))

        # ログ表示エリア
        log_frame = ttk.Frame(main_frame)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.log_text = tk.Text(log_frame, wrap=tk.WORD, height=10)
        scrollbar = ttk.Scrollbar(
            log_frame, orient=tk.VERTICAL, command=self.log_text.yview
        )
        self.log_text.configure(yscrollcommand=scrollbar.set)

        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # キャンセルボタン
        self.cancel_button = ttk.Button(main_frame, text="キャンセル", command=self._cancel)
        self.cancel_button.pack(pady=(0, 5))

        # 閉じるボタン（初期は無効）
        self.close_button = ttk.Button(
            main_frame, text="閉じる", command=self._close, state="disabled"
        )
        self.close_button.pack()

    def update_progress(self, current: int, total: int, message: str = ""):
        """プログレスを更新"""
        if total > 0:
            progress = (current / total) * 100
            self.progress_var.set(progress)

        status_text = f"{current}/{total}"
        if message:
            status_text += f" - {message}"
        self.status_var.set(status_text)

        self.window.update_idletasks()

    def add_log(self, message: str):
        """ログメッセージを追加"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.window.update_idletasks()

    def _cancel(self):
        """処理をキャンセル"""
        self.is_cancelled = True
        self.cancel_button.config(state="disabled")
        self.add_log("キャンセルが要求されました...")

    def finish(self, success: bool = True):
        """処理完了"""
        self.cancel_button.config(state="disabled")
        self.close_button.config(state="normal")

        if success:
            self.status_var.set("処理が完了しました")
            self.add_log("✓ 処理が正常に完了しました")
        else:
            self.status_var.set("処理が失敗しました")
            self.add_log("✗ 処理が失敗しました")

    def _close(self):
        """ウィンドウを閉じる"""
        self.window.destroy()


class SettingsFrame(ttk.LabelFrame):
    """設定フレーム（reduce用）"""

    def __init__(self, parent: tk.Widget):
        super().__init__(parent, text="設定", padding="10")
        self._setup_widgets()

    def _setup_widgets(self):
        """ウィジェットを設定"""
        # JPEG品質設定
        ttk.Label(self, text="JPEG品質 (1-100):").grid(
            row=0, column=0, sticky="w", padx=(0, 10)
        )
        self.quality_var = tk.IntVar(value=87)
        quality_spin = ttk.Spinbox(
            self, from_=1, to=100, textvariable=self.quality_var, width=10
        )
        quality_spin.grid(row=0, column=1, sticky="w")

        # 最大長辺設定
        ttk.Label(self, text="最大長辺 (px):").grid(
            row=1, column=0, sticky="w", padx=(0, 10), pady=(10, 0)
        )
        self.max_size_var = tk.IntVar(value=3000)
        size_spin = ttk.Spinbox(
            self,
            from_=500,
            to=10000,
            increment=100,
            textvariable=self.max_size_var,
            width=10,
        )
        size_spin.grid(row=1, column=1, sticky="w", pady=(10, 0))

    def get_settings(self) -> dict:
        """設定値を取得"""
        return {
            "quality": self.quality_var.get(),
            "max_long_side": self.max_size_var.get(),
        }
