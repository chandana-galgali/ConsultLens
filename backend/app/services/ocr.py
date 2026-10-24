"""Text extraction, cheapest method first:
   .txt -> read directly | PDF with text layer -> read layer | scan/photo -> Tesseract (or Textract).
Returns (text, engine, confidence). Confidence is the mean word confidence (0-100) when the engine reports it."""
import io
import shutil
from pathlib import Path

import pytesseract
from pdf2image import convert_from_path
from PIL import Image, ImageOps
from pypdf import PdfReader

from ..config import settings

TESS_CFG = "--oem 3 --psm 6"


def _configure_tesseract() -> None:
    """Find Tesseract on Windows even when it is not on PATH."""
    if settings.tesseract_cmd:
        pytesseract.pytesseract.tesseract_cmd = settings.tesseract_cmd
        return
    if shutil.which("tesseract"):
        return
    for candidate in (r"C:\Program Files\Tesseract-OCR\tesseract.exe", r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"):
        if Path(candidate).exists():
            pytesseract.pytesseract.tesseract_cmd = candidate
            return


_configure_tesseract()


def _preprocess(img: Image.Image) -> Image.Image:
    img = ImageOps.autocontrast(ImageOps.grayscale(ImageOps.exif_transpose(img)))
    if img.width < 1500:  # small photos OCR badly; upscale
        scale = 1500 / img.width
        img = img.resize((int(img.width * scale), int(img.height * scale)))
    return img


def _pdf_text_layer(path: Path) -> str:
    try:
        return "\n".join((p.extract_text() or "") for p in PdfReader(str(path)).pages)
    except Exception:
        return ""


def _tesseract(img: Image.Image) -> tuple[str, float | None]:
    """One Tesseract pass; rebuilds the text line by line and averages word confidence."""
    d = pytesseract.image_to_data(img, config=TESS_CFG, output_type=pytesseract.Output.DICT)
    lines: dict[tuple[int, int, int], list[str]] = {}
    confs: list[float] = []
    for i, word in enumerate(d["text"]):
        word = str(word).strip()
        conf = float(d["conf"][i])
        if not word or conf < 0:
            continue
        key = (d["block_num"][i], d["par_num"][i], d["line_num"][i])
        lines.setdefault(key, []).append(word)
        confs.append(conf)
    text = "\n".join(" ".join(ws) for _, ws in sorted(lines.items()))
    return text, (round(sum(confs) / len(confs), 1) if confs else None)


def _textract(image_bytes: bytes) -> str:
    import boto3

    client = boto3.client("textract", region_name=settings.aws_region)
    resp = client.detect_document_text(Document={"Bytes": image_bytes})
    return "\n".join(b["Text"] for b in resp["Blocks"] if b["BlockType"] == "LINE")


def extract_text(path: str) -> tuple[str, str, float | None]:
    """Returns (text, engine_name, confidence_or_None)."""
    p = Path(path)
    ext = p.suffix.lower()

    if ext in {".txt", ".md"}:
        return p.read_text(errors="ignore"), "plain", None

    if ext == ".pdf":
        text = _pdf_text_layer(p)
        if len(text.strip()) > 40:
            return text, "pdf-text", None
        pages = convert_from_path(str(p), dpi=300, poppler_path=settings.poppler_path or None)
        results = [_tesseract(_preprocess(pg)) for pg in pages]
        confs = [c for _, c in results if c is not None]
        return "\n".join(t for t, _ in results), "tesseract", (round(sum(confs) / len(confs), 1) if confs else None)

    img = _preprocess(Image.open(p))
    if settings.use_textract:
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return _textract(buf.getvalue()), "textract", None
    text, conf = _tesseract(img)
    return text, "tesseract", conf
