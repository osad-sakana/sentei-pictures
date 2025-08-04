"""
画像軽量化スクリプト
JPEGファイルを指定した品質で圧縮して保存します。
"""

import sys
import os
from pathlib import Path
from PIL import Image

def print_usage():
    """使用方法を表示"""
    print("使用方法:")
    print("  poetry run python reduce.py <画像があるパス> <軽量化した画像を保存するパス>")
    print("")
    print("例:")
    print("  poetry run python reduce.py /path/to/original /path/to/reduced")

def is_jpeg_file(filename):
    """JPEGファイルかどうかを判定"""
    jpeg_extensions = {'.jpg', '.jpeg', '.JPG', '.JPEG'}
    return Path(filename).suffix in jpeg_extensions

def reduce_image_quality(input_path, output_path, max_long_side=3000, quality=87):
    """
    画像をリサイズして品質を調整して保存
    - 長辺を最大3000pxにリサイズ（300dpi換算で約25cm）
    - JPEG品質85-90%（デフォルト87%）
    - 目標ファイルサイズ：10-15MB程度
    """
    try:
        with Image.open(input_path) as img:
            # RGB形式に変換（JPEGはRGBのみサポート）
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # リサイズが必要かチェック
            width, height = img.size
            long_side = max(width, height)
            
            if long_side > max_long_side:
                # アスペクト比を保持してリサイズ
                if width > height:
                    new_width = max_long_side
                    new_height = int(height * max_long_side / width)
                else:
                    new_height = max_long_side
                    new_width = int(width * max_long_side / height)
                
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                print(f"  リサイズ: {width}x{height} → {new_width}x{new_height}")
            
            # 品質を調整しながら保存（目標ファイルサイズに合わせて微調整）
            img.save(output_path, 'JPEG', quality=quality, optimize=True)
            
            # ファイルサイズをチェックして表示
            file_size_mb = output_path.stat().st_size / (1024 * 1024)
            print(f"  品質{quality}%で保存完了 (ファイルサイズ: {file_size_mb:.1f}MB)")
            
        return True
    except Exception as e:
        print(f"エラー: {input_path} の処理に失敗しました: {e}")
        return False

def main():
    if len(sys.argv) != 3:
        print("エラー: 引数の数が正しくありません。")
        print_usage()
        sys.exit(1)
    
    input_dir = Path(sys.argv[1])
    output_dir = Path(sys.argv[2])
    
    # 入力ディレクトリの存在チェック
    if not input_dir.exists() or not input_dir.is_dir():
        print(f"エラー: 入力ディレクトリが存在しません: {input_dir}")
        sys.exit(1)
    
    # 出力ディレクトリの作成
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # JPEGファイルを検索
    jpeg_files = []
    for file_path in input_dir.iterdir():
        if file_path.is_file() and is_jpeg_file(file_path.name):
            jpeg_files.append(file_path)
    
    if not jpeg_files:
        print(f"JPEGファイルが見つかりませんでした: {input_dir}")
        sys.exit(0)
    
    print(f"{len(jpeg_files)}個のJPEGファイルを処理します...")
    
    success_count = 0
    for i, input_file in enumerate(jpeg_files, 1):
        output_file = output_dir / input_file.name
        print(f"[{i}/{len(jpeg_files)}] {input_file.name} を処理中...")
        
        if reduce_image_quality(input_file, output_file):
            success_count += 1
    
    print(f"完了: {success_count}/{len(jpeg_files)}個のファイルを軽量化しました。")

if __name__ == "__main__":
    main()