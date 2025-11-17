"""Tests for document parser utility"""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from app.utils.document_parser import (
    DocumentParser,
    DocumentParseError,
    parse_resume,
    parse_resume_bytes,
    is_supported_format
)


class TestDocumentParserFormatSupport:
    """Tests for format support detection"""

    def test_is_supported_pdf(self):
        """Test PDF format is supported"""
        assert DocumentParser.is_supported("resume.pdf") is True
        assert DocumentParser.is_supported(Path("resume.pdf")) is True

    def test_is_supported_docx(self):
        """Test DOCX format is supported"""
        assert DocumentParser.is_supported("resume.docx") is True
        assert DocumentParser.is_supported(Path("resume.docx")) is True

    def test_is_supported_txt(self):
        """Test TXT format is supported"""
        assert DocumentParser.is_supported("resume.txt") is True

    def test_is_supported_md(self):
        """Test MD format is supported"""
        assert DocumentParser.is_supported("resume.md") is True

    def test_is_not_supported_doc(self):
        """Test DOC format is not supported (legacy)"""
        assert DocumentParser.is_supported("resume.doc") is False

    def test_is_not_supported_html(self):
        """Test HTML format is not supported"""
        assert DocumentParser.is_supported("resume.html") is False

    def test_is_not_supported_rtf(self):
        """Test RTF format is not supported"""
        assert DocumentParser.is_supported("resume.rtf") is False

    def test_is_supported_case_insensitive(self):
        """Test format detection is case-insensitive"""
        assert DocumentParser.is_supported("resume.PDF") is True
        assert DocumentParser.is_supported("resume.DOCX") is True
        assert DocumentParser.is_supported("resume.TXT") is True

    def test_convenience_function_is_supported_format(self):
        """Test convenience function is_supported_format"""
        assert is_supported_format("resume.pdf") is True
        assert is_supported_format("resume.doc") is False


class TestDocumentParserTextFiles:
    """Tests for text file parsing"""

    def test_parse_text_utf8(self, tmp_path):
        """Test parsing UTF-8 text file"""
        text_file = tmp_path / "resume.txt"
        content = "这是一份中文简历\n包含多行内容"
        text_file.write_text(content, encoding='utf-8')

        parser = DocumentParser()
        result = parser.parse_text(text_file)

        assert result == content

    def test_parse_markdown(self, tmp_path):
        """Test parsing Markdown file"""
        md_file = tmp_path / "resume.md"
        content = "# Resume\n\n## Education\n- University of Example"
        md_file.write_text(content, encoding='utf-8')

        parser = DocumentParser()
        result = parser.parse_text(md_file)

        assert result == content

    def test_parse_text_with_special_characters(self, tmp_path):
        """Test parsing text with special characters"""
        text_file = tmp_path / "resume.txt"
        content = "姓名：张三\n技能：Python、Java、C++\n邮箱：example@test.com"
        text_file.write_text(content, encoding='utf-8')

        parser = DocumentParser()
        result = parser.parse_text(text_file)

        assert "张三" in result
        assert "Python" in result

    @patch('chardet.detect')
    def test_parse_text_with_encoding_detection(self, mock_detect, tmp_path):
        """Test parsing with encoding detection fallback"""
        text_file = tmp_path / "resume.txt"
        content = "Resume content"

        # Write as UTF-8 but simulate detection needed
        text_file.write_bytes(content.encode('utf-8'))

        # Mock chardet to return GBK
        mock_detect.return_value = {'encoding': 'gbk', 'confidence': 0.85}

        parser = DocumentParser()

        # Should try UTF-8 first (which works), so chardet won't be called
        result = parser.parse_text(text_file)
        assert "Resume content" in result


class TestDocumentParserPDF:
    """Tests for PDF parsing"""

    @patch('pypdf.PdfReader')
    def test_parse_pdf_success(self, mock_pdf_reader):
        """Test successful PDF parsing"""
        # Mock PDF reader
        mock_page1 = Mock()
        mock_page1.extract_text.return_value = "Page 1 content\nWith some text"

        mock_page2 = Mock()
        mock_page2.extract_text.return_value = "Page 2 content\nMore text"

        mock_reader = Mock()
        mock_reader.pages = [mock_page1, mock_page2]

        mock_pdf_reader.return_value = mock_reader

        parser = DocumentParser()
        parser._lazy_imports_done = True  # Skip import check

        result = parser.parse_pdf("test.pdf")

        assert "Page 1 content" in result
        assert "Page 2 content" in result
        assert "\n\n" in result  # Pages separated

    @patch('pypdf.PdfReader')
    def test_parse_pdf_empty(self, mock_pdf_reader):
        """Test parsing empty PDF raises error"""
        mock_page = Mock()
        mock_page.extract_text.return_value = "   "  # Only whitespace

        mock_reader = Mock()
        mock_reader.pages = [mock_page]

        mock_pdf_reader.return_value = mock_reader

        parser = DocumentParser()
        parser._lazy_imports_done = True

        with pytest.raises(DocumentParseError, match="No text could be extracted"):
            parser.parse_pdf("test.pdf")

    @patch('pypdf.PdfReader')
    def test_parse_pdf_page_extraction_error(self, mock_pdf_reader):
        """Test PDF parsing handles page extraction errors"""
        mock_page1 = Mock()
        mock_page1.extract_text.side_effect = Exception("Extraction failed")

        mock_page2 = Mock()
        mock_page2.extract_text.return_value = "Page 2 content"

        mock_reader = Mock()
        mock_reader.pages = [mock_page1, mock_page2]

        mock_pdf_reader.return_value = mock_reader

        parser = DocumentParser()
        parser._lazy_imports_done = True

        # Should skip page 1, get page 2
        result = parser.parse_pdf("test.pdf")
        assert "Page 2 content" in result


class TestDocumentParserDOCX:
    """Tests for DOCX parsing"""

    @patch('docx.Document')
    def test_parse_docx_success(self, mock_document):
        """Test successful DOCX parsing"""
        # Mock paragraphs
        mock_para1 = Mock()
        mock_para1.text = "Paragraph 1"

        mock_para2 = Mock()
        mock_para2.text = "Paragraph 2"

        # Mock document
        mock_doc = Mock()
        mock_doc.paragraphs = [mock_para1, mock_para2]
        mock_doc.tables = []

        mock_document.return_value = mock_doc

        parser = DocumentParser()
        parser._lazy_imports_done = True

        result = parser.parse_docx("test.docx")

        assert "Paragraph 1" in result
        assert "Paragraph 2" in result

    @patch('docx.Document')
    def test_parse_docx_with_tables(self, mock_document):
        """Test DOCX parsing includes table content"""
        # Mock paragraph
        mock_para = Mock()
        mock_para.text = "Before table"

        # Mock table
        mock_cell1 = Mock()
        mock_cell1.text = "Cell 1"

        mock_cell2 = Mock()
        mock_cell2.text = "Cell 2"

        mock_row = Mock()
        mock_row.cells = [mock_cell1, mock_cell2]

        mock_table = Mock()
        mock_table.rows = [mock_row]

        mock_doc = Mock()
        mock_doc.paragraphs = [mock_para]
        mock_doc.tables = [mock_table]

        mock_document.return_value = mock_doc

        parser = DocumentParser()
        parser._lazy_imports_done = True

        result = parser.parse_docx("test.docx")

        assert "Before table" in result
        assert "Cell 1" in result
        assert "Cell 2" in result

    @patch('docx.Document')
    def test_parse_docx_empty(self, mock_document):
        """Test parsing empty DOCX raises error"""
        mock_doc = Mock()
        mock_doc.paragraphs = []
        mock_doc.tables = []

        mock_document.return_value = mock_doc

        parser = DocumentParser()
        parser._lazy_imports_done = True

        with pytest.raises(DocumentParseError, match="No text could be extracted"):
            parser.parse_docx("test.docx")


class TestDocumentParserMain:
    """Tests for main parse_file method"""

    def test_parse_file_not_found(self):
        """Test parsing non-existent file raises error"""
        parser = DocumentParser()

        with pytest.raises(DocumentParseError, match="File not found"):
            parser.parse_file("/nonexistent/file.pdf")

    def test_parse_file_unsupported_format(self, tmp_path):
        """Test parsing unsupported format raises error"""
        html_file = tmp_path / "resume.html"
        html_file.write_text("<html>Resume</html>")

        parser = DocumentParser()

        with pytest.raises(DocumentParseError, match="Unsupported file format"):
            parser.parse_file(html_file)

    def test_parse_file_routes_to_text_parser(self, tmp_path):
        """Test parse_file routes .txt to text parser"""
        text_file = tmp_path / "resume.txt"
        text_file.write_text("Resume content")

        parser = DocumentParser()
        result = parser.parse_file(text_file)

        assert result == "Resume content"


class TestDocumentParserBytes:
    """Tests for parsing from bytes"""

    @patch('pypdf.PdfReader')
    def test_parse_bytes_pdf(self, mock_pdf_reader):
        """Test parsing PDF from bytes"""
        mock_page = Mock()
        mock_page.extract_text.return_value = "PDF content"

        mock_reader = Mock()
        mock_reader.pages = [mock_page]

        mock_pdf_reader.return_value = mock_reader

        parser = DocumentParser()
        parser._lazy_imports_done = True

        result = parser.parse_bytes(b"fake pdf bytes", "resume.pdf")

        assert "PDF content" in result

    @patch('docx.Document')
    def test_parse_bytes_docx(self, mock_document):
        """Test parsing DOCX from bytes"""
        mock_para = Mock()
        mock_para.text = "DOCX content"

        mock_doc = Mock()
        mock_doc.paragraphs = [mock_para]
        mock_doc.tables = []

        mock_document.return_value = mock_doc

        parser = DocumentParser()
        parser._lazy_imports_done = True

        result = parser.parse_bytes(b"fake docx bytes", "resume.docx")

        assert "DOCX content" in result

    def test_parse_bytes_text_utf8(self):
        """Test parsing text from bytes"""
        content = "Resume text content"
        file_bytes = content.encode('utf-8')

        parser = DocumentParser()
        result = parser.parse_bytes(file_bytes, "resume.txt")

        assert result == content

    def test_parse_bytes_unsupported_format(self):
        """Test parsing unsupported format from bytes raises error"""
        parser = DocumentParser()

        with pytest.raises(DocumentParseError, match="Unsupported file format"):
            parser.parse_bytes(b"content", "resume.html")


class TestConvenienceFunctions:
    """Tests for convenience functions"""

    def test_parse_resume_function(self, tmp_path):
        """Test parse_resume convenience function"""
        text_file = tmp_path / "resume.txt"
        text_file.write_text("Resume content")

        result = parse_resume(text_file)
        assert result == "Resume content"

    @patch('app.utils.document_parser.document_parser.parse_bytes')
    def test_parse_resume_bytes_function(self, mock_parse_bytes):
        """Test parse_resume_bytes convenience function"""
        mock_parse_bytes.return_value = "Parsed content"

        result = parse_resume_bytes(b"bytes", "resume.pdf")

        assert result == "Parsed content"
        mock_parse_bytes.assert_called_once_with(b"bytes", "resume.pdf")
