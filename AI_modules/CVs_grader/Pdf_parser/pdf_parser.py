import sys
sys.path.insert(1, r"NavigaTech\AI_modules\CVs_grader")

from Extractor.cv_information_extractor import ResumeParser
from Pdf_parser.profile_urls_extractor import PDFUrlExtractor
from pdfminer.high_level import extract_text
from io import BytesIO



class ResumePdfParser:
    def __init__(self):
        self.resume_parser = ResumeParser()

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
        parsed_resume["basic_info"]["github"] = urls["github_url"]
        parsed_resume["basic_info"]["linkedin"] = urls["linkedin_url"]

        return parsed_resume
