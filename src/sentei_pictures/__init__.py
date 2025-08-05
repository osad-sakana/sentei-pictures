"""
Sentei Pictures - Photo selection and compression utility

A utility for processing and selecting photos with two main functions:
- reduce: Compress and resize JPEG images for web/print use
- choice: Copy original high-resolution images based on selected reduced versions
"""

__version__ = "0.1.0"
__author__ = "Claude Code Assistant"
__email__ = "noreply@anthropic.com"

from .core.file_matcher import FileMatcher
from .core.image_processor import ImageProcessor

__all__ = ["ImageProcessor", "FileMatcher"]
