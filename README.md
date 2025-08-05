# Sentei Pictures

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

写真選定・圧縮ユーティリティ - Photo selection and compression utility

## 概要

Sentei Picturesは、大量の写真を効率的に処理・選定するためのPython製ユーティリティです。
主に以下の2つの機能を提供します：

- **reduce**: JPEG画像の軽量化（リサイズ・品質調整）
- **choice**: 選定した画像に対応する元画像のコピー

## 特徴

- 📸 JPEG画像の高品質な軽量化（最大3000px、品質87%）
- 🔍 ファジーファイル名マッチング（大文字小文字・拡張子の違いを吸収）
- 💬 対話型インターフェース
- ⚡ コマンドライン引数での一括処理
- 🛡️ 堅牢なエラーハンドリング
- 📊 処理進捗の詳細表示

## インストール

### 要件

- Python 3.9以上
- Poetry (推奨) または pip

### Poetry使用（推奨）

```bash
# リポジトリをクローン
git clone <repository-url>
cd sentei-pictures

# 依存関係をインストール
poetry install

# 開発版としてインストール
poetry install --with dev
```

### pip使用

```bash
pip install -e .
```

## 使用方法

### 1. 統合メニュー（推奨）

```bash
sentei
```

対話型メニューでreduce/choice機能を選択できます。

### 2. 個別コマンド

#### 画像軽量化（reduce）

```bash
# 対話型
sentei-reduce

# コマンドライン引数
sentei-reduce /path/to/original /path/to/reduced
```

#### 選定画像コピー（choice）

```bash
# 対話型
sentei-choice

# コマンドライン引数
sentei-choice /path/to/original /path/to/selected /path/to/reduced
```

## ワークフロー例

### 一般的な写真選定ワークフロー

1. **軽量化**: 元画像（50MB/枚）を軽量化（10-15MB/枚）

   ```bash
   sentei-reduce /original/photos /reduced/photos
   ```

2. **選定**: 軽量化された画像から気に入ったものを別フォルダにコピー

   ```bash
   cp /reduced/photos/IMG_001.jpg /selected/
   cp /reduced/photos/IMG_005.jpg /selected/
   # ... 手動で選定
   ```

3. **元画像取得**: 選定した画像に対応する元画像を取得

   ```bash
   sentei-choice /original/photos /final/photos /selected/
   ```

## 技術詳細

### 画像処理仕様

- **リサイズ**: 長辺最大3000px（アスペクト比保持）
- **品質**: JPEG品質87%（最適化有効）
- **色空間**: RGBA/LA/P → RGB自動変換
- **リサンプリング**: LANCZOS（高品質）

### ファイルマッチング

- 完全一致 → 拡張子違い → 大文字小文字違いの順で検索
- 対応画像拡張子: `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`（大文字小文字問わず）

## 開発

### 開発環境セットアップ

```bash
# 開発依存関係をインストール
poetry install --with dev

# pre-commitフックを設定
poetry run pre-commit install
```

### テスト実行

```bash
# 全テスト実行
poetry run pytest

# カバレッジ付き
poetry run pytest --cov=sentei_pictures

# 特定のテストファイル
poetry run pytest tests/test_image_processor.py
```

### コード品質チェック

```bash
# pre-commitフック手動実行
poetry run pre-commit run --all-files

# 個別実行
poetry run black src/ tests/
poetry run flake8 src/ tests/
poetry run isort src/ tests/
```

## プロジェクト構造

```text
sentei-pictures/
├── src/sentei_pictures/          # メインパッケージ
│   ├── __init__.py
│   ├── core/                     # コア機能
│   │   ├── __init__.py
│   │   ├── image_processor.py    # 画像処理
│   │   └── file_matcher.py       # ファイルマッチング
│   └── cli/                      # コマンドライン interface
│       ├── __init__.py
│       ├── main.py               # 統合メニュー
│       ├── reduce.py             # reduce コマンド
│       ├── choice.py             # choice コマンド
│       └── input_handler.py      # ユーザー入力処理
├── tests/                        # テストスイート
├── pyproject.toml               # プロジェクト設定
└── README.md
```

## ライセンス

MIT License - 詳細は [LICENSE](LICENSE) ファイルを参照してください。

## 貢献

Issues、Pull Requestsを歓迎します。大きな変更を行う前に、まずissueで相談してください。

## 変更履歴

### v0.1.0

- 初期リリース
- reduce機能（画像軽量化）
- choice機能（選定画像コピー）
- 対話型・コマンドライン両対応
- 統合メニュー
