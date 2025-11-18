"""
Integration tests for DocumentParser OCR functionality

Tests the smart fallback logic between text extraction and OCR
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import tempfile

from app.utils.document_parser import DocumentParser
from app.utils.pdf_ocr_parser import PdfOcrSettings


class TestDocumentParserOcrIntegration:
    """Test OCR integration in DocumentParser"""

    def test_parse_pdf_no_ocr_when_text_sufficient(self):
        """Test that OCR is NOT used when text extraction returns sufficient text"""
        # Create settings with OCR enabled
        ocr_settings = PdfOcrSettings(
            enabled=True,
            min_text_length=200
        )

        parser = DocumentParser(ocr_settings=ocr_settings)

        # Mock text extraction to return sufficient text (>200 chars)
        sufficient_text = "This is a test PDF with sufficient text. " * 10  # 410+ chars

        with patch.object(DocumentParser, '_extract_pdf_text_original', return_value=sufficient_text):
            with patch.object(parser, '_get_ocr_parser') as mock_get_ocr:
                # Create temp file
                with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
                    temp_pdf = f.name

                try:
                    result = parser.parse_pdf(temp_pdf)

                    # Should return the text-based extraction
                    assert result == sufficient_text

                    # OCR parser should NOT be initialized
                    mock_get_ocr.assert_not_called()

                finally:
                    Path(temp_pdf).unlink()

    def test_parse_pdf_uses_ocr_when_text_insufficient(self):
        """Test that OCR IS used when text extraction returns insufficient text"""
        ocr_settings = PdfOcrSettings(
            enabled=True,
            min_text_length=200
        )

        parser = DocumentParser(ocr_settings=ocr_settings)

        # Mock text extraction to return insufficient text (<200 chars)
        insufficient_text = "Short text."  # Only 11 chars
        ocr_extracted_text = "OCR extracted much longer text content. " * 10  # 410+ chars

        with patch.object(DocumentParser, '_extract_pdf_text_original', return_value=insufficient_text):
            # Mock OCR parser
            mock_ocr_parser = Mock()
            mock_ocr_parser.extract_text.return_value = ocr_extracted_text

            with patch.object(parser, '_get_ocr_parser', return_value=mock_ocr_parser):
                with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
                    temp_pdf = f.name

                try:
                    result = parser.parse_pdf(temp_pdf)

                    # Should return OCR result
                    assert result == ocr_extracted_text

                    # OCR parser should be called (path could be string or Path)
                    assert mock_ocr_parser.extract_text.call_count == 1
                    call_args = mock_ocr_parser.extract_text.call_args[0][0]
                    assert str(call_args) == temp_pdf

                finally:
                    Path(temp_pdf).unlink()

    def test_parse_pdf_force_ocr_true(self):
        """Test that OCR is ALWAYS used when force_ocr=True"""
        ocr_settings = PdfOcrSettings(
            enabled=True,
            force_ocr=True,  # Force OCR
            min_text_length=200
        )

        parser = DocumentParser(ocr_settings=ocr_settings)

        # Even with sufficient text available
        sufficient_text = "This is sufficient text. " * 20
        ocr_text = "OCR extracted text (forced). " * 20

        with patch.object(DocumentParser, '_extract_pdf_text_original', return_value=sufficient_text) as mock_text:
            mock_ocr_parser = Mock()
            mock_ocr_parser.extract_text.return_value = ocr_text

            with patch.object(parser, '_get_ocr_parser', return_value=mock_ocr_parser):
                with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
                    temp_pdf = f.name

                try:
                    result = parser.parse_pdf(temp_pdf)

                    # Should return OCR result (not text extraction)
                    assert result == ocr_text

                    # Text extraction should NOT be called when force_ocr=True
                    mock_text.assert_not_called()

                    # OCR should be called
                    mock_ocr_parser.extract_text.assert_called_once()

                finally:
                    Path(temp_pdf).unlink()

    def test_parse_pdf_ocr_disabled(self):
        """Test that OCR is NOT used when disabled in settings"""
        ocr_settings = PdfOcrSettings(
            enabled=False  # OCR disabled
        )

        parser = DocumentParser(ocr_settings=ocr_settings)

        # Even with insufficient text
        insufficient_text = "Short."

        with patch.object(DocumentParser, '_extract_pdf_text_original', return_value=insufficient_text):
            with patch.object(parser, '_get_ocr_parser') as mock_get_ocr:
                with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
                    temp_pdf = f.name

                try:
                    result = parser.parse_pdf(temp_pdf)

                    # Should return text extraction result (even if insufficient)
                    assert result == insufficient_text

                    # OCR should NOT be used
                    mock_get_ocr.assert_not_called()

                finally:
                    Path(temp_pdf).unlink()

    def test_parse_pdf_ocr_fallback_on_import_error(self):
        """Test fallback to text extraction when OCR dependencies not installed"""
        ocr_settings = PdfOcrSettings(
            enabled=True,
            min_text_length=200
        )

        parser = DocumentParser(ocr_settings=ocr_settings)

        # Insufficient text triggers OCR
        insufficient_text = "Short text."

        with patch.object(DocumentParser, '_extract_pdf_text_original', return_value=insufficient_text):
            # Mock OCR parser to raise ImportError
            mock_ocr_parser = Mock()
            mock_ocr_parser.extract_text.side_effect = ImportError("PaddleOCR not installed")

            with patch.object(parser, '_get_ocr_parser', return_value=mock_ocr_parser):
                with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
                    temp_pdf = f.name

                try:
                    result = parser.parse_pdf(temp_pdf)

                    # Should fallback to text extraction result
                    assert result == insufficient_text

                finally:
                    Path(temp_pdf).unlink()

    def test_parse_pdf_ocr_fallback_on_ocr_failure(self):
        """Test fallback to text extraction when OCR fails"""
        ocr_settings = PdfOcrSettings(
            enabled=True,
            min_text_length=200
        )

        parser = DocumentParser(ocr_settings=ocr_settings)

        # Insufficient text triggers OCR
        insufficient_text = "Short text."

        with patch.object(DocumentParser, '_extract_pdf_text_original', return_value=insufficient_text):
            # Mock OCR parser to raise generic exception
            mock_ocr_parser = Mock()
            mock_ocr_parser.extract_text.side_effect = Exception("OCR processing failed")

            with patch.object(parser, '_get_ocr_parser', return_value=mock_ocr_parser):
                with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
                    temp_pdf = f.name

                try:
                    result = parser.parse_pdf(temp_pdf)

                    # Should fallback to text extraction result
                    assert result == insufficient_text

                finally:
                    Path(temp_pdf).unlink()

    def test_parse_pdf_use_ocr_parameter_override(self):
        """Test that use_ocr parameter can enable/disable OCR"""
        # Test use_ocr=True enables OCR when disabled in settings
        ocr_settings = PdfOcrSettings(
            enabled=False,  # OCR disabled in settings
            min_text_length=200
        )

        parser = DocumentParser(ocr_settings=ocr_settings)

        insufficient_text = "Short."
        ocr_text = "OCR text. " * 20

        # use_ocr=True should enable OCR despite settings
        with patch.object(DocumentParser, '_extract_pdf_text_original', return_value=insufficient_text):
            mock_ocr_parser = Mock()
            mock_ocr_parser.extract_text.return_value = ocr_text

            with patch.object(parser, '_get_ocr_parser', return_value=mock_ocr_parser):
                with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
                    temp_pdf = f.name

                try:
                    result = parser.parse_pdf(temp_pdf, use_ocr=True)

                    # Should use OCR because use_ocr=True
                    assert result == ocr_text
                    assert mock_ocr_parser.extract_text.call_count == 1

                finally:
                    Path(temp_pdf).unlink()

    def test_parse_pdf_empty_text_triggers_ocr(self):
        """Test that empty text extraction triggers OCR"""
        ocr_settings = PdfOcrSettings(
            enabled=True,
            min_text_length=200
        )

        parser = DocumentParser(ocr_settings=ocr_settings)

        # Empty text
        empty_text = ""
        ocr_text = "OCR extracted content. " * 20

        with patch.object(DocumentParser, '_extract_pdf_text_original', return_value=empty_text):
            mock_ocr_parser = Mock()
            mock_ocr_parser.extract_text.return_value = ocr_text

            with patch.object(parser, '_get_ocr_parser', return_value=mock_ocr_parser):
                with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
                    temp_pdf = f.name

                try:
                    result = parser.parse_pdf(temp_pdf)

                    # Should use OCR
                    assert result == ocr_text
                    mock_ocr_parser.extract_text.assert_called_once()

                finally:
                    Path(temp_pdf).unlink()

    def test_parse_pdf_whitespace_only_text_triggers_ocr(self):
        """Test that whitespace-only text triggers OCR"""
        ocr_settings = PdfOcrSettings(
            enabled=True,
            min_text_length=200
        )

        parser = DocumentParser(ocr_settings=ocr_settings)

        # Only whitespace
        whitespace_text = "   \n\n\t  \n  "
        ocr_text = "OCR extracted content. " * 20

        with patch.object(DocumentParser, '_extract_pdf_text_original', return_value=whitespace_text):
            mock_ocr_parser = Mock()
            mock_ocr_parser.extract_text.return_value = ocr_text

            with patch.object(parser, '_get_ocr_parser', return_value=mock_ocr_parser):
                with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
                    temp_pdf = f.name

                try:
                    result = parser.parse_pdf(temp_pdf)

                    # Should use OCR (whitespace doesn't count)
                    assert result == ocr_text
                    mock_ocr_parser.extract_text.assert_called_once()

                finally:
                    Path(temp_pdf).unlink()

    def test_parse_pdf_exactly_at_threshold(self):
        """Test behavior when text length is exactly at threshold"""
        ocr_settings = PdfOcrSettings(
            enabled=True,
            min_text_length=200
        )

        parser = DocumentParser(ocr_settings=ocr_settings)

        # Exactly 200 characters (at threshold)
        threshold_text = "x" * 200

        with patch.object(DocumentParser, '_extract_pdf_text_original', return_value=threshold_text):
            with patch.object(parser, '_get_ocr_parser') as mock_get_ocr:
                with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
                    temp_pdf = f.name

                try:
                    result = parser.parse_pdf(temp_pdf)

                    # At threshold should NOT trigger OCR (>= vs >)
                    assert result == threshold_text
                    mock_get_ocr.assert_not_called()

                finally:
                    Path(temp_pdf).unlink()

    def test_parse_pdf_just_below_threshold(self):
        """Test behavior when text length is just below threshold"""
        ocr_settings = PdfOcrSettings(
            enabled=True,
            min_text_length=200
        )

        parser = DocumentParser(ocr_settings=ocr_settings)

        # 199 characters (just below threshold)
        below_threshold_text = "x" * 199
        ocr_text = "OCR text. " * 30

        with patch.object(DocumentParser, '_extract_pdf_text_original', return_value=below_threshold_text):
            mock_ocr_parser = Mock()
            mock_ocr_parser.extract_text.return_value = ocr_text

            with patch.object(parser, '_get_ocr_parser', return_value=mock_ocr_parser):
                with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
                    temp_pdf = f.name

                try:
                    result = parser.parse_pdf(temp_pdf)

                    # Should trigger OCR
                    assert result == ocr_text
                    mock_ocr_parser.extract_text.assert_called_once()

                finally:
                    Path(temp_pdf).unlink()


class TestDocumentParserOcrSettings:
    """Test OCR settings management in DocumentParser"""

    def test_default_ocr_settings(self):
        """Test that default OCR settings are used when none provided"""
        parser = DocumentParser()

        settings = parser._get_ocr_settings()

        # Should use defaults from PdfOcrSettings
        assert settings.enabled is True
        assert settings.force_ocr is False
        assert settings.min_text_length == 200
        assert settings.engine == "paddleocr"

    def test_custom_ocr_settings(self):
        """Test using custom OCR settings"""
        custom_settings = PdfOcrSettings(
            enabled=True,
            force_ocr=True,
            min_text_length=100,
            engine="tesseract"
        )

        parser = DocumentParser(ocr_settings=custom_settings)

        settings = parser._get_ocr_settings()

        assert settings.enabled is True
        assert settings.force_ocr is True
        assert settings.min_text_length == 100
        assert settings.engine == "tesseract"

    def test_ocr_parser_lazy_initialization(self):
        """Test that OCR parser is only initialized when needed"""
        parser = DocumentParser()

        # Initially None
        assert parser._ocr_parser is None

        # After getting parser
        with patch('app.utils.pdf_ocr_parser.PdfOcrParser') as mock_parser_class:
            mock_instance = Mock()
            mock_parser_class.return_value = mock_instance

            ocr_parser = parser._get_ocr_parser()

            # Should be initialized
            assert ocr_parser is not None
            mock_parser_class.assert_called_once()

            # Second call should reuse same instance
            ocr_parser2 = parser._get_ocr_parser()
            assert ocr_parser2 is ocr_parser
            mock_parser_class.assert_called_once()  # Still only once

    def test_parse_file_with_pdf_ocr_enabled(self):
        """Test parse_file method works with PDF and OCR enabled"""
        ocr_settings = PdfOcrSettings(enabled=True)
        parser = DocumentParser(ocr_settings=ocr_settings)

        sufficient_text = "Resume content. " * 20

        with patch.object(DocumentParser, '_extract_pdf_text_original', return_value=sufficient_text):
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
                temp_pdf = f.name

            try:
                result = parser.parse_file(temp_pdf)

                # Should successfully parse
                assert result == sufficient_text

            finally:
                Path(temp_pdf).unlink()
