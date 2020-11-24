import scrapy
from ..items import TaScraperItem
import re
import csv
from scrapy.http import Request


class TASpider(scrapy.Spider):
    name = 'TA_scraper'

    def __init__(self, links_file='', *args, **kwargs):
        super(TASpider, self).__init__(*args, **kwargs)
        self.start_urls = []
        with open(links_file, 'r') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                self.start_urls.append(row[0])
        self.start_urls = self.start_urls

    def parse(self, response):
        item = TaScraperItem()
        item['name'] = response.xpath("//h1[contains(@data-test-target,'top-info-header')]/text()").extract()
        item['redirected'] = response.request.meta.get('redirect_urls')
        item['claimed'] = response.xpath("//div[contains(@data-test-target,'restaurant-detail-info')]/div/div/div/div/div/text()").extract()
        item['rating'] = response.xpath("//svg[contains(@aria-label,'bubbles')]/@aria-label").get()
        item['rev_rank'] = response.xpath("//*[@class = 'ui_columns']/div[1]/descendant-or-self::text()").extract()
        item['address'] = response.xpath("//a[contains(@href,'MAPVIEW')]/text()").get()
        item['primary_cus_price'] = response.xpath("//div[contains(@data-test-target,'restaurant-detail-info')]/div[2]/span[3]/descendant::*/text()").extract()
        item['URL_TA'] = response.url
        item['orig_url'] = response.request.url
        item['tel'] = response.xpath("//a[contains(@href,'tel:')]/text()").get()
        item['mail'] = response.xpath("//a[contains(@href, 'mailto')]/@href").get()
        item['is_website'] = response.xpath("//a[contains(text(), 'Website')]/@data-encoded-url").get()
        item['cuisines'] = response.xpath("//div[contains(text(),'CUISINES')]/following-sibling::div/text()").get()
        item['special_diets'] = response.xpath("//div[contains(text(),'Special Diets')]/following-sibling::div/text()").get()
        item['photo_count'] = response.xpath("//span[contains(@class, 'see_all_count')]/span/text()").get()
        item['is_video'] = response.xpath("//*[contains(local-name(), 'video')]").get()
        item['reviews'] = response.xpath("//p[contains(@class,'partial_entry')]/text()").getall()
        item['review_dates'] = response.xpath("//span[contains(@class,'ratingDate')]/text()").getall()
        item['review_ratings'] = response.xpath("//span[contains(@alt,'of')]/@alt").extract()
        yield item
