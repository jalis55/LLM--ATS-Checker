"""Extract selectable text from uploaded PDF documents."""

from typing import BinaryIO

import pymupdf


def extract_text_from_pdf(uploaded_file: BinaryIO) -> str:
    """Read a PDF without consuming the upload's current stream position."""
    position = uploaded_file.tell()
    try:
        uploaded_file.seek(0)
        data = uploaded_file.read()
    finally:
        uploaded_file.seek(position)

    if not data:
        raise ValueError("The uploaded PDF is empty.")

    try:
        with pymupdf.open(stream=data, filetype="pdf") as document:
            if document.needs_pass:
                raise ValueError(
                    "This PDF is password-protected. Upload an unlocked copy."
                )
            text = "\n\n".join(page.get_text().strip() for page in document).strip()
    except (pymupdf.FileDataError, RuntimeError) as error:
        raise ValueError(
            "This PDF could not be read. Upload a valid, undamaged PDF."
        ) from error

    if not text:
        raise ValueError(
            "No readable text was found. For scanned PDFs, use OCR first "
            "or paste the document text."
        )
    return text
