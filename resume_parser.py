"""Resume text extraction utilities.

Handles:
- PDF (text-based) via pdfplumber (fallback PyPDF2)
- DOCX via python-docx
- Scanned PDFs via pdf2image + pytesseract (only if OCR flag or low text ratio)

Functions are designed to be lazy with heavy imports (OCR) to keep startup fast.
"""
from __future__ import annotations
import io
import os
import re
from dataclasses import dataclass
from typing import Optional, List, Tuple, Dict

# Light imports first
try:
    import pdfplumber  # type: ignore
except Exception:  # pragma: no cover
    pdfplumber = None

try:
    from PyPDF2 import PdfReader  # type: ignore
except Exception:  # pragma: no cover
    PdfReader = None  # type: ignore

try:
    import docx  # python-docx
except Exception:  # pragma: no cover
    docx = None  # type: ignore

TEXT_CLEAN_RE = re.compile(r"[ \t]+")

SUPPORTED_EXT = {".pdf", ".docx"}


@dataclass
class ParseResult:
    text: str
    meta: Dict[str, str]
    ocr_used: bool = False


def _clean_text(text: str) -> str:
    text = text.replace("\u00a0", " ")
    text = TEXT_CLEAN_RE.sub(" ", text)
    # Normalize bullet styles
    text = re.sub(r"\n[•\-*]\s*", "\n- ", text)
    # Collapse excessive newlines
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _extract_pdf_text(path: str) -> Tuple[str, int]:
    text_parts: List[str] = []
    char_count = 0
    if pdfplumber:
        try:
            with pdfplumber.open(path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text() or ""
                    text_parts.append(page_text)
                    char_count += len(page_text)
            return "\n".join(text_parts), char_count
        except Exception:
            pass  # fallback below
    if PdfReader:
        try:
            reader = PdfReader(path)
            for page in reader.pages:
                page_text = page.extract_text() or ""
                text_parts.append(page_text)
                char_count += len(page_text)
            return "\n".join(text_parts), char_count
        except Exception:
            pass
    raise RuntimeError("Failed to parse PDF (no suitable backend).")


def _extract_docx_text(path: str) -> str:
    if not docx:
        raise RuntimeError("python-docx not installed. Add to requirements.")
    d = docx.Document(path)
    paras = []
    for p in d.paragraphs:
        paras.append(p.text)
    return "\n".join(paras)


def _ocr_pdf(path: str) -> str:
    """OCR a (likely) scanned PDF using pdf2image + pytesseract."""
    try:
        from pdf2image import convert_from_path  # type: ignore
        import pytesseract  # type: ignore
    except Exception as e:  # pragma: no cover
        raise RuntimeError("OCR dependencies missing (pdf2image, pytesseract).") from e

    images = convert_from_path(path)
    texts: List[str] = []
    for im in images:
        txt = pytesseract.image_to_string(im)
        texts.append(txt)
    return "\n".join(texts)


def parse_resume(file_path: str, force_ocr: bool = False, ocr_min_char_threshold: int = 40) -> ParseResult:
    """Parse resume file into text.

    Parameters
    ----------
    file_path: str
        Path to uploaded file on disk.
    force_ocr: bool
        Always perform OCR for PDFs (useful for known scanned doc).
    ocr_min_char_threshold: int
        If extracted PDF text chars less than this, fallback to OCR.
    """
    ext = os.path.splitext(file_path)[1].lower()
    if ext not in SUPPORTED_EXT:
        raise ValueError(f"Unsupported file extension: {ext}. Supported: {SUPPORTED_EXT}")

    ocr_used = False

    if ext == ".pdf":
        if force_ocr:
            text = _ocr_pdf(file_path)
            ocr_used = True
        else:
            raw_text, char_count = _extract_pdf_text(file_path)
            if char_count < ocr_min_char_threshold:
                # fallback to OCR
                text = _ocr_pdf(file_path)
                ocr_used = True
            else:
                text = raw_text
    else:  # docx
        text = _extract_docx_text(file_path)

    clean = _clean_text(text)
    meta = {
        "filename": os.path.basename(file_path),
        "filesize": str(os.path.getsize(file_path)),
        "ocr_used": str(ocr_used),
        "extension": ext,
        "char_len": str(len(clean))
    }
    return ParseResult(text=clean, meta=meta, ocr_used=ocr_used)


if __name__ == "__main__":  # Simple manual test
    import sys
    if len(sys.argv) > 1:
        res = parse_resume(sys.argv[1])
        print(res.meta)
        print(res.text[:1000])
