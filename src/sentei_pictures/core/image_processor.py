"""
画像処理コア機能
JPEGファイルの軽量化・リサイズ処理を行う
"""

from pathlib import Path
from typing import Optional, Tuple

from PIL import Image


class ImageProcessor:
    """画像処理を行うクラス"""

    def __init__(self, max_long_side: int = 3000, quality: int = 87):
        """
        Args:
            max_long_side: 長辺の最大ピクセル数
            quality: JPEG品質（1-100）
        """
        self.max_long_side = max_long_side
        self.quality = quality

    @staticmethod
    def is_jpeg_file(filename: str) -> bool:
        """JPEGファイルかどうかを判定"""
        jpeg_extensions = {".jpg", ".jpeg", ".JPG", ".JPEG"}
        return Path(filename).suffix in jpeg_extensions

    def process_image(self, input_path: Path, output_path: Path) -> bool:
        """
        画像をリサイズして品質を調整して保存

        Args:
            input_path: 入力ファイルパス
            output_path: 出力ファイルパス

        Returns:
            bool: 処理成功時True
        """
        try:
            with Image.open(input_path) as img:
                # RGB形式に変換（JPEGはRGBのみサポート）
                if img.mode in ("RGBA", "LA", "P"):
                    img = img.convert("RGB")

                # リサイズが必要かチェック
                width, height = img.size
                long_side = max(width, height)

                if long_side > self.max_long_side:
                    # アスペクト比を保持してリサイズ
                    if width > height:
                        new_width = self.max_long_side
                        new_height = int(height * self.max_long_side / width)
                    else:
                        new_height = self.max_long_side
                        new_width = int(width * self.max_long_side / height)

                    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    print(f"  リサイズ: {width}x{height} → {new_width}x{new_height}")

                # 品質を調整しながら保存
                img.save(output_path, "JPEG", quality=self.quality, optimize=True)

                # ファイルサイズをチェックして表示
                file_size_mb = output_path.stat().st_size / (1024 * 1024)
                print(f"  品質{self.quality}%で保存完了 (ファイルサイズ: {file_size_mb:.1f}MB)")

            return True
        except Exception as e:
            print(f"エラー: {input_path} の処理に失敗しました: {e}")
            return False

    def get_image_info(self, file_path: Path) -> Optional[Tuple[int, int]]:
        """
        画像の情報を取得

        Args:
            file_path: 画像ファイルパス

        Returns:
            Optional[Tuple[int, int]]: (width, height) or None
        """
        try:
            with Image.open(file_path) as img:
                return img.size
        except Exception:
            return None
