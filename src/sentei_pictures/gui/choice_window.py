"""
選定画像コピーウィンドウ
選択した画像の元ファイルをコピーする
"""

import shutil
import threading
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

from ..core.file_matcher import FileMatcher
from .widgets import DirectorySelector, ProgressWindow


class ChoiceWindow:
    """選定画像コピーウィンドウクラス"""

    def __init__(self, parent: tk.Widget):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("選定画像コピー")
        self.window.geometry("600x450")
        self.window.resizable(True, False)

        # ウィンドウを親の中央に配置
        self.window.transient(parent)
        self._center_window()

        self._setup_widgets()

    def _center_window(self):
        """ウィンドウを画面中央に配置"""
        self.window.update_idletasks()
        width = 600
        height = 450
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f"{width}x{height}+{x}+{y}")

    def _setup_widgets(self):
        """ウィジェットを設定"""
        # メインフレーム
        main_frame = ttk.Frame(self.window, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # タイトル
        title_label = ttk.Label(main_frame, text="選定画像コピー", font=("", 14, "bold"))
        title_label.pack(pady=(0, 20))

        # 説明
        desc_label = ttk.Label(
            main_frame,
            text="選定した軽量化画像に対応する元の高解像度画像をコピーします",
            font=("", 9),
            foreground="gray",
        )
        desc_label.pack(pady=(0, 15))

        # ディレクトリ選択フレーム
        dirs_frame = ttk.LabelFrame(main_frame, text="ディレクトリ設定", padding="10")
        dirs_frame.pack(fill=tk.X, pady=(0, 15))

        # 元画像ディレクトリ選択
        self.original_selector = DirectorySelector(
            dirs_frame, "元画像ディレクトリ（高解像度の元画像があるフォルダ）:"
        )
        self.original_selector.pack(fill=tk.X, pady=(0, 10))

        # 出力ディレクトリ選択
        self.output_selector = DirectorySelector(
            dirs_frame, "出力ディレクトリ（選定した元画像をコピーするフォルダ）:", create_if_missing=True
        )
        self.output_selector.pack(fill=tk.X, pady=(0, 10))

        # 選定ディレクトリ選択
        self.selected_selector = DirectorySelector(
            dirs_frame, "選定ディレクトリ（選定した軽量化画像があるフォルダ）:"
        )
        self.selected_selector.pack(fill=tk.X)

        # プレビューフレーム
        preview_frame = ttk.LabelFrame(main_frame, text="プレビュー", padding="10")
        preview_frame.pack(fill=tk.X, pady=(0, 15))

        self.preview_label = ttk.Label(
            preview_frame, text="選定ディレクトリを選択すると、処理対象ファイル数が表示されます", foreground="gray"
        )
        self.preview_label.pack()

        # 選定ディレクトリの変更を監視
        self.selected_selector.path_entry.bind("<FocusOut>", self._update_preview)
        self.selected_selector.path_entry.bind(
            "<KeyRelease>", self._schedule_preview_update
        )

        # ボタンフレーム
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        # 実行ボタン
        self.execute_button = ttk.Button(
            button_frame,
            text="コピー開始",
            command=self._execute_choice,
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
        selected_path = self.selected_selector.get_path()
        if selected_path and selected_path.exists():
            try:
                selected_files = FileMatcher.get_image_files(selected_path)
                count = len(selected_files)
                if count > 0:
                    self.preview_label.config(
                        text=f"処理対象: {count}個の選定画像", foreground="blue"
                    )
                    self.execute_button.config(state="normal")
                else:
                    self.preview_label.config(
                        text="画像ファイルが見つかりません", foreground="orange"
                    )
                    self.execute_button.config(state="disabled")
            except Exception:
                self.preview_label.config(text="ディレクトリの読み取りに失敗しました", foreground="red")
                self.execute_button.config(state="disabled")
        else:
            self.preview_label.config(
                text="選定ディレクトリを選択すると、処理対象ファイル数が表示されます", foreground="gray"
            )
            self.execute_button.config(state="disabled")

    def _execute_choice(self):
        """選定画像コピー処理を実行"""
        # 入力値の検証
        original_dir = self.original_selector.get_path()
        output_dir = self.output_selector.get_path()
        selected_dir = self.selected_selector.get_path()

        if not original_dir:
            messagebox.showerror("エラー", "元画像ディレクトリを選択してください")
            return

        if not output_dir:
            messagebox.showerror("エラー", "出力ディレクトリを選択してください")
            return

        if not selected_dir:
            messagebox.showerror("エラー", "選定ディレクトリを選択してください")
            return

        # プログレスウィンドウを表示
        progress_window = ProgressWindow(self.window, "選定画像コピー中...")

        # バックグラウンドで処理を実行
        thread = threading.Thread(
            target=self._choice_worker,
            args=(original_dir, output_dir, selected_dir, progress_window),
            daemon=True,
        )
        thread.start()

    def _choice_worker(
        self,
        original_dir: Path,
        output_dir: Path,
        selected_dir: Path,
        progress_window: ProgressWindow,
    ):
        """選定画像コピー処理のワーカースレッド"""
        try:
            # 選定されたファイルを取得
            progress_window.add_log("選定されたファイルを検索中...")
            selected_files = FileMatcher.get_image_files(selected_dir)

            if not selected_files:
                progress_window.add_log("選定されたファイルが見つかりませんでした")
                progress_window.finish(False)
                return

            progress_window.add_log(f"{len(selected_files)}個の選定されたファイルを処理します")

            success_count = 0
            not_found_files = []

            for i, selected_file in enumerate(selected_files, 1):
                if progress_window.is_cancelled:
                    progress_window.add_log("処理がキャンセルされました")
                    progress_window.finish(False)
                    return

                progress_window.update_progress(
                    i - 1, len(selected_files), f"{selected_file.name} に対応する元画像を検索中..."
                )
                progress_window.add_log(
                    f"[{i}/{len(selected_files)}] {selected_file.name}"
                )

                # 対応する元画像を検索
                original_file = FileMatcher.find_matching_file(
                    selected_file.name, original_dir
                )

                if original_file:
                    output_file = output_dir / original_file.name
                    try:
                        shutil.copy2(original_file, output_file)
                        progress_window.add_log(f"  → {original_file.name} をコピーしました")
                        success_count += 1

                        # ファイルサイズ情報を追加
                        try:
                            file_size_mb = output_file.stat().st_size / (1024 * 1024)
                            progress_window.add_log(
                                f"    (ファイルサイズ: {file_size_mb:.1f}MB)"
                            )
                        except Exception:
                            pass

                    except Exception as e:
                        progress_window.add_log(
                            f"  → エラー: {original_file} のコピーに失敗しました: {e}"
                        )
                else:
                    progress_window.add_log("  → 対応する元画像が見つかりませんでした")
                    not_found_files.append(selected_file.name)

            # 完了
            progress_window.update_progress(
                len(selected_files), len(selected_files), "完了"
            )
            progress_window.add_log(
                f"\\n完了: {success_count}/{len(selected_files)}個のファイルをコピーしました"
            )

            if not_found_files:
                progress_window.add_log(f"\\n見つからなかったファイル ({len(not_found_files)}個):")
                for filename in not_found_files[:10]:  # 最初の10個だけ表示
                    progress_window.add_log(f"  - {filename}")
                if len(not_found_files) > 10:
                    progress_window.add_log(f"  ... 他{len(not_found_files) - 10}個")

            progress_window.finish(True)

        except Exception as e:
            progress_window.add_log(f"エラーが発生しました: {e}")
            progress_window.finish(False)
