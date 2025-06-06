import scrapy
from urllib.parse import quote_plus
# import random
from urllib.parse import urlsplit, urlunsplit

# from scrapy_splash import SplashRequest

from ..utils import KEYWORDS


class LinkedJobsSpider(scrapy.Spider):
    name = "linkedin_jobs"
    allowed_domains = ["linkedin.com", "vn.linkedin.com", "localhost"]
    api_base = 'https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?location=Vietnam&trk=public_jobs_jobs-search-bar_search-submit&start='

    ITEMS_PER_PAGE = 10
    seen_urls = set()

    splash_endpoints = [
        "http://localhost:8050",
        "http://localhost:8051",
        "http://localhost:8052",
        "http://localhost:8053"
    ]


    def strip_query(self, url):
        parts = urlsplit(url)
        return urlunsplit((parts.scheme, parts.netloc, parts.path, '', ''))


    def start_requests(self):
        offset = 0

        for keyword in KEYWORDS:
            keyword_encoded = quote_plus(keyword)
            url = f"{self.api_base}{offset}&keywords={keyword_encoded}"

            yield scrapy.Request(
                url=url,
                callback=self.parse_job,
                meta={
                    'keyword': keyword,
                    'offset': offset
                }
            )

    def parse_job(self, response):
        keyword = response.meta['keyword']
        offset = response.meta['offset']

        jobs = response.css("li")
        num_jobs_returned = len(jobs)
        print("******* Num Jobs Returned *******")
        print(num_jobs_returned)
        print('*****')

        for job in jobs:
            job_url = job.css(".base-card__full-link::attr(href)").get()
            if not job_url:
                continue

            job_url = job_url.strip()
            job_url = self.strip_query(job_url)
            if job_url in self.seen_urls:
                continue

            self.seen_urls.add(job_url)

            job_item = {
                'title': job.css("h3::text").get(default='not-found').strip(),
                'job_url': job_url,
                'date_posted': job.css('time::text').get(default='not-found').strip(),
                'company': job.css('h4 a::text').get(default='not-found').strip(),
                'company_url': job.css('h4 a::attr(href)').get(default='not-found'),
                'location': job.css('.job-search-card__location::text').get(default='not-found').strip()
            }

            # chosen_splash = random.choice(self.splash_endpoints)
            yield scrapy.Request(
                url=job_item['job_url'],
                callback=self.parse_job_detail,
                meta={'item': job_item}
            )

        if num_jobs_returned > 0:
            next_offset = int(offset) + num_jobs_returned
            keyword_encoded = quote_plus(keyword)
            next_url = f"{self.api_base}{next_offset}&keywords={keyword_encoded}"

            yield scrapy.Request(
                url=next_url,
                callback=self.parse_job,
                meta={
                    'keyword': keyword,
                    'offset': next_offset
                }
            )

    def parse_job_detail(self, response):
        item = response.meta['item']

        logo = response.xpath('//*[@id="main-content"]/section[1]/div/section[2]/div/a/img/@src').get()
        if logo is None:
            logo = response.xpath('//*[@id="base-contextual-sign-in-modal"]/div/section/div/div/img/@src').get()
        if logo is None:
            logo = response.xpath('//*[@id="ember34"]/@src').get()

        desc_texts = response.xpath(
            '//*[@id="main-content"]/section[1]/div/div/section[1]/div/div/section/div/descendant::text()').getall()
        level = response.xpath('//*[@id="main-content"]/section[1]/div/div/section[1]/div/ul/li[1]/span/text()').get()
        job_type = response.xpath('//*[@id="main-content"]/section[1]/div/div/section[1]/div/ul/li[2]/span/text()').get()
        if desc_texts is None:
            return


        item['from_site'] = "Linkedin"
        item['company_logo'] = logo
        cleaned_description = [t.strip() for t in desc_texts if t.strip()]
        item['description'] = '\n'.join(cleaned_description)
        if level: item['job_level'] = level.replace('\n', '').strip()
        if job_type: item['job_type'] = job_type.replace('\n', '').strip()

        yield item




