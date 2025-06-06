# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class CourseItem(scrapy.Item):
    from_site = scrapy.Field()
    title = scrapy.Field()
    instructor = scrapy.Field()
    organization = scrapy.Field()
    rating = scrapy.Field()
    reviews = scrapy.Field()
    enrolled = scrapy.Field()
    level = scrapy.Field()
    url = scrapy.Field()
    skills = scrapy.Field()
    what_you_will_learn = scrapy.Field()
    estimated_time = scrapy.Field()
    description = scrapy.Field()

