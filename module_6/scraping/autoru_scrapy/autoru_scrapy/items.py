# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class AutoruScrapyItem(scrapy.Item):
    url = scrapy.Field()
    orig_url = scrapy.Field()
    model_brand = scrapy.Field()
    model = scrapy.Field()
    brand = scrapy.Field()
    generation = scrapy.Field()
    date_posted = scrapy.Field()
    views_stats = scrapy.Field()
    views_total = scrapy.Field()
    views_today = scrapy.Field()
    offer_id = scrapy.Field()
    year = scrapy.Field()
    mileage = scrapy.Field()
    body_type = scrapy.Field()
    color = scrapy.Field()
    fuel_type = scrapy.Field()
    engine = scrapy.Field()
    engine_volume = scrapy.Field()
    engine_power = scrapy.Field()
    transmission = scrapy.Field()
    drive = scrapy.Field()
    wheel = scrapy.Field()
    state = scrapy.Field()
    owners_count = scrapy.Field()
    pts = scrapy.Field()
    customs = scrapy.Field()
    exchange = scrapy.Field()
    vin = scrapy.Field()
    license_plate = scrapy.Field()
    photos_links = scrapy.Field()
    photos_count = scrapy.Field()
    descr = scrapy.Field()
    complectation = scrapy.Field()
    price = scrapy.Field()
    catalog_link = scrapy.Field()