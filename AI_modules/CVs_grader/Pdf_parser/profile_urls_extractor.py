import fitz
from urllib.parse import urlparse


class PDFUrlExtractor:
    def __init__(self, pdf_file):
        """
        Accepts a file-like object, such as a Flask `FileStorage` object.
        """
        self.pdf_file = pdf_file

    def extract_urls(self):
        """Extract all URLs from the PDF."""
        urls = []
        self.pdf_file.seek(0)  # Ensure the stream is at the beginning
        with fitz.open(stream=self.pdf_file.read(), filetype="pdf") as doc:
            for page in doc:
                for link in page.get_links():
                    uri = link.get('uri')
                    if uri:
                        urls.append(uri)
        return urls

    def is_profile_url(self, url):
        """Check if the URL is a profile link."""
        parsed = urlparse(url)
        netloc = parsed.netloc.lower()
        path_parts = parsed.path.strip('/').split('/')

        # Check LinkedIn Profile
        if "linkedin.com" in netloc:
            return len(path_parts) == 2 and path_parts[0] == "in"

        # Check GitHub Profile
        if "github.com" in netloc:
            return len(path_parts) == 1

        return False

    def filter_profile_urls(self, urls):
        """Return only profile URLs."""
        return [url for url in urls if self.is_profile_url(url)]

    def extract_profile_urls(self):
        """Extract and return profile URLs."""
        urls = self.extract_urls()
        profile_urls = self.filter_profile_urls(urls)

        all_urls = {
            "github_url": "",
            "linkedin_url": ""
        }

        for url in profile_urls:
            if "github.com" in url:
                all_urls["github_url"] = url
            elif "linkedin.com" in url:
                all_urls["linkedin_url"] = url

        return all_urls
