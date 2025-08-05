"""Tests for FileMatcher class."""

from pathlib import Path
from unittest.mock import Mock, patch

from sentei_pictures.core.file_matcher import FileMatcher


class TestFileMatcher:
    """FileMatcher class のテスト"""

    def test_is_image_file_valid_extensions(self):
        """有効な画像拡張子のテスト"""
        valid_files = [
            "test.jpg",
            "test.jpeg",
            "test.JPG",
            "test.JPEG",
            "test.png",
            "test.PNG",
            "test.gif",
            "test.GIF",
            "test.bmp",
            "test.BMP",
        ]

        for filename in valid_files:
            assert FileMatcher.is_image_file(filename) is True

    def test_is_image_file_invalid_extensions(self):
        """無効な拡張子のテスト"""
        invalid_files = [
            "test.txt",
            "test.pdf",
            "test.doc",
            "test.mp4",
            "test.zip",
            "test.exe",
            "test",
        ]

        for filename in invalid_files:
            assert FileMatcher.is_image_file(filename) is False

    def test_get_jpeg_files(self):
        """JPEGファイル取得のテスト"""
        # モックディレクトリとファイルを作成
        mock_dir = Mock()
        mock_files = [
            Mock(name="file1.jpg", is_file=Mock(return_value=True), suffix=".jpg"),
            Mock(name="file2.jpeg", is_file=Mock(return_value=True), suffix=".jpeg"),
            Mock(name="file3.JPG", is_file=Mock(return_value=True), suffix=".JPG"),
            Mock(name="file4.png", is_file=Mock(return_value=True), suffix=".png"),
            Mock(name="file5.txt", is_file=Mock(return_value=True), suffix=".txt"),
            Mock(name="subdir", is_file=Mock(return_value=False), suffix=""),
        ]
        mock_dir.iterdir.return_value = mock_files

        result = FileMatcher.get_jpeg_files(mock_dir)

        # JPEGファイルのみが返されることを確認
        assert len(result) == 3
        assert mock_files[0] in result  # file1.jpg
        assert mock_files[1] in result  # file2.jpeg
        assert mock_files[2] in result  # file3.JPG

    def test_get_image_files(self):
        """画像ファイル取得のテスト"""
        mock_dir = Mock()
        mock_files = [
            Mock(is_file=Mock(return_value=True), name="file1.jpg"),
            Mock(is_file=Mock(return_value=True), name="file2.png"),
            Mock(is_file=Mock(return_value=True), name="file3.gif"),
            Mock(is_file=Mock(return_value=True), name="file4.txt"),
            Mock(is_file=Mock(return_value=False), name="subdir"),
        ]
        mock_dir.iterdir.return_value = mock_files

        with patch.object(FileMatcher, "is_image_file") as mock_is_image:
            mock_is_image.side_effect = lambda name: name.endswith(
                (".jpg", ".png", ".gif")
            )

            result = FileMatcher.get_image_files(mock_dir)

        # 画像ファイルのみが返されることを確認
        assert len(result) == 3
        assert mock_files[0] in result  # file1.jpg
        assert mock_files[1] in result  # file2.png
        assert mock_files[2] in result  # file3.gif

    def test_find_matching_file_exact_match(self):
        """完全一致でのファイル検索テスト"""
        mock_dir = Mock()
        mock_file = Mock()
        mock_file.exists.return_value = True

        with patch.object(Path, "__truediv__", return_value=mock_file):
            result = FileMatcher.find_matching_file("test.jpg", mock_dir)

        assert result == mock_file

    def test_find_matching_file_stem_match(self):
        """ベース名一致でのファイル検索テスト"""
        mock_dir = Mock()

        # 完全一致はしない
        mock_exact_file = Mock()
        mock_exact_file.exists.return_value = False

        # iterdir でファイルを返す
        mock_matching_file = Mock()
        mock_matching_file.is_file.return_value = True
        mock_matching_file.stem = "test"
        mock_matching_file.name = "test.png"

        mock_non_matching_file = Mock()
        mock_non_matching_file.is_file.return_value = True
        mock_non_matching_file.stem = "other"
        mock_non_matching_file.name = "other.jpg"

        mock_dir.iterdir.return_value = [mock_matching_file, mock_non_matching_file]

        with patch.object(Path, "__truediv__", return_value=mock_exact_file):
            with patch.object(FileMatcher, "is_image_file") as mock_is_image:
                mock_is_image.side_effect = lambda name: name.endswith((".jpg", ".png"))

                result = FileMatcher.find_matching_file("test.jpg", mock_dir)

        assert result == mock_matching_file

    def test_find_matching_file_case_insensitive_match(self):
        """大文字小文字を無視したファイル検索テスト"""
        mock_dir = Mock()

        # 完全一致とベース名一致はしない
        mock_exact_file = Mock()
        mock_exact_file.exists.return_value = False

        mock_non_matching_file1 = Mock()
        mock_non_matching_file1.is_file.return_value = True
        mock_non_matching_file1.stem = "other"
        mock_non_matching_file1.name = "other.jpg"

        mock_matching_file = Mock()
        mock_matching_file.is_file.return_value = True
        mock_matching_file.stem = "TEST"  # 大文字
        mock_matching_file.stem.lower.return_value = "test"
        mock_matching_file.name = "TEST.png"

        mock_dir.iterdir.return_value = [mock_non_matching_file1, mock_matching_file]

        with patch.object(Path, "__truediv__", return_value=mock_exact_file):
            with patch.object(FileMatcher, "is_image_file") as mock_is_image:
                mock_is_image.side_effect = lambda name: name.endswith((".jpg", ".png"))

                result = FileMatcher.find_matching_file("test.jpg", mock_dir)

        assert result == mock_matching_file

    def test_find_matching_file_not_found(self):
        """ファイルが見つからない場合のテスト"""
        mock_dir = Mock()

        # 完全一致はしない
        mock_exact_file = Mock()
        mock_exact_file.exists.return_value = False

        # 一致するファイルがない
        mock_non_matching_file = Mock()
        mock_non_matching_file.is_file.return_value = True
        mock_non_matching_file.stem = "other"
        mock_non_matching_file.stem.lower.return_value = "other"
        mock_non_matching_file.name = "other.jpg"

        mock_dir.iterdir.return_value = [mock_non_matching_file]

        with patch.object(Path, "__truediv__", return_value=mock_exact_file):
            with patch.object(FileMatcher, "is_image_file") as mock_is_image:
                mock_is_image.side_effect = lambda name: name.endswith((".jpg", ".png"))

                result = FileMatcher.find_matching_file("test.jpg", mock_dir)

        assert result is None
