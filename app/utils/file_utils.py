from pathlib import Path
from fastapi import UploadFile, HTTPException


def ensure_directory(path: str) -> None:
    Path(path).mkdir(parents=True, exist_ok=True)


def validate_pdf_file(file: UploadFile, max_size_mb: int) -> None:
    if not file.filename:
        raise HTTPException(status_code=400, detail="File must have a filename.")

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    content_type = (file.content_type or "").lower()
    if content_type and content_type not in {"application/pdf", "application/octet-stream"}:
        raise HTTPException(status_code=400, detail="Uploaded file is not a valid PDF.")

def validate_pdf_bytes(file_bytes: bytes, max_size_mb: int) -> None:
    if not file_bytes:
        raise HTTPException(status_code=400, detail="The uploaded PDF is empty.")
    if len(file_bytes) > max_size_mb * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds the {max_size_mb} MB limit.",
        )
    if not file_bytes.startswith(b"%PDF-"):
        raise HTTPException(status_code=400, detail="The file does not have a valid PDF signature.")


def safe_filename(filename: str) -> str:
    """Drop path components and characters unsafe for local storage."""

    name = Path(filename).name
    cleaned = "".join(char if char.isalnum() or char in "._- " else "_" for char in name)
    return cleaned.strip(" .") or "document.pdf"
