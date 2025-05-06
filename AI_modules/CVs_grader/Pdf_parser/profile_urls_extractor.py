import fitz
from urllib.parse import urlparse


class PDFUrlExtractor:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path

    def extract_urls(self):
        """Extract all URLs from the PDF."""
        urls = []
        with fitz.open(self.pdf_path) as doc:
            for page in doc:
                for link in page.get_links():
                    uri = link.get('uri')
                    if uri:
                        urls.append(uri)
        return urls

    def is_profile_url(self, url):
        """Check if the URL is a true profile link (not a repo or paper)."""
        parsed = urlparse(url)
        netloc = parsed.netloc.lower()
        path_parts = parsed.path.strip('/').split('/')

        if "linkedin.com" in netloc:
            return len(path_parts) == 2 and path_parts[0] == "in"

        if "github.com" in netloc:
            return len(path_parts) == 1

        return False

    def filter_profile_urls(self, urls):
        """Return only profile URLs from a given list of URLs."""
        return list({url for url in urls if self.is_profile_url(url)})

    def extract_profile_urls(self):
        """Extract and return only profile URLs from the PDF."""
        urls = self.extract_urls()
        profile_urls = self.filter_profile_urls(urls)

        all_urls = {
            "github_url": "",
            "linkedin_url": ""
        }
        if (len(profile_urls) >= 2):
            if ("github" in urls[0]):
                all_urls["github_url"] = urls[0]
                all_urls["linkedin_url"] = urls[1]
            else:
                all_urls["github_url"] = urls[1]
                all_urls["linkedin_url"] = urls[0]
        elif (len(profile_urls) == 1):
            if ("github" in urls[0]):
                all_urls["github_url"] = urls[0]
                all_urls["linkedin_url"] = ""
            else:
                all_urls["github_url"] = ""
                all_urls["linkedin_url"] = urls[0]
        else:
            all_urls["github_url"] = ""
            all_urls["linkedin_url"] = ""

        return all_urls
