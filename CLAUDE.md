# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Commands

### Development

```bash
# Install dependencies
poetry install

# Run image reduction script
poetry run python reduce.py <input_directory> <output_directory>

# Run image selection/copy script
poetry run python choice.py <original_directory> <output_directory> <selected_directory>
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
