import scrapy
from urllib.parse import quote_plus
# import random
from urllib.parse import urlsplit, urlunsplit

# from scrapy_splash import SplashRequest

from ..utils import KEYWORDS


class CourseraSpider(scrapy.Spider):
    name = "coursera"
    allowed_domains = ["coursera.org", "localhost"]
    api_base = 'https://www.coursera.org/courses?language=English&page='

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
        page = 1

        for keyword in KEYWORDS:
            keyword_encoded = quote_plus(keyword)
            url = f"{self.api_base}{page}&query={keyword_encoded}"

            yield scrapy.Request(
                url=url,
                callback=self.parse_course,
                meta={
                    'keyword': keyword,
                    'page': page
                }
            )

    def parse_course(self, response):
        keyword = response.meta['keyword']
        page = response.meta['page']

        courses = response.css("#searchResults > div:nth-child(1) > div > ul > li")
        num_courses_returned = len(courses)
        print("******* Num Jobs Returned *******")
        print(num_courses_returned)
        print('*****')

        for course in courses:
            url = course.css("a::attr(href)").get()
            if not url:
                continue

            url = url.strip()
            if not url.startswith("/learn"):
                continue

            url = 'https://www.coursera.org' + url
            url = self.strip_query(url)
            if url in self.seen_urls:
                continue

            self.seen_urls.add(url)

            course_item = {
                'title': course.css("h3::text").get(default='not-found').strip(),
                'url': url,
                'reviews': course.css("div.css-vac8rf::text").get(default='not-found').strip(),
                'organization': course.css("p.cds-ProductCard-partnerNames::text").get(default='').strip(),
                'meta_data': course.css("div.cds-CommonCard-metadata > p::text").get(default='').strip()
            }

            # chosen_splash = random.choice(self.splash_endpoints)
            yield scrapy.Request(
                url=course_item['url'],
                callback=self.parse_course_detail,
                meta={'item': course_item}
            )

        if num_courses_returned > 0:
            next_page = int(page) + 1
            keyword_encoded = quote_plus(keyword)
            next_url = f"{self.api_base}{next_page}&query={keyword_encoded}"

            yield scrapy.Request(
                url=next_url,
                callback=self.parse_course,
                meta={
                    'keyword': keyword,
                    'page': next_page
                }
            )

    def parse_course_detail(self, response):
        item = response.meta['item']

        instructor = response.xpath('//*[@id="rendered-content"]/div/main/section[2]/div/div/div[1]/div[1]/div/div/div[2]/div[2]/div/div[2]/div[1]/p/span/a/span/text()').get(default='not-found').strip()
        enrolled = response.xpath('//*[@id="rendered-content"]/div/main/section[2]/div/div/div[1]/div[1]/div/div/div[2]/div[4]/p/span/strong/span/text()').get(default='not-found').strip()
        rating = response.xpath('//*[@id="rendered-content"]/div/main/section[2]/div/div/div[2]/div[2]/div[1]/div[2]/div/div[1]/text()').get(default='not-found').strip()
        skills = response.css('.css-1l1jvyr a::text').getall()
        what_you_will_learn = response.css('li .css-g2bbpm p span span::text').getall()
        description = response.css('#modules > div > div > div > div:nth-child(1) > div > div > div > div.content > div > p:nth-child(1)::text').get(default='not-found')

        item['from_site'] = "Coursera"
        item['description'] = description
        item['instructor'] = instructor
        item['enrolled'] = enrolled
        item['rating'] = rating
        item['skills'] = skills
        item['what_you_will_learn'] = what_you_will_learn

        yield item




