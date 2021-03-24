# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import re
import datetime


class DefaultValuesPipeline(object):
    def process_iIem(self, item, spider):
        for field in item.fields:
            item.setdefault(field, None)
        return item


class AutoruScrapyPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        # model_brand
        if adapter['orig_url'] != adapter['url']:
            print(
                f"Detected redirect from {adapter['orig_url']}",
                f"to {adapter['url']}")
        if adapter['model_brand'] is None:
            print(f"Could not download data from {adapter['url']}")
            return item
        model_brand = adapter['model_brand'][0::2]
        try:
            adapter['brand'] = model_brand[0]
        except IndexError:
            adapter['brand'] = adapter['model_brand']
        try:
            adapter['model'] = model_brand[1]
            adapter['generation'] = model_brand[2]
        except IndexError:
            pass
        # date_posted
        months = {
            'января': 1,
            'февраля': 2,
            'марта': 3,
            'апреля': 4,
            'мая': 5,
            'июня': 6,
            'июля': 7,
            'августа': 8,
            'сентября': 9,
            'октября': 10,
            'ноября': 11,
            'декабря': 12
        }
        # date_posted = adapter['date_posted'].lower().split()
        # adapter['date_posted'] = datetime.date(
        #     int(date_posted[-1]),
        #     months[date_posted[1]],
        #     int([date_posted[2]]))
        # views
        if adapter['views_stats']:
            adapter['views_total'] = int(
                re.findall('\d+', adapter['views_stats'])[0])
            try:
                adapter['views_today'] = re.findall(
                    '\d+',
                    adapter['views_stats'])[1]
            except IndexError:
                adapter['views_today'] = 0
        # id
        if adapter['offer_id']:
            adapter['offer_id'] = adapter['offer_id'].split()[-1]
        # year
        if adapter['year']:
            try:
                adapter['year'] = int(adapter['year'])
            except ValueError or TypeError:
                pass
        # mileage
        try:
            adapter['mileage'] = int(adapter['mileage']
                                     .encode('ascii', 'ignore')
                                     .decode('utf-8'))
        except Exception:
            pass
        # body type
        if adapter['body_type']:
            adapter['body_type'] = str(adapter['body_type']).lower()
        # color
        if adapter['color']:
            adapter['color'] = str(adapter['color']).lower()
        # fuel
        if adapter['engine']:
            if len(adapter['engine']) > 1:
                if 'Электро' in adapter['engine'][1]:
                    adapter['fuel_type'] = 'Электро'
                    adapter['engine_volume'] = 0
                    power = str(adapter['engine'][1]).split(' / ')[0]
                    adapter['engine_power'] = float(
                        power.encode('ascii', 'ignore')
                        .decode('utf-8')
                        .strip('.'))
                else: 
                    adapter['fuel_type'] = adapter['engine'][-1]
                    volume = str(adapter['engine'][1]).split(' / ')[0]
                    adapter['engine_volume'] = float(
                        volume.encode('ascii', 'ignore')
                        .decode('utf-8'))
                    power = str(adapter['engine'][1]).split(' / ')[1]
                    adapter['engine_power'] = float(
                        power.encode('ascii', 'ignore')
                        .decode('utf-8')
                        .strip('.'))
        # owners count
        if adapter['owners_count']:
            try:
                if '1' in adapter['owners_count']:
                    adapter['owners_count'] = 1
                elif '2' in adapter['owners_count']:
                    adapter['owners_count'] = 2
                else:
                    adapter['owners_count'] = 3
            except TypeError:
                pass
        # photos count
        try:
            adapter['photos_count'] = len(adapter['photos_links'])
        except TypeError:
            adapter['photos_count'] = None
        try:
            adapter['price'] = int(adapter['price']
                                   .encode('ascii', 'ignore')
                                   .decode('utf-8'))
        except Exception:
            pass
        try:
            adapter['catalog_link'] = adapter['catalog_link'].split('/?')[0]
        except Exception:
            pass
        return item
