"""
画像軽量化ウィンドウ
JPEG画像のリサイズと品質調整を行う
"""

import threading
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

from ..core.file_matcher import FileMatcher
from ..core.image_processor import ImageProcessor
from .widgets import DirectorySelector, ProgressWindow, SettingsFrame


class ReduceWindow:
    """画像軽量化ウィンドウクラス"""

    def __init__(self, parent: tk.Widget):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("画像軽量化")
        self.window.geometry("600x400")
        self.window.resizable(True, False)

        # ウィンドウを親の中央に配置
        self.window.transient(parent)
        self._center_window()

        self._setup_widgets()

    def _center_window(self):
        """ウィンドウを画面中央に配置"""
        self.window.update_idletasks()
        width = 600
        height = 400
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f"{width}x{height}+{x}+{y}")

    def _setup_widgets(self):
        """ウィジェットを設定"""
        # メインフレーム
        main_frame = ttk.Frame(self.window, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # タイトル
        title_label = ttk.Label(main_frame, text="画像軽量化", font=("", 14, "bold"))
        title_label.pack(pady=(0, 20))

        # ディレクトリ選択フレーム
        dirs_frame = ttk.LabelFrame(main_frame, text="ディレクトリ設定", padding="10")
        dirs_frame.pack(fill=tk.X, pady=(0, 15))

        # 入力ディレクトリ選択
        self.input_selector = DirectorySelector(dirs_frame, "入力ディレクトリ（軽量化する画像があるフォルダ）:")
        self.input_selector.pack(fill=tk.X, pady=(0, 10))

        # 出力ディレクトリ選択
        self.output_selector = DirectorySelector(
            dirs_frame, "出力ディレクトリ（軽量化した画像を保存するフォルダ）:", create_if_missing=True
        )
        self.output_selector.pack(fill=tk.X)

        # 設定フレーム
        self.settings_frame = SettingsFrame(main_frame)
        self.settings_frame.pack(fill=tk.X, pady=(0, 15))

        # プレビューフレーム
        preview_frame = ttk.LabelFrame(main_frame, text="プレビュー", padding="10")
        preview_frame.pack(fill=tk.X, pady=(0, 15))

        self.preview_label = ttk.Label(
            preview_frame, text="入力ディレクトリを選択すると、処理対象ファイル数が表示されます", foreground="gray"
        )
        self.preview_label.pack()

        # 入力ディレクトリの変更を監視
        self.input_selector.path_entry.bind("<FocusOut>", self._update_preview)
        self.input_selector.path_entry.bind(
            "<KeyRelease>", self._schedule_preview_update
        )

        # ボタンフレーム
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        # 実行ボタン
        self.execute_button = ttk.Button(
            button_frame,
            text="軽量化開始",
            command=self._execute_reduce,
            style="Accent.TButton",
        )
        self.execute_button.pack(side=tk.RIGHT, padx=(5, 0))

        # キャンセルボタン
        ttk.Button(button_frame, text="閉じる", command=self.window.destroy).pack(
            side=tk.RIGHT
        )

        # プレビュー更新タイマー
        self._preview_timer = None

    def _schedule_preview_update(self, event=None):
        """プレビュー更新をスケジュール（キー入力の度に呼ばれるのを防ぐ）"""
        if self._preview_timer:
            self.window.after_cancel(self._preview_timer)
        self._preview_timer = self.window.after(500, self._update_preview)

    def _update_preview(self, event=None):
        """プレビューを更新"""
        input_path = self.input_selector.get_path()
        if input_path and input_path.exists():
            try:
                jpeg_files = FileMatcher.get_jpeg_files(input_path)
                count = len(jpeg_files)
                if count > 0:
                    self.preview_label.config(
                        text=f"処理対象: {count}個のJPEGファイル", foreground="blue"
                    )
                    self.execute_button.config(state="normal")
                else:
                    self.preview_label.config(
                        text="JPEGファイルが見つかりません", foreground="orange"
                    )
                    self.execute_button.config(state="disabled")
            except Exception:
                self.preview_label.config(text="ディレクトリの読み取りに失敗しました", foreground="red")
                self.execute_button.config(state="disabled")
        else:
            self.preview_label.config(
                text="入力ディレクトリを選択すると、処理対象ファイル数が表示されます", foreground="gray"
            )
            self.execute_button.config(state="disabled")

    def _execute_reduce(self):
        """軽量化処理を実行"""
        # 入力値の検証
        input_dir = self.input_selector.get_path()
        output_dir = self.output_selector.get_path()

        if not input_dir:
            messagebox.showerror("エラー", "入力ディレクトリを選択してください")
            return

        if not output_dir:
            messagebox.showerror("エラー", "出力ディレクトリを選択してください")
            return

        # 設定値を取得
        settings = self.settings_frame.get_settings()

        # プログレスウィンドウを表示
        progress_window = ProgressWindow(self.window, "画像軽量化中...")

        # バックグラウンドで処理を実行
        thread = threading.Thread(
            target=self._reduce_worker,
            args=(input_dir, output_dir, settings, progress_window),
            daemon=True,
        )
        thread.start()

    def _reduce_worker(
        self,
        input_dir: Path,
        output_dir: Path,
        settings: dict,
        progress_window: ProgressWindow,
    ):
        """軽量化処理のワーカースレッド"""
        try:
            # JPEGファイルを検索
            progress_window.add_log("JPEGファイルを検索中...")
            jpeg_files = FileMatcher.get_jpeg_files(input_dir)

            if not jpeg_files:
                progress_window.add_log("JPEGファイルが見つかりませんでした")
                progress_window.finish(False)
                return

            progress_window.add_log(f"{len(jpeg_files)}個のJPEGファイルを処理します")

            # 画像プロセッサーを初期化
            processor = ImageProcessor(
                max_long_side=settings["max_long_side"], quality=settings["quality"]
            )

            success_count = 0

            for i, input_file in enumerate(jpeg_files, 1):
                if progress_window.is_cancelled:
                    progress_window.add_log("処理がキャンセルされました")
                    progress_window.finish(False)
                    return

                output_file = output_dir / input_file.name
                progress_window.update_progress(
                    i - 1, len(jpeg_files), f"{input_file.name} を処理中..."
                )
                progress_window.add_log(f"[{i}/{len(jpeg_files)}] {input_file.name}")

                if processor.process_image(input_file, output_file):
                    success_count += 1
                    # ファイルサイズ情報を追加
                    try:
                        file_size_mb = output_file.stat().st_size / (1024 * 1024)
                        progress_window.add_log(
                            f"  → 完了 (ファイルサイズ: {file_size_mb:.1f}MB)"
                        )
                    except Exception:
                        progress_window.add_log("  → 完了")
                else:
                    progress_window.add_log("  → 失敗")

            # 完了
            progress_window.update_progress(len(jpeg_files), len(jpeg_files), "完了")
            progress_window.add_log(
                f"\\n完了: {success_count}/{len(jpeg_files)}個のファイルを軽量化しました"
            )
            progress_window.finish(True)

        except Exception as e:
            progress_window.add_log(f"エラーが発生しました: {e}")
            progress_window.finish(False)
