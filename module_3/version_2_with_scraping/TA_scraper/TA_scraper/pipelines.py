# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import re


class DefaultValuesPipeline(object):

    def process_item(self, item, spider):
        for field in item.fields:
            item.setdefault(field, None)
        return item


class NoneChecksPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if adapter['name'] is None:
            adapter['name'] = 'No name'
        adapter['review_number'] = 0
        return item

class TaScraperPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        #check if was redirected - means inactive
        if item['redirected'] is None:
            adapter['inactive'] = 0
            adapter['name_changed'] = 0
        else:
            adapter['URL_TA'] = adapter['redirected'][0]
            if re.search('-d\d+-', adapter['orig_url']) is None:
                adapter['inactive'] = 1
                adapter['name_changed'] = 0
                adapter['ID_TA'] = re.search('-d\d+-', adapter['URL_TA'])[0][1:-1] 
            else:
                adapter['inactive'] = 0
                adapter['name_changed'] = 1
        if adapter['inactive'] == 0:
            #check CLosed in name
            if len(adapter['name']) > 1:
                if 'CLOSED' in adapter['name'][1]:
                    adapter['closed'] = 1
                else: 
                    adapter['closed'] = 0
            elif len(adapter['name']) == 1:
                adapter['name'] = adapter['name'][0]
                adapter['closed'] = 0
            else: adapter['name'] = None
            #ID_TA
            adapter['ID_TA'] = re.search('-d\d+-', adapter['URL_TA'])[0][1:-1] 
            #claimed
            if len(adapter['claimed']) > 1:
                if adapter['claimed'][1] == 'Claimed':
                    adapter['claimed'] = 1
                elif adapter['claimed'][1] == 'Unclaimed':
                    adapter['claimed'] = 0
                else: adapter['claimed'] = None
            else: adapter['claimed'] = None
            #primary cuisine and price
            if len(adapter['primary_cus_price']) > 0:
                if re.search('\$', adapter['primary_cus_price'][0]) is not None:
                    adapter['pricing'] = adapter['primary_cus_price'][0]
                    if len(adapter['primary_cus_price']) > 1:
                        adapter['primary_cus'] = adapter['primary_cus_price'][1]
                    else: adapter['primary_cus'] = 'Unknown'
                else: 
                    adapter['primary_cus'] = adapter['primary_cus_price'][0]
                    adapter['pricing'] = None
            else: 
                adapter['primary_cus'] = 'Unknown'
                adapter['pricing'] = None
            #is_video
            if adapter['is_video'] is None:
                adapter['is_video'] = 0
            else: adapter['is_video'] = 1
            #rating
            if adapter['rating'] is not None:
                rating = re.search('(\d.\d|\d)', adapter['rating'])
                if rating is not None:
                    adapter['rating'] = rating[0]
            #rev_rank
            i = 0
            while i<len(adapter['rev_rank']):
                if re.search('\d+ rev',adapter['rev_rank'][i]) is not None:
                    adapter['review_number'] = re.search('\d+ rev',adapter['rev_rank'][i])[0][0:-4]
                elif re.search('\#', adapter['rev_rank'][i]) is not None:
                    string = ' '.join(adapter['rev_rank'][i:i+3])
                    string = string.replace(',','')
                    if adapter['primary_cus'] in string:
                        adapter['cus_rest_rank'] = re.findall('\d+', string)[0]
                        adapter['cus_rest_count'] = re.findall('\d+', string)[1]
                        #adapter['city'] = string[re.search(' in ', string).span()[1]:]
                    elif 'Restaurant' in string:
                        adapter['rank'] = re.search('\d+', string)[0]
                        adapter['city_rest_count'] = re.findall('\d+', string)[1]
                    city = re.search(' in ', string)
                    if city is not None:
                        adapter['city'] = string[city.span()[1]:]
                i += 1
            del adapter['rev_rank']
            #mail
            if adapter['mail'] is not None:
                    adapter['mail'] = 1
            else: adapter['mail'] = 0
            #photo_count
            if adapter['photo_count'] is None:
                adapter['photo_count'] = 0
            else:
                count = re.search('\(\d+\)', re.sub(',', '', adapter['photo_count']))
                if count is not None:
                    adapter['photo_count'] = count[0][1:-1]
                else: adapter['photo_count'] = 0
            #is_website
            if adapter['is_website'] is None:
                adapter['is_website'] = 0
            else: adapter['is_website'] = 1

            #review_ratings
            adapter['review_ratings'] = \
                [re.search('(\d.\d|\d)', x)[0] for x in adapter['review_ratings']]
            #review_dates
            adapter['review_dates'] = \
                [(re.sub('Reviewed ', '', x)) for x in adapter['review_dates']]
        return item

        