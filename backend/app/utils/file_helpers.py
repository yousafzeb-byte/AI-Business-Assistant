import logging
from pypdf import PdfReader

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {"txt", "pdf", "md", "csv"}

# Map extensions to valid MIME type prefixes
MIME_TYPE_MAP = {
    "txt": ["text/"],
    "pdf": ["application/pdf"],
    "md": ["text/"],
    "csv": ["text/", "application/csv"],
}


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def validate_file_mime(file_storage) -> bool:
    """Check that the upload's MIME type is consistent with its extension."""
    filename = file_storage.filename or ""
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    content_type = (file_storage.content_type or "").lower()
    allowed_mimes = MIME_TYPE_MAP.get(ext, [])
    return any(content_type.startswith(m) for m in allowed_mimes)


def extract_text_from_file(file_path: str, filename: str) -> str:
    """Extract text content from an uploaded file."""
    ext = filename.rsplit(".", 1)[1].lower()

    if ext == "pdf":
        return _extract_pdf(file_path)
    else:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()


def _extract_pdf(file_path: str) -> str:
    try:
        reader = PdfReader(file_path)
        text_parts = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
        return "\n".join(text_parts)
    except Exception as e:
        logger.error("PDF extraction error: %s", e)
        raise ValueError(f"Could not extract text from PDF: {e}")
