"""Recognize text in one bounded project-local PNG/JPEG through Host OCR.

Requires an OCR plugin which AutoJs6 has already enabled and authorized.
"""

from pathlib import Path

from autojs6 import ocr, result


IMAGE_PATH = "fixtures/text.png"

lines = ocr.recognize(Path(IMAGE_PATH).read_bytes())
result.set(
    {
        "image": IMAGE_PATH,
        "lines": list(lines),
    }
)
