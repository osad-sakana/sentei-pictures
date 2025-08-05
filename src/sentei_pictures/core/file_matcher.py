"""
ファイルマッチング機能
選定された画像に対応する元画像を検索する
"""

from pathlib import Path
from typing import List, Optional


class FileMatcher:
    """ファイルマッチングを行うクラス"""

    @staticmethod
    def is_image_file(filename: str) -> bool:
        """画像ファイルかどうかを判定"""
        image_extensions = {
            ".jpg",
            ".jpeg",
            ".JPG",
            ".JPEG",
            ".png",
            ".PNG",
            ".gif",
            ".GIF",
            ".bmp",
            ".BMP",
        }
        return Path(filename).suffix.lower() in {
            ext.lower() for ext in image_extensions
        }

    @staticmethod
    def find_matching_file(filename: str, search_dir: Path) -> Optional[Path]:
        """
        ファイル名に一致するファイルを検索（大文字小文字・拡張子を考慮）

        Args:
            filename: 検索対象のファイル名
            search_dir: 検索ディレクトリ

        Returns:
            Optional[Path]: 見つかったファイルパス or None
        """
        base_name = Path(filename).stem

        # まず完全一致を試す
        if (search_dir / filename).exists():
            return search_dir / filename

        # 拡張子違いや大文字小文字違いを検索
        for file_path in search_dir.iterdir():
            if (
                file_path.is_file()
                and file_path.stem == base_name
                and FileMatcher.is_image_file(file_path.name)
            ):
                return file_path

        # 大文字小文字を無視して検索
        for file_path in search_dir.iterdir():
            if (
                file_path.is_file()
                and file_path.stem.lower() == base_name.lower()
                and FileMatcher.is_image_file(file_path.name)
            ):
                return file_path

        return None

    @staticmethod
    def get_image_files(directory: Path) -> List[Path]:
        """
        ディレクトリから画像ファイルを取得

        Args:
            directory: 検索ディレクトリ

        Returns:
            List[Path]: 画像ファイルのリスト
        """
        image_files = []
        for file_path in directory.iterdir():
            if file_path.is_file() and FileMatcher.is_image_file(file_path.name):
                image_files.append(file_path)
        return image_files

    @staticmethod
    def get_jpeg_files(directory: Path) -> List[Path]:
        """
        ディレクトリからJPEGファイルを取得

        Args:
            directory: 検索ディレクトリ

        Returns:
            List[Path]: JPEGファイルのリスト
        """
        jpeg_extensions = {".jpg", ".jpeg", ".JPG", ".JPEG"}
        jpeg_files = []
        for file_path in directory.iterdir():
            if file_path.is_file() and file_path.suffix in jpeg_extensions:
                jpeg_files.append(file_path)
        return jpeg_files
