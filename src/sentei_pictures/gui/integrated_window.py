"""
統合メニューウィンドウ
画像軽量化→選定画像コピーの一連の流れを管理する
"""

import shutil
import threading
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

from ..core.file_matcher import FileMatcher
from ..core.image_processor import ImageProcessor
from .widgets import DirectorySelector, ProgressWindow, SettingsFrame


class IntegratedWindow:
    """統合メニューウィンドウクラス"""

    def __init__(self, parent: tk.Widget):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("統合メニュー - 写真処理ワークフロー")
        self.window.geometry("700x600")
        self.window.resizable(True, False)

        # ウィンドウを親の中央に配置
        self.window.transient(parent)
        self._center_window()

        self._setup_widgets()

    def _center_window(self):
        """ウィンドウを画面中央に配置"""
        self.window.update_idletasks()
        width = 700
        height = 600
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f"{width}x{height}+{x}+{y}")

    def _setup_widgets(self):
        """ウィジェットを設定"""
        # メインフレーム
        main_frame = ttk.Frame(self.window, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # タイトル
        title_label = ttk.Label(
            main_frame, text="統合メニュー - 写真処理ワークフロー", font=("", 14, "bold")
        )
        title_label.pack(pady=(0, 10))

        # 説明
        desc_text = """
このワークフローでは以下の手順で写真を処理します：
1. 元画像を軽量化してプレビュー用画像を作成
2. プレビュー画像から選定した画像に対応する元画像をコピー
        """.strip()

        desc_label = ttk.Label(
            main_frame, text=desc_text, font=("", 9), foreground="gray"
        )
        desc_label.pack(pady=(0, 20))

        # ステップ1: 画像軽量化設定
        step1_frame = ttk.LabelFrame(main_frame, text="ステップ1: 画像軽量化", padding="10")
        step1_frame.pack(fill=tk.X, pady=(0, 15))

        # 元画像ディレクトリ
        self.original_selector = DirectorySelector(
            step1_frame, "元画像ディレクトリ（高解像度の元画像があるフォルダ）:"
        )
        self.original_selector.pack(fill=tk.X, pady=(0, 10))

        # 軽量化画像出力ディレクトリ
        self.reduced_selector = DirectorySelector(
            step1_frame, "軽量化画像出力ディレクトリ（プレビュー用画像を保存するフォルダ）:", create_if_missing=True
        )
        self.reduced_selector.pack(fill=tk.X, pady=(0, 10))

        # 設定
        self.settings_frame = SettingsFrame(step1_frame)
        self.settings_frame.pack(fill=tk.X)

        # ステップ2: 選定画像コピー設定
        step2_frame = ttk.LabelFrame(main_frame, text="ステップ2: 選定画像コピー", padding="10")
        step2_frame.pack(fill=tk.X, pady=(0, 15))

        # 選定ディレクトリ
        self.selected_selector = DirectorySelector(
            step2_frame, "選定ディレクトリ（選定した軽量化画像があるフォルダ）:"
        )
        self.selected_selector.pack(fill=tk.X, pady=(0, 10))

        # 最終出力ディレクトリ
        self.final_output_selector = DirectorySelector(
            step2_frame, "最終出力ディレクトリ（選定した元画像をコピーするフォルダ）:", create_if_missing=True
        )
        self.final_output_selector.pack(fill=tk.X)

        # プレビューフレーム
        preview_frame = ttk.LabelFrame(main_frame, text="プレビュー", padding="10")
        preview_frame.pack(fill=tk.X, pady=(0, 15))

        self.preview_label = ttk.Label(
            preview_frame, text="元画像ディレクトリを選択すると、処理対象ファイル数が表示されます", foreground="gray"
        )
        self.preview_label.pack()

        # 元画像ディレクトリの変更を監視
        self.original_selector.path_entry.bind("<FocusOut>", self._update_preview)
        self.original_selector.path_entry.bind(
            "<KeyRelease>", self._schedule_preview_update
        )

        # ボタンフレーム
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        # 実行ボタン
        self.execute_button = ttk.Button(
            button_frame,
            text="ワークフロー開始",
            command=self._execute_workflow,
            style="Accent.TButton",
        )
        self.execute_button.pack(side=tk.RIGHT, padx=(5, 0))

        # 軽量化のみ実行ボタン
        self.reduce_only_button = ttk.Button(
            button_frame, text="軽量化のみ実行", command=self._execute_reduce_only
        )
        self.reduce_only_button.pack(side=tk.RIGHT, padx=(5, 0))

        # キャンセルボタン
        ttk.Button(button_frame, text="閉じる", command=self.window.destroy).pack(
            side=tk.RIGHT
        )

        # プレビュー更新タイマー
        self._preview_timer = None

    def _schedule_preview_update(self, event=None):
        """プレビュー更新をスケジュール"""
        if self._preview_timer:
            self.window.after_cancel(self._preview_timer)
        self._preview_timer = self.window.after(500, self._update_preview)

    def _update_preview(self, event=None):
        """プレビューを更新"""
        original_path = self.original_selector.get_path()
        if original_path and original_path.exists():
            try:
                jpeg_files = FileMatcher.get_jpeg_files(original_path)
                count = len(jpeg_files)
                if count > 0:
                    self.preview_label.config(
                        text=f"処理対象: {count}個のJPEGファイル", foreground="blue"
                    )
                    self.execute_button.config(state="normal")
                    self.reduce_only_button.config(state="normal")
                else:
                    self.preview_label.config(
                        text="JPEGファイルが見つかりません", foreground="orange"
                    )
                    self.execute_button.config(state="disabled")
                    self.reduce_only_button.config(state="disabled")
            except Exception:
                self.preview_label.config(text="ディレクトリの読み取りに失敗しました", foreground="red")
                self.execute_button.config(state="disabled")
                self.reduce_only_button.config(state="disabled")
        else:
            self.preview_label.config(
                text="元画像ディレクトリを選択すると、処理対象ファイル数が表示されます", foreground="gray"
            )
            self.execute_button.config(state="disabled")
            self.reduce_only_button.config(state="disabled")

    def _execute_reduce_only(self):
        """軽量化処理のみを実行"""
        # 入力値の検証
        original_dir = self.original_selector.get_path()
        reduced_dir = self.reduced_selector.get_path()

        if not original_dir:
            messagebox.showerror("エラー", "元画像ディレクトリを選択してください")
            return

        if not reduced_dir:
            messagebox.showerror("エラー", "軽量化画像出力ディレクトリを選択してください")
            return

        # 設定値を取得
        settings = self.settings_frame.get_settings()

        # プログレスウィンドウを表示
        progress_window = ProgressWindow(self.window, "画像軽量化中...")

        # バックグラウンドで処理を実行
        thread = threading.Thread(
            target=self._reduce_worker,
            args=(original_dir, reduced_dir, settings, progress_window),
            daemon=True,
        )
        thread.start()

    def _execute_workflow(self):
        """フルワークフローを実行"""
        # 入力値の検証
        original_dir = self.original_selector.get_path()
        reduced_dir = self.reduced_selector.get_path()
        selected_dir = self.selected_selector.get_path()
        final_output_dir = self.final_output_selector.get_path()

        if not original_dir:
            messagebox.showerror("エラー", "元画像ディレクトリを選択してください")
            return

        if not reduced_dir:
            messagebox.showerror("エラー", "軽量化画像出力ディレクトリを選択してください")
            return

        if not selected_dir:
            messagebox.showerror("エラー", "選定ディレクトリを選択してください")
            return

        if not final_output_dir:
            messagebox.showerror("エラー", "最終出力ディレクトリを選択してください")
            return

        # 設定値を取得
        settings = self.settings_frame.get_settings()

        # プログレスウィンドウを表示
        progress_window = ProgressWindow(self.window, "写真処理ワークフロー実行中...")

        # バックグラウンドで処理を実行
        thread = threading.Thread(
            target=self._workflow_worker,
            args=(
                original_dir,
                reduced_dir,
                selected_dir,
                final_output_dir,
                settings,
                progress_window,
            ),
            daemon=True,
        )
        thread.start()

    def _reduce_worker(
        self,
        original_dir: Path,
        reduced_dir: Path,
        settings: dict,
        progress_window: ProgressWindow,
    ):
        """軽量化処理のワーカースレッド"""
        try:
            # JPEGファイルを検索
            progress_window.add_log("JPEGファイルを検索中...")
            jpeg_files = FileMatcher.get_jpeg_files(original_dir)

            if not jpeg_files:
                progress_window.add_log("JPEGファイルが見つかりませんでした")
                progress_window.finish(False)
                return

            progress_window.add_log(f"{len(jpeg_files)}個のJPEGファイルを軽量化します")

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

                output_file = reduced_dir / input_file.name
                progress_window.update_progress(
                    i - 1, len(jpeg_files), f"{input_file.name} を処理中..."
                )
                progress_window.add_log(f"[{i}/{len(jpeg_files)}] {input_file.name}")

                if processor.process_image(input_file, output_file):
                    success_count += 1
                    progress_window.add_log("  → 完了")
                else:
                    progress_window.add_log("  → 失敗")

            # 完了
            progress_window.update_progress(len(jpeg_files), len(jpeg_files), "軽量化完了")
            progress_window.add_log(
                f"\\n軽量化完了: {success_count}/{len(jpeg_files)}個のファイルを処理しました"
            )
            progress_window.finish(True)

        except Exception as e:
            progress_window.add_log(f"エラーが発生しました: {e}")
            progress_window.finish(False)

    def _workflow_worker(
        self,
        original_dir: Path,
        reduced_dir: Path,
        selected_dir: Path,
        final_output_dir: Path,
        settings: dict,
        progress_window: ProgressWindow,
    ):
        """フルワークフローのワーカースレッド"""
        try:
            # ステップ1: 軽量化
            progress_window.add_log("=== ステップ1: 画像軽量化を開始 ===")

            # JPEGファイルを検索
            progress_window.add_log("JPEGファイルを検索中...")
            jpeg_files = FileMatcher.get_jpeg_files(original_dir)

            if not jpeg_files:
                progress_window.add_log("JPEGファイルが見つかりませんでした")
                progress_window.finish(False)
                return

            progress_window.add_log(f"{len(jpeg_files)}個のJPEGファイルを軽量化します")

            # 画像プロセッサーを初期化
            processor = ImageProcessor(
                max_long_side=settings["max_long_side"], quality=settings["quality"]
            )

            reduce_success_count = 0
            total_files = len(jpeg_files)

            for i, input_file in enumerate(jpeg_files, 1):
                if progress_window.is_cancelled:
                    progress_window.add_log("処理がキャンセルされました")
                    progress_window.finish(False)
                    return

                output_file = reduced_dir / input_file.name
                progress_window.update_progress(
                    i - 1, total_files * 2, f"軽量化: {input_file.name}"
                )
                progress_window.add_log(f"[軽量化 {i}/{total_files}] {input_file.name}")

                if processor.process_image(input_file, output_file):
                    reduce_success_count += 1
                    progress_window.add_log("  → 完了")
                else:
                    progress_window.add_log("  → 失敗")

            progress_window.add_log(
                f"\\n軽量化完了: {reduce_success_count}/{total_files}個のファイルを処理しました"
            )
            progress_window.add_log("\\n=== ステップ2: 選定画像コピーを開始 ===")

            # ステップ2: 選定画像コピー
            # 選定されたファイルを取得
            progress_window.add_log("選定されたファイルを検索中...")
            selected_files = FileMatcher.get_image_files(selected_dir)

            if not selected_files:
                progress_window.add_log("選定されたファイルが見つかりませんでした")
                progress_window.add_log("軽量化のみ完了しました")
                progress_window.finish(True)
                return

            progress_window.add_log(f"{len(selected_files)}個の選定されたファイルを処理します")

            choice_success_count = 0
            not_found_files = []

            for i, selected_file in enumerate(selected_files, 1):
                if progress_window.is_cancelled:
                    progress_window.add_log("処理がキャンセルされました")
                    progress_window.finish(False)
                    return

                progress_index = total_files + i - 1
                progress_window.update_progress(
                    progress_index, total_files * 2, f"コピー: {selected_file.name}"
                )
                progress_window.add_log(
                    f"[コピー {i}/{len(selected_files)}] {selected_file.name}"
                )

                # 対応する元画像を検索
                original_file = FileMatcher.find_matching_file(
                    selected_file.name, original_dir
                )

                if original_file:
                    output_file = final_output_dir / original_file.name
                    try:
                        shutil.copy2(original_file, output_file)
                        progress_window.add_log(f"  → {original_file.name} をコピーしました")
                        choice_success_count += 1
                    except Exception as e:
                        progress_window.add_log(f"  → エラー: コピーに失敗しました: {e}")
                else:
                    progress_window.add_log("  → 対応する元画像が見つかりませんでした")
                    not_found_files.append(selected_file.name)

            # 最終結果
            progress_window.update_progress(
                total_files * 2, total_files * 2, "ワークフロー完了"
            )
            progress_window.add_log("\\n=== ワークフロー完了 ===")
            progress_window.add_log(f"軽量化: {reduce_success_count}/{total_files}個")
            progress_window.add_log(
                f"コピー: {choice_success_count}/{len(selected_files)}個"
            )

            if not_found_files:
                progress_window.add_log(f"\\n見つからなかったファイル ({len(not_found_files)}個):")
                for filename in not_found_files[:5]:  # 最初の5個のみ表示
                    progress_window.add_log(f"  - {filename}")
                if len(not_found_files) > 5:
                    progress_window.add_log(f"  ... 他{len(not_found_files) - 5}個")

            progress_window.finish(True)

        except Exception as e:
            progress_window.add_log(f"エラーが発生しました: {e}")
            progress_window.finish(False)
