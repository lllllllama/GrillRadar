"""
PDF OCR Parser for scanned/image-based PDFs

Provides OCR-based text extraction for PDFs that don't contain selectable text,
particularly useful for scanned Chinese resumes.
"""
import logging
import os
from pathlib import Path
from typing import Union, List, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class PdfOcrSettings(BaseModel):
    """
    Configuration for PDF OCR processing

    Attributes:
        enabled: Enable OCR processing (default: True)
        force_ocr: Always use OCR even if text extraction works (default: False)
        min_text_length: Minimum text length to consider text extraction successful (default: 200)
        engine: OCR engine to use (default: "paddleocr")
        lang: OCR language (default: "ch" for Chinese, can be "en" or "ch")
        use_gpu: Use GPU for OCR if available (default: False)
        show_log: Show OCR processing logs (default: False)
    """

    enabled: bool = Field(
        default=True,
        description="Enable OCR processing for PDFs"
    )

    force_ocr: bool = Field(
        default=False,
        description="Always use OCR even if text extraction succeeds"
    )

    min_text_length: int = Field(
        default=200,
        description="Minimum characters to consider text extraction successful"
    )

    engine: str = Field(
        default="paddleocr",
        description="OCR engine: 'paddleocr' or 'tesseract'"
    )

    lang: str = Field(
        default="ch",
        description="OCR language: 'ch' (Chinese), 'en' (English), 'ch_en' (both)"
    )

    use_gpu: bool = Field(
        default=False,
        description="Use GPU for OCR processing"
    )

    show_log: bool = Field(
        default=False,
        description="Show OCR processing logs"
    )

    dpi: int = Field(
        default=200,
        description="DPI for PDF to image conversion"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "enabled": True,
                "force_ocr": False,
                "min_text_length": 200,
                "engine": "paddleocr",
                "lang": "ch",
                "use_gpu": False,
                "show_log": False,
                "dpi": 200
            }
        }


class PdfOcrParser:
    """
    PDF OCR Parser using PaddleOCR

    Converts PDF pages to images and uses OCR to extract text.
    Particularly effective for scanned PDFs and Chinese text.
    """

    def __init__(self, settings: Optional[PdfOcrSettings] = None):
        """
        Initialize OCR parser

        Args:
            settings: OCR settings (uses defaults if None)
        """
        self.settings = settings or PdfOcrSettings()
        self._ocr_engine = None
        self._dependencies_checked = False

    def _check_dependencies(self):
        """Check and import required dependencies"""
        if self._dependencies_checked:
            return

        try:
            # Import pdf2image for PDF to image conversion
            import pdf2image
            from PIL import Image
        except ImportError as e:
            raise ImportError(
                "pdf2image and Pillow are required for OCR. "
                "Install with: pip install pdf2image Pillow\n"
                "On Linux, also install: sudo apt-get install poppler-utils"
            ) from e

        if self.settings.engine == "paddleocr":
            try:
                from paddleocr import PaddleOCR
            except ImportError as e:
                raise ImportError(
                    "PaddleOCR is required for OCR. "
                    "Install with: pip install paddleocr"
                ) from e
        elif self.settings.engine == "tesseract":
            try:
                import pytesseract
            except ImportError as e:
                raise ImportError(
                    "pytesseract is required for Tesseract OCR. "
                    "Install with: pip install pytesseract\n"
                    "Also install Tesseract: sudo apt-get install tesseract-ocr tesseract-ocr-chi-sim"
                ) from e

        self._dependencies_checked = True

    def _init_ocr_engine(self):
        """Initialize OCR engine (lazy loading)"""
        if self._ocr_engine is not None:
            return

        self._check_dependencies()

        if self.settings.engine == "paddleocr":
            from paddleocr import PaddleOCR

            # PaddleOCR initialization
            logger.info(f"Initializing PaddleOCR (lang={self.settings.lang}, gpu={self.settings.use_gpu})")

            self._ocr_engine = PaddleOCR(
                use_angle_cls=True,
                lang=self.settings.lang,
                use_gpu=self.settings.use_gpu,
                show_log=self.settings.show_log
            )

            logger.info("PaddleOCR initialized successfully")

        elif self.settings.engine == "tesseract":
            import pytesseract
            self._ocr_engine = pytesseract
            logger.info("Tesseract OCR initialized")

        else:
            raise ValueError(f"Unsupported OCR engine: {self.settings.engine}")

    def _pdf_to_images(self, pdf_path: Union[str, Path]) -> List:
        """
        Convert PDF pages to images

        Args:
            pdf_path: Path to PDF file

        Returns:
            List of PIL Image objects
        """
        from pdf2image import convert_from_path

        logger.info(f"Converting PDF to images (DPI={self.settings.dpi})")

        try:
            images = convert_from_path(
                pdf_path,
                dpi=self.settings.dpi,
                fmt='JPEG',
                thread_count=4  # Parallel processing
            )

            logger.info(f"Converted PDF to {len(images)} images")
            return images

        except Exception as e:
            logger.error(f"Failed to convert PDF to images: {e}")
            raise

    def _ocr_image(self, image) -> str:
        """
        Extract text from image using OCR

        Args:
            image: PIL Image object

        Returns:
            Extracted text
        """
        if self.settings.engine == "paddleocr":
            return self._ocr_image_paddle(image)
        elif self.settings.engine == "tesseract":
            return self._ocr_image_tesseract(image)
        else:
            raise ValueError(f"Unsupported OCR engine: {self.settings.engine}")

    def _ocr_image_paddle(self, image) -> str:
        """Extract text using PaddleOCR"""
        import numpy as np

        # Convert PIL Image to numpy array
        image_array = np.array(image)

        # Run OCR
        result = self._ocr_engine.ocr(image_array, cls=True)

        # Extract text from results
        text_lines = []
        if result and result[0]:
            for line in result[0]:
                if line and len(line) >= 2:
                    text = line[1][0]  # line[1] is (text, confidence)
                    if text.strip():
                        text_lines.append(text)

        return '\n'.join(text_lines)

    def _ocr_image_tesseract(self, image) -> str:
        """Extract text using Tesseract"""
        lang_map = {
            'ch': 'chi_sim',
            'en': 'eng',
            'ch_en': 'chi_sim+eng'
        }

        tesseract_lang = lang_map.get(self.settings.lang, 'chi_sim')

        text = self._ocr_engine.image_to_string(image, lang=tesseract_lang)
        return text.strip()

    def extract_text(self, pdf_path: Union[str, Path]) -> str:
        """
        Extract text from PDF using OCR

        Args:
            pdf_path: Path to PDF file

        Returns:
            Extracted text content

        Raises:
            Exception: If OCR processing fails
        """
        pdf_path = Path(pdf_path)

        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        logger.info(f"Starting OCR extraction for: {pdf_path.name}")

        # Initialize OCR engine
        self._init_ocr_engine()

        # Convert PDF to images
        images = self._pdf_to_images(pdf_path)

        # Process each page
        page_texts = []
        for i, image in enumerate(images, 1):
            logger.info(f"Processing page {i}/{len(images)} with OCR")

            try:
                page_text = self._ocr_image(image)

                if page_text.strip():
                    # Add page marker
                    page_texts.append(f"=== Page {i} ===\n{page_text}")
                    logger.debug(f"Page {i}: extracted {len(page_text)} characters")
                else:
                    logger.warning(f"Page {i}: no text extracted")

            except Exception as e:
                logger.error(f"Failed to OCR page {i}: {e}")
                page_texts.append(f"=== Page {i} ===\n[OCR failed for this page]")

        # Combine all pages
        full_text = '\n\n'.join(page_texts)

        logger.info(
            f"OCR extraction complete: {len(images)} pages, "
            f"{len(full_text)} total characters"
        )

        return full_text


def create_ocr_settings_from_env() -> PdfOcrSettings:
    """
    Create PdfOcrSettings from environment variables

    Environment variables:
        PDF_OCR_ENABLED: Enable OCR (default: true)
        PDF_OCR_FORCE: Force OCR always (default: false)
        PDF_OCR_MIN_TEXT: Minimum text length (default: 200)
        PDF_OCR_ENGINE: OCR engine (default: paddleocr)
        PDF_OCR_LANG: OCR language (default: ch)
        PDF_OCR_USE_GPU: Use GPU (default: false)
        PDF_OCR_DPI: Image DPI (default: 200)

    Returns:
        PdfOcrSettings instance
    """
    return PdfOcrSettings(
        enabled=os.getenv('PDF_OCR_ENABLED', 'true').lower() == 'true',
        force_ocr=os.getenv('PDF_OCR_FORCE', 'false').lower() == 'true',
        min_text_length=int(os.getenv('PDF_OCR_MIN_TEXT', '200')),
        engine=os.getenv('PDF_OCR_ENGINE', 'paddleocr'),
        lang=os.getenv('PDF_OCR_LANG', 'ch'),
        use_gpu=os.getenv('PDF_OCR_USE_GPU', 'false').lower() == 'true',
        show_log=os.getenv('PDF_OCR_SHOW_LOG', 'false').lower() == 'true',
        dpi=int(os.getenv('PDF_OCR_DPI', '200'))
    )
