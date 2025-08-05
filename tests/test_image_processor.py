"""Tests for ImageProcessor class."""

from pathlib import Path
from unittest.mock import Mock, patch

from PIL import Image

from sentei_pictures.core.image_processor import ImageProcessor


class TestImageProcessor:
    """ImageProcessor class のテスト"""

    def test_init_default_values(self):
        """デフォルト値でのインスタンス化をテスト"""
        processor = ImageProcessor()
        assert processor.max_long_side == 3000
        assert processor.quality == 87

    def test_init_custom_values(self):
        """カスタム値でのインスタンス化をテスト"""
        processor = ImageProcessor(max_long_side=2000, quality=90)
        assert processor.max_long_side == 2000
        assert processor.quality == 90

    def test_is_jpeg_file_valid_extensions(self):
        """有効なJPEG拡張子のテスト"""
        assert ImageProcessor.is_jpeg_file("test.jpg") is True
        assert ImageProcessor.is_jpeg_file("test.jpeg") is True
        assert ImageProcessor.is_jpeg_file("test.JPG") is True
        assert ImageProcessor.is_jpeg_file("test.JPEG") is True

    def test_is_jpeg_file_invalid_extensions(self):
        """無効な拡張子のテスト"""
        assert ImageProcessor.is_jpeg_file("test.png") is False
        assert ImageProcessor.is_jpeg_file("test.gif") is False
        assert ImageProcessor.is_jpeg_file("test.bmp") is False
        assert ImageProcessor.is_jpeg_file("test.txt") is False

    @patch("sentei_pictures.core.image_processor.Image.open")
    def test_get_image_info_success(self, mock_open):
        """画像情報取得の成功ケースをテスト"""
        mock_img = Mock()
        mock_img.size = (1920, 1080)
        mock_open.return_value.__enter__.return_value = mock_img

        processor = ImageProcessor()
        result = processor.get_image_info(Path("test.jpg"))

        assert result == (1920, 1080)
        mock_open.assert_called_once_with(Path("test.jpg"))

    @patch("sentei_pictures.core.image_processor.Image.open")
    def test_get_image_info_failure(self, mock_open):
        """画像情報取得の失敗ケースをテスト"""
        mock_open.side_effect = Exception("File not found")

        processor = ImageProcessor()
        result = processor.get_image_info(Path("nonexistent.jpg"))

        assert result is None

    @patch("sentei_pictures.core.image_processor.Image.open")
    @patch("builtins.print")
    def test_process_image_no_resize_needed(self, mock_print, mock_open):
        """リサイズが不要な場合のテスト"""
        # モックの設定
        mock_img = Mock()
        mock_img.mode = "RGB"
        mock_img.size = (2000, 1500)  # max_long_side (3000) より小さい
        mock_open.return_value.__enter__.return_value = mock_img

        # ファイルサイズのモック
        mock_path = Mock()
        mock_path.stat.return_value.st_size = 1024 * 1024 * 5  # 5MB

        processor = ImageProcessor()

        with patch.object(Path, "stat", return_value=mock_path.stat.return_value):
            result = processor.process_image(Path("input.jpg"), Path("output.jpg"))

        assert result is True
        mock_img.save.assert_called_once_with(
            Path("output.jpg"), "JPEG", quality=87, optimize=True
        )
        # リサイズが呼ばれていないことを確認
        mock_img.resize.assert_not_called()

    @patch("sentei_pictures.core.image_processor.Image.open")
    @patch("builtins.print")
    def test_process_image_with_resize(self, mock_print, mock_open):
        """リサイズが必要な場合のテスト"""
        # モックの設定
        mock_img = Mock()
        mock_img.mode = "RGB"
        mock_img.size = (4000, 3000)  # max_long_side (3000) より大きい
        mock_resized_img = Mock()
        mock_img.resize.return_value = mock_resized_img
        mock_open.return_value.__enter__.return_value = mock_img

        # ファイルサイズのモック
        mock_path = Mock()
        mock_path.stat.return_value.st_size = 1024 * 1024 * 10  # 10MB

        processor = ImageProcessor()

        with patch.object(Path, "stat", return_value=mock_path.stat.return_value):
            result = processor.process_image(Path("input.jpg"), Path("output.jpg"))

        assert result is True
        # リサイズが呼ばれたことを確認
        mock_img.resize.assert_called_once_with((3000, 2250), Image.Resampling.LANCZOS)
        mock_resized_img.save.assert_called_once()

    @patch("sentei_pictures.core.image_processor.Image.open")
    @patch("builtins.print")
    def test_process_image_rgba_conversion(self, mock_print, mock_open):
        """RGBA画像のRGB変換テスト"""
        mock_img = Mock()
        mock_img.mode = "RGBA"
        mock_img.size = (2000, 1500)
        mock_rgb_img = Mock()
        mock_img.convert.return_value = mock_rgb_img
        mock_open.return_value.__enter__.return_value = mock_img

        # ファイルサイズのモック
        mock_output_path = Mock()
        mock_output_path.stat.return_value.st_size = 1024 * 1024 * 5

        processor = ImageProcessor()

        with patch("sentei_pictures.core.image_processor.Path") as mock_path_class:
            mock_path_class.return_value = mock_output_path
            result = processor.process_image(Path("input.png"), mock_output_path)

        assert result is True
        mock_img.convert.assert_called_once_with("RGB")
        mock_rgb_img.save.assert_called_once()

    @patch("sentei_pictures.core.image_processor.Image.open")
    @patch("builtins.print")
    def test_process_image_exception(self, mock_print, mock_open):
        """画像処理中の例外をテスト"""
        mock_open.side_effect = Exception("Processing error")

        processor = ImageProcessor()
        result = processor.process_image(Path("input.jpg"), Path("output.jpg"))

        assert result is False
        mock_print.assert_called_with("エラー: input.jpg の処理に失敗しました: Processing error")
