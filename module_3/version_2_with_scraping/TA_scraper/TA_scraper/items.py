# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class TaScraperItem(scrapy.Item):
    name = scrapy.Field()
    claimed = scrapy.Field()
    rating = scrapy.Field()
    URL_TA = scrapy.Field()
    ID_TA = scrapy.Field()
    rev_rank = scrapy.Field()
    review_number = scrapy.Field()
    address = scrapy.Field()
    primary_cus = scrapy.Field()
    primary_cus_price = scrapy.Field()
    pricing = scrapy.Field()
    mail = scrapy.Field()
    is_website = scrapy.Field()
    photo_count = scrapy.Field()
    is_video = scrapy.Field()
    tel = scrapy.Field()
    reviews = scrapy.Field()
    review_dates = scrapy.Field()
    review_ratings = scrapy.Field()
    special_diets = scrapy.Field()
    cuisines = scrapy.Field()
    orig_url = scrapy.Field()
    inactive = scrapy.Field()
    rank = scrapy.Field()
    cus_rest_rank = scrapy.Field()
    city_rest_count = scrapy.Field()
    cus_rest_count = scrapy.Field()
    city = scrapy.Field()
    closed = scrapy.Field()
    redirected = scrapy.Field()
    name_changed = scrapy.Field()
