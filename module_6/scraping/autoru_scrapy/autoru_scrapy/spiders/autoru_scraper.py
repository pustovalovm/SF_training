import scrapy
import pathlib
import csv
from ..items import AutoruScrapyItem
import re
from scrapy.http import Request


class AutoruScraperSpider(scrapy.Spider):
    name = 'autoru_scraper'

    def __init__(self, links_file='', *args, **kwargs):
        super(AutoruScraperSpider, self).__init__(*args, **kwargs)
        self.start_urls = []
        with open(links_file, 'r') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter='\n')
            for row in csv_reader:
                if '/cars/used/' in row[0]:
                    self.start_urls.append(row[0])
        # limit number of urls for testing purposes
        # self.start_urls = self.start_urls[0:10]

    def parse(self, response):
        item = AutoruScrapyItem()
        item['url'] = response.url
        item['orig_url'] = response.request.url
        item['model_brand'] = (response
                               .xpath('//a[contains(@class, "CardBreadcrumbs__itemText")]/text()')
                               .getall())

        item['date_posted'] = (response
                               .xpath('//div[contains(@title, "Дата размещения")]/text()')
                               .get())

        item['views_stats'] = (response
                               .xpath('//div[contains(@title, "Количество просмотров")]/text()')
                               .get())
        #views_stats = re.findall('[\d.\w ]+', views_stats)

        item['offer_id'] = (response
                            .xpath('//div[contains(@title, "Идентификатор объявления")]/text()')
                            .get())

        item['year'] = response.xpath(
            '//li[contains(@class, "CardInfoRow_year")]/span/a/text()').get()

        item['mileage'] = response.xpath(
            '//li[contains(@class, "CardInfoRow_kmAge")]/span[2]/text()').get()

        item['body_type'] = response.xpath(
            '//li[contains(@class, "CardInfoRow_bodytype")]/span/a/text()').get()

        item['color'] = response.xpath(
            '//li[contains(@class, "CardInfoRow_color")]/span/a/text()').get()

        item['engine'] = response.xpath('//li[contains(@class, "CardInfoRow_engine")]/span//text()').getall()

        item['transmission'] = response.xpath(
            '//li[contains(@class, "CardInfoRow_transmission")]/span[2]/text()').get()

        item['drive'] = response.xpath(
            '//li[contains(@class, "CardInfoRow_drive")]/span[2]/text()').get()

        item['wheel'] = response.xpath(
            '//li[contains(@class, "CardInfoRow_wheel")]/span[2]/text()').get()

        item['state'] = response.xpath(
            '//li[contains(@class, "CardInfoRow_state")]/span[2]/text()').get()

        item['owners_count'] = response.xpath(
            '//li[contains(@class, "CardInfoRow_ownersCount")]/span[2]/text()').get()

        item['pts'] = response.xpath(
            '//li[contains(@class, "CardInfoRow_pts")]/span[2]/text()').get()

        item['customs'] = response.xpath(
            '//li[contains(@class, "CardInfoRow_customs")]/span[2]/text()').get()

        item['exchange'] = response.xpath(
            '//li[contains(@class, "CardInfoRow_exchange")]/span[2]/text()').get()

        item['vin'] = response.xpath(
            '//li[contains(@class, "CardInfoRow CardInfoRow_vin")]/span[2]/text()').get()

        item['license_plate'] = response.xpath(
            '//li[contains(@class, "CardInfoRow_licensePlate")]/span[2]/text()').get()

        item['photos_links'] = (response.xpath(
            '//img[contains(@class, "ImageGalleryDesktop__image")]/@src')
            .extract())

        item['descr'] = response.xpath(
            '//div[contains(@class, "CardDescription__textInner")]/span/text()').extract()

        item['complectation'] = response.xpath(
            '//li[contains(@class, "ComplectationGroups__itemContentEl")]/text()').extract()

        item['price'] = response.xpath(
            '//span[contains(@class, "OfferPriceCaption__price")]/text()').get()
        item['catalog_link'] = response.xpath(
            '//a[contains(@class, "CardCatalogLink")]/@href').get()
            
        yield item
