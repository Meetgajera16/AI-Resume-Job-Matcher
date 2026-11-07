from io import BytesIO
from pathlib import Path
from pypdf import PdfReader


class PDFParser:
    def extract_text(self, file_path: str) -> str:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        reader = PdfReader(str(path))
        return self._read_pages(reader)

    def extract_text_from_bytes(self, file_bytes: bytes) -> str:
        """Extract text without persisting a sensitive resume to disk."""

        reader = PdfReader(BytesIO(file_bytes))
        return self._read_pages(reader)

    @staticmethod
    def _read_pages(reader: PdfReader) -> str:
        pages_text = []

        for page in reader.pages:
            text = page.extract_text() or ""
            pages_text.append(text)

        return "\n".join(pages_text).strip()
