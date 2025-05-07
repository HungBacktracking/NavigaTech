from pdfminer.high_level import extract_text

from app.pdfparser.cv_information_extractor import ResumeParser
from app.pdfparser.profile_urls_extractor import PDFUrlExtractor


class ResumePdfParser:
    def __init__(self, resume_parser: ResumeParser):
        self.resume_parser = resume_parser

    def read_pdf(self, pdf_file):
        """Method to parse PDF into text."""
        try:

            pdf_file.seek(0)
            text = extract_text(pdf_file)
            return text
        except Exception as e:
            print(f"Error reading PDF: {e}")
            return ""

    def parse(self, pdf_file):
        """
        1. Parse text from the resume PDF.
        2. Extract profile URLs.
        3. Parse resume information.
        """
        pdf_file.seek(0)
        url_extractor = PDFUrlExtractor(pdf_file)
        pdf_file.seek(0)
        resume_text = self.read_pdf(pdf_file)

        urls = url_extractor.extract_profile_urls()
        parsed_resume = self.resume_parser.parse(resume_text=resume_text)
        parsed_resume["github_url"] = urls["github_url"]
        parsed_resume["linkedin_url"] = urls["linkedin_url"]

        return parsed_resume
