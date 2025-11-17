"""
Document parser for multi-format resume support

Supports:
- PDF files (.pdf)
- Word documents (.docx, .doc)
- Text files (.txt)
- Markdown files (.md)
"""
import logging
from pathlib import Path
from typing import Union, BinaryIO
import io

logger = logging.getLogger(__name__)


class DocumentParseError(Exception):
    """Exception raised when document parsing fails"""
    pass


class DocumentParser:
    """
    Multi-format document parser for resumes

    Supported formats:
    - PDF (.pdf)
    - Word (.docx)
    - Text (.txt)
    - Markdown (.md)
    """

    SUPPORTED_EXTENSIONS = {'.pdf', '.docx', '.txt', '.md'}

    def __init__(self):
        """Initialize document parser"""
        self._lazy_imports_done = False

    def _lazy_import_dependencies(self):
        """Lazy import heavy dependencies only when needed"""
        if self._lazy_imports_done:
            return

        global pypdf, docx, chardet
        try:
            import pypdf
            import docx
            import chardet
            self._lazy_imports_done = True
        except ImportError as e:
            raise DocumentParseError(
                f"Required parsing library not installed: {e}. "
                "Please run: pip install pypdf python-docx chardet"
            )

    @staticmethod
    def is_supported(file_path: Union[str, Path]) -> bool:
        """
        Check if file format is supported

        Args:
            file_path: Path to file

        Returns:
            True if format is supported, False otherwise
        """
        path = Path(file_path)
        return path.suffix.lower() in DocumentParser.SUPPORTED_EXTENSIONS

    @staticmethod
    def detect_encoding(file_path: Union[str, Path]) -> str:
        """
        Detect text file encoding

        Args:
            file_path: Path to text file

        Returns:
            Detected encoding (e.g., 'utf-8', 'gb2312', 'gbk')
        """
        try:
            import chardet
            with open(file_path, 'rb') as f:
                raw_data = f.read()
                result = chardet.detect(raw_data)
                encoding = result['encoding']
                confidence = result['confidence']

                logger.debug(f"Detected encoding: {encoding} (confidence: {confidence:.2%})")

                # Default to utf-8 if confidence is too low
                if confidence < 0.7:
                    logger.warning(
                        f"Low confidence ({confidence:.2%}) for detected encoding {encoding}, "
                        "defaulting to utf-8"
                    )
                    return 'utf-8'

                return encoding or 'utf-8'
        except Exception as e:
            logger.warning(f"Encoding detection failed: {e}, defaulting to utf-8")
            return 'utf-8'

    def parse_pdf(self, file_path: Union[str, Path]) -> str:
        """
        Parse PDF file to extract text

        Args:
            file_path: Path to PDF file

        Returns:
            Extracted text content

        Raises:
            DocumentParseError: If parsing fails
        """
        self._lazy_import_dependencies()

        try:
            from pypdf import PdfReader

            reader = PdfReader(file_path)
            text_parts = []

            for page_num, page in enumerate(reader.pages, 1):
                try:
                    text = page.extract_text()
                    if text.strip():
                        text_parts.append(text)
                except Exception as e:
                    logger.warning(f"Failed to extract text from page {page_num}: {e}")
                    continue

            if not text_parts:
                raise DocumentParseError("No text could be extracted from PDF")

            full_text = '\n\n'.join(text_parts)
            logger.info(f"Successfully parsed PDF: {len(reader.pages)} pages, {len(full_text)} chars")

            return full_text

        except DocumentParseError:
            raise
        except Exception as e:
            raise DocumentParseError(f"Failed to parse PDF file: {e}")

    def parse_docx(self, file_path: Union[str, Path]) -> str:
        """
        Parse DOCX file to extract text

        Args:
            file_path: Path to DOCX file

        Returns:
            Extracted text content

        Raises:
            DocumentParseError: If parsing fails
        """
        self._lazy_import_dependencies()

        try:
            from docx import Document

            doc = Document(file_path)
            text_parts = []

            # Extract text from paragraphs
            for para in doc.paragraphs:
                if para.text.strip():
                    text_parts.append(para.text)

            # Extract text from tables
            for table in doc.tables:
                for row in table.rows:
                    row_text = '\t'.join(cell.text.strip() for cell in row.cells if cell.text.strip())
                    if row_text:
                        text_parts.append(row_text)

            if not text_parts:
                raise DocumentParseError("No text could be extracted from DOCX")

            full_text = '\n'.join(text_parts)
            logger.info(f"Successfully parsed DOCX: {len(doc.paragraphs)} paragraphs, {len(full_text)} chars")

            return full_text

        except DocumentParseError:
            raise
        except Exception as e:
            raise DocumentParseError(f"Failed to parse DOCX file: {e}")

    def parse_text(self, file_path: Union[str, Path]) -> str:
        """
        Parse text file (TXT, MD)

        Args:
            file_path: Path to text file

        Returns:
            File content

        Raises:
            DocumentParseError: If parsing fails
        """
        try:
            # Try UTF-8 first (most common)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                    logger.info(f"Successfully parsed text file with UTF-8: {len(text)} chars")
                    return text
            except UnicodeDecodeError:
                # Try auto-detection for other encodings (e.g., GBK, GB2312 for Chinese)
                encoding = self.detect_encoding(file_path)
                with open(file_path, 'r', encoding=encoding) as f:
                    text = f.read()
                    logger.info(f"Successfully parsed text file with {encoding}: {len(text)} chars")
                    return text

        except Exception as e:
            raise DocumentParseError(f"Failed to parse text file: {e}")

    def parse_file(self, file_path: Union[str, Path]) -> str:
        """
        Parse file based on extension

        Args:
            file_path: Path to file

        Returns:
            Extracted text content

        Raises:
            DocumentParseError: If file format is unsupported or parsing fails
        """
        path = Path(file_path)

        if not path.exists():
            raise DocumentParseError(f"File not found: {file_path}")

        if not path.is_file():
            raise DocumentParseError(f"Not a file: {file_path}")

        extension = path.suffix.lower()

        if extension not in self.SUPPORTED_EXTENSIONS:
            raise DocumentParseError(
                f"Unsupported file format: {extension}. "
                f"Supported formats: {', '.join(sorted(self.SUPPORTED_EXTENSIONS))}"
            )

        logger.info(f"Parsing document: {path.name} ({extension})")

        # Route to appropriate parser
        if extension == '.pdf':
            return self.parse_pdf(path)
        elif extension == '.docx':
            return self.parse_docx(path)
        elif extension in {'.txt', '.md'}:
            return self.parse_text(path)
        else:
            raise DocumentParseError(f"No parser available for {extension}")

    def parse_bytes(self, file_bytes: bytes, filename: str) -> str:
        """
        Parse file from bytes (useful for API uploads)

        Args:
            file_bytes: File content as bytes
            filename: Original filename (used to determine format)

        Returns:
            Extracted text content

        Raises:
            DocumentParseError: If parsing fails
        """
        extension = Path(filename).suffix.lower()

        if extension not in self.SUPPORTED_EXTENSIONS:
            raise DocumentParseError(
                f"Unsupported file format: {extension}. "
                f"Supported formats: {', '.join(sorted(self.SUPPORTED_EXTENSIONS))}"
            )

        logger.info(f"Parsing uploaded document: {filename} ({extension})")

        try:
            if extension == '.pdf':
                self._lazy_import_dependencies()
                from pypdf import PdfReader

                pdf_file = io.BytesIO(file_bytes)
                reader = PdfReader(pdf_file)
                text_parts = []

                for page in reader.pages:
                    text = page.extract_text()
                    if text.strip():
                        text_parts.append(text)

                if not text_parts:
                    raise DocumentParseError("No text could be extracted from PDF")

                return '\n\n'.join(text_parts)

            elif extension == '.docx':
                self._lazy_import_dependencies()
                from docx import Document

                docx_file = io.BytesIO(file_bytes)
                doc = Document(docx_file)
                text_parts = []

                for para in doc.paragraphs:
                    if para.text.strip():
                        text_parts.append(para.text)

                for table in doc.tables:
                    for row in table.rows:
                        row_text = '\t'.join(cell.text.strip() for cell in row.cells if cell.text.strip())
                        if row_text:
                            text_parts.append(row_text)

                if not text_parts:
                    raise DocumentParseError("No text could be extracted from DOCX")

                return '\n'.join(text_parts)

            elif extension in {'.txt', '.md'}:
                # Try UTF-8 first
                try:
                    return file_bytes.decode('utf-8')
                except UnicodeDecodeError:
                    # Try auto-detection
                    import chardet
                    result = chardet.detect(file_bytes)
                    encoding = result['encoding'] or 'utf-8'
                    return file_bytes.decode(encoding, errors='replace')

            else:
                raise DocumentParseError(f"No parser available for {extension}")

        except DocumentParseError:
            raise
        except Exception as e:
            raise DocumentParseError(f"Failed to parse uploaded file: {e}")


# Singleton instance
document_parser = DocumentParser()


# Convenience functions
def parse_resume(file_path: Union[str, Path]) -> str:
    """
    Parse resume file (convenience function)

    Args:
        file_path: Path to resume file

    Returns:
        Extracted text content

    Raises:
        DocumentParseError: If parsing fails
    """
    return document_parser.parse_file(file_path)


def parse_resume_bytes(file_bytes: bytes, filename: str) -> str:
    """
    Parse resume from bytes (convenience function for API uploads)

    Args:
        file_bytes: File content as bytes
        filename: Original filename

    Returns:
        Extracted text content

    Raises:
        DocumentParseError: If parsing fails
    """
    return document_parser.parse_bytes(file_bytes, filename)


def is_supported_format(filename: str) -> bool:
    """
    Check if filename has supported extension

    Args:
        filename: Filename to check

    Returns:
        True if supported, False otherwise
    """
    return DocumentParser.is_supported(filename)
