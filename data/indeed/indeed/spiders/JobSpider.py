import scrapy
from urllib.parse import quote_plus
import re
import json
# import random
from urllib.parse import urlsplit, urlunsplit

# from scrapy_splash import SplashRequest

from ..utils import KEYWORDS


class IndeedJobsSpider(scrapy.Spider):
    name = "indeed_jobs"
    allowed_domains = ["indeed.com", "jobs.vn.indeed.com", "localhost"]
    api_base = 'https://jobs.vn.indeed.com/jobs?l=Vi%E1%BB%87t+Nam&start='

    ITEMS_PER_PAGE = 10
    seen_urls = set()

    splash_endpoints = [
        "http://localhost:8050",
        "http://localhost:8051",
        "http://localhost:8052",
        "http://localhost:8053"
    ]


    def start_requests(self):
        offset = 0

        for keyword in KEYWORDS:
            keyword_encoded = quote_plus(keyword)
            url = f"{self.api_base}{offset}&q={keyword_encoded}"

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

        script_tag = re.findall(r'window.mosaic.providerData\["mosaic-provider-jobcards"\]=(\{.+?\});', response.text)
        if script_tag is None:
            return

        json_blob = json.loads(script_tag[0])
        jobs_list = json_blob['metaData']['mosaicProviderJobCardsModel']['results']
        num_jobs_returned = len(jobs_list)

        print("******* Num Jobs Returned *******")
        print(num_jobs_returned)
        print('*****')

        for index, job in enumerate(jobs_list):
            jobKey = job.get('jobKey')
            if not jobKey:
                continue

            job_url = f"https://jobs.vn.indeed.com/viewjob?jk={jobKey}"
            job_url = job_url.strip()
            if job_url in self.seen_urls:
                continue

            self.seen_urls.add(job_url)

            job_item = {
                'company': job.get('company'),
                'job_url': job_url,
                'title': job.get('title'),
                'location': job.get('jobLocationCity'),
                'date_posted': job.get('pubDate'),
            }

            yield scrapy.Request(
                url=job_item['job_url'],
                callback=self.parse_job_detail,
                meta={'item': job_item}
            )

        # jobs = response.css("#mosaic-provider-jobcards > ul > li")
        # num_jobs_returned = len(jobs)
        # print("******* Num Jobs Returned *******")
        # print(num_jobs_returned)
        # print('*****')
        #
        # for job in jobs:
        #     job_id = job.css("#mosaic-provider-jobcards > ul > li h2 a::attr(data-jk)").get()
        #
        #     if not job_id:
        #         continue
        #
        #     job_url = f"https://jobs.vn.indeed.com/viewjob?jk={job_id}"
        #     job_url = job_url.strip()
        #     if job_url in self.seen_urls:
        #         continue
        #
        #     self.seen_urls.add(job_url)
        #
        #     job_item = {
        #         'title': job.css("h2::text").get(default='not-found').strip(),
        #         'job_url': job_url
        #     }
        #
        #     # chosen_splash = random.choice(self.splash_endpoints)
        #     yield scrapy.Request(
        #         url=job_item['job_url'],
        #         callback=self.parse_job_detail,
        #         meta={'item': job_item}
        #     )

        if num_jobs_returned > 0 and offset < 5:
            next_offset = int(offset) + self.ITEMS_PER_PAGE
            keyword_encoded = quote_plus(keyword)
            next_url = f"{self.api_base}{next_offset}&q={keyword_encoded}"

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

        script_tag = re.findall(r"_initialData=(\{.+?\});", response.text)
        if script_tag is None:
            return

        json_blob = json.loads(script_tag[0])
        item['from_site'] = "Indeed"
        item['description'] = json_blob["jobInfoWrapperModel"]["jobInfoModel"]['sanitizedJobDescription']
        item['job_type'] = None
        item['job_level'] = None

        yield item


        # logo = response.xpath('//*[@id="main-content"]/section[1]/div/section[2]/div/a/img/@src').get()
        # if logo is None:
        #     logo = response.xpath('//*[@id="base-contextual-sign-in-modal"]/div/section/div/div/img/@src').get()
        # if logo is None:
        #     logo = response.xpath('//*[@id="ember34"]/@src').get()
        #
        # desc_texts = response.xpath(
        #     '//*[@id="main-content"]/section[1]/div/div/section[1]/div/div/section/div/descendant::text()').getall()
        # level = response.xpath('//*[@id="main-content"]/section[1]/div/div/section[1]/div/ul/li[1]/span/text()').get()
        # job_type = response.xpath('//*[@id="main-content"]/section[1]/div/div/section[1]/div/ul/li[2]/span/text()').get()
        # if desc_texts is None:
        #     return
        #
        #
        # item['company'] = response.xpath('//*[@id="viewJobSSRRoot"]/div[2]/div[3]/div/div/div[1]/div[2]/div[1]/div[2]/div/div/div/div[1]/div/span/text()').get().strip()
        # item['location'] = response.xpath('//*[@id="jobLocationText"]/div/span/text()').get().strip()
        #
        #
        # item['from_site'] = "Linkedin"
        # item['company_logo'] = logo
        # cleaned_description = [t.strip() for t in desc_texts if t.strip()]
        # item['description'] = '\n'.join(cleaned_description)
        # if level: item['job_level'] = level.replace('\n', '').strip()
        # if job_type: item['job_type'] = job_type.replace('\n', '').strip()
        #
        # yield item




