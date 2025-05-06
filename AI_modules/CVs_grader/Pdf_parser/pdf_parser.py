import sys
sys.path.insert(1, r"NavigaTech\AI_modules\CVs_grader")

from pdfminer.high_level import extract_text
from Pdf_parser.profile_urls_extractor import PDFUrlExtractor
from Extractor.cv_information_extractor import ResumeParser



class ResumePdfParser:
    def __init__(self):
        # self.pdf_path = pdf_path
        self.resume_parser = ResumeParser()

    def read_pdf(self, pdf_path):
        """Method to parse pdf into text"""
        text = extract_text(pdf_path)
        return text

    def parse(self, pdf_path):
        """
        1. Get parse text from resume pdf
        2. Get profile URLs in resume
        3. Get parse resume information 
        """
        url_extractor = PDFUrlExtractor(pdf_path)
        resume_text = self.read_pdf(pdf_path)
        urls = url_extractor.extract_profile_urls()
        parsed_resume = self.resume_parser.parse(resume_text=resume_text)
        parsed_resume["basic_info"]["github"] = urls["github_url"]
        parsed_resume["basic_info"]["linkedin"] = urls["linkedin_url"]
        return parsed_resume
