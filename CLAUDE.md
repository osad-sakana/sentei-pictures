# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Commands

### Development

```bash
# Install dependencies (including dev dependencies)
poetry install --with dev

# Install package in development mode
poetry install

# 統合メニュー（推奨）
sentei

# 個別コマンド実行
sentei-reduce
sentei-choice

# コマンドライン引数で実行
sentei-reduce <input_directory> <output_directory>
sentei-choice <original_directory> <output_directory> <selected_directory>

# テスト実行
poetry run pytest
poetry run pytest --cov=sentei_pictures

# コード品質チェック
poetry run pre-commit run --all-files
```

### Code Quality

Remove unused imports (e.g., `import os` in reduce.py) when found by linters.

## Architecture Overview

This is a photo processing utility with two complementary Python scripts:

### Core Workflow

1. **reduce.py** - Compresses and resizes JPEG images for web/print use
2. **choice.py** - Copies original high-resolution images based on selected reduced versions

### Image Processing Pipeline

The typical workflow involves two stages:

- **Reduction**: Batch process photos to 3000px max dimension, 87% JPEG quality (~10-15MB files)
- **Selection**: After reviewing reduced images, copy corresponding originals using filename matching

### Key Implementation Details

- **reduce.py**: Uses Pillow with LANCZOS resampling, handles RGBA→RGB conversion, provides progress feedback
- **choice.py**: Implements fuzzy filename matching (case-insensitive, extension-flexible) to handle discrepancies
  between reduced and original filenames
- Both scripts use robust error handling and provide detailed progress output
- File matching logic accounts for different extensions and case variations between directories

### Project Configuration

- Poetry package manager with `package-mode = false`
- Python 3.8+ requirement
- Pillow as the sole external dependency
