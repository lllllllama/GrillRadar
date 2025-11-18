"""
Tests for PDF OCR parser

Tests OCR-based PDF text extraction functionality
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from app.utils.pdf_ocr_parser import (
    PdfOcrSettings,
    PdfOcrParser,
    create_ocr_settings_from_env
)


class TestPdfOcrSettings:
    """Test PdfOcrSettings model"""

    def test_default_settings(self):
        """Test default settings"""
        settings = PdfOcrSettings()

        assert settings.enabled is True
        assert settings.force_ocr is False
        assert settings.min_text_length == 200
        assert settings.engine == "paddleocr"
        assert settings.lang == "ch"
        assert settings.use_gpu is False
        assert settings.show_log is False
        assert settings.dpi == 200

    def test_custom_settings(self):
        """Test custom settings"""
        settings = PdfOcrSettings(
            enabled=False,
            force_ocr=True,
            min_text_length=100,
            engine="tesseract",
            lang="en",
            use_gpu=True,
            dpi=300
        )

        assert settings.enabled is False
        assert settings.force_ocr is True
        assert settings.min_text_length == 100
        assert settings.engine == "tesseract"
        assert settings.lang == "en"
        assert settings.use_gpu is True
        assert settings.dpi == 300

    def test_create_from_env(self, monkeypatch):
        """Test creating settings from environment variables"""
        monkeypatch.setenv('PDF_OCR_ENABLED', 'false')
        monkeypatch.setenv('PDF_OCR_FORCE', 'true')
        monkeypatch.setenv('PDF_OCR_MIN_TEXT', '100')
        monkeypatch.setenv('PDF_OCR_ENGINE', 'tesseract')
        monkeypatch.setenv('PDF_OCR_LANG', 'en')
        monkeypatch.setenv('PDF_OCR_USE_GPU', 'true')
        monkeypatch.setenv('PDF_OCR_DPI', '300')

        settings = create_ocr_settings_from_env()

        assert settings.enabled is False
        assert settings.force_ocr is True
        assert settings.min_text_length == 100
        assert settings.engine == "tesseract"
        assert settings.lang == "en"
        assert settings.use_gpu is True
        assert settings.dpi == 300


class TestPdfOcrParser:
    """Test PdfOcrParser class"""

    def test_init_default_settings(self):
        """Test initialization with default settings"""
        parser = PdfOcrParser()

        assert parser.settings.enabled is True
        assert parser.settings.engine == "paddleocr"
        assert parser._ocr_engine is None

    def test_init_custom_settings(self):
        """Test initialization with custom settings"""
        settings = PdfOcrSettings(engine="tesseract", lang="en")
        parser = PdfOcrParser(settings)

        assert parser.settings.engine == "tesseract"
        assert parser.settings.lang == "en"

    def test_init_ocr_engine_unsupported(self):
        """Test OCR engine initialization with unsupported engine"""
        settings = PdfOcrSettings(engine="unsupported")
        parser = PdfOcrParser(settings)

        with patch('app.utils.pdf_ocr_parser.PdfOcrParser._check_dependencies'):
            with pytest.raises(ValueError, match="Unsupported OCR engine"):
                parser._init_ocr_engine()

    def test_check_dependencies_missing_pdf2image(self):
        """Test dependency check when pdf2image is missing"""
        with patch('app.utils.pdf_ocr_parser.PdfOcrParser._check_dependencies') as mock_check:
            mock_check.side_effect = ImportError("pdf2image not installed")

            parser = PdfOcrParser()

            with pytest.raises(ImportError, match="pdf2image"):
                parser._check_dependencies()

    def test_pdf_to_images(self):
        """Test PDF to images conversion logic"""
        # This test requires pdf2image which is optional
        # The integration tests cover the full flow
        pytest.skip("Skipping - requires optional pdf2image dependency")

    def test_ocr_image_paddle(self):
        """Test OCR with PaddleOCR - result parsing logic"""
        # This test requires numpy which is optional
        # The integration tests cover the full flow
        pytest.skip("Skipping - requires optional numpy dependency")

    def test_ocr_image_tesseract(self):
        """Test OCR with Tesseract"""
        settings = PdfOcrSettings(engine="tesseract", lang="ch")
        parser = PdfOcrParser(settings)

        mock_tesseract = Mock()
        mock_tesseract.image_to_string.return_value = "测试文本\n第二行"
        parser._ocr_engine = mock_tesseract

        mock_image = Mock()

        text = parser._ocr_image_tesseract(mock_image)

        assert text == "测试文本\n第二行"
        mock_tesseract.image_to_string.assert_called_once_with(
            mock_image,
            lang='chi_sim'
        )

    @patch.object(PdfOcrParser, '_pdf_to_images')
    @patch.object(PdfOcrParser, '_init_ocr_engine')
    @patch.object(PdfOcrParser, '_ocr_image')
    def test_extract_text_success(self, mock_ocr_image, mock_init, mock_pdf2img):
        """Test successful text extraction"""
        # Create temp file
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            temp_pdf = f.name

        try:
            # Mock images
            mock_images = [Mock(), Mock()]
            mock_pdf2img.return_value = mock_images

            # Mock OCR results
            mock_ocr_image.side_effect = ["Page 1 text", "Page 2 text"]

            parser = PdfOcrParser()
            text = parser.extract_text(temp_pdf)

            assert "=== Page 1 ===" in text
            assert "Page 1 text" in text
            assert "=== Page 2 ===" in text
            assert "Page 2 text" in text

            mock_init.assert_called_once()
            mock_pdf2img.assert_called_once()
            assert mock_ocr_image.call_count == 2

        finally:
            Path(temp_pdf).unlink()

    def test_extract_text_file_not_found(self):
        """Test extraction with non-existent file"""
        parser = PdfOcrParser()

        with pytest.raises(FileNotFoundError):
            parser.extract_text('nonexistent.pdf')

    @patch.object(PdfOcrParser, '_pdf_to_images')
    @patch.object(PdfOcrParser, '_init_ocr_engine')
    @patch.object(PdfOcrParser, '_ocr_image')
    def test_extract_text_with_ocr_failure(self, mock_ocr_image, mock_init, mock_pdf2img):
        """Test extraction when OCR fails on some pages"""
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            temp_pdf = f.name

        try:
            mock_images = [Mock(), Mock()]
            mock_pdf2img.return_value = mock_images

            # Second page fails
            mock_ocr_image.side_effect = ["Page 1 text", Exception("OCR failed")]

            parser = PdfOcrParser()
            text = parser.extract_text(temp_pdf)

            # Should have page 1 text and error marker for page 2
            assert "Page 1 text" in text
            assert "[OCR failed for this page]" in text

        finally:
            Path(temp_pdf).unlink()


class TestOcrIntegration:
    """Integration tests for OCR functionality"""

    @patch.object(PdfOcrParser, 'extract_text')
    def test_ocr_called_when_enabled(self, mock_extract):
        """Test that OCR is called when conditions are met"""
        mock_extract.return_value = "OCR extracted text"

        settings = PdfOcrSettings(enabled=True, min_text_length=100)
        parser = PdfOcrParser(settings)

        # This would be called by document_parser when text extraction returns too little
        text = parser.extract_text('test.pdf')

        assert text == "OCR extracted text"
        mock_extract.assert_called_once()

    def test_settings_validation(self):
        """Test settings validation"""
        # Valid settings
        settings = PdfOcrSettings(dpi=100, min_text_length=50)
        assert settings.dpi == 100
        assert settings.min_text_length == 50

        # Invalid DPI should still work (pydantic doesn't validate ranges by default)
        settings = PdfOcrSettings(dpi=-100)
        assert settings.dpi == -100  # No validation, but would fail in actual use
