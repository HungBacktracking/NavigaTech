# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class JobItem(scrapy.Item):
    from_site = scrapy.Field()
    job_url = scrapy.Field()
    title = scrapy.Field()
    company = scrapy.Field()
    company_logo = scrapy.Field()
    job_type = scrapy.Field()
    job_level = scrapy.Field()
    location = scrapy.Field()
    date_posted = scrapy.Field()
    description = scrapy.Field()
