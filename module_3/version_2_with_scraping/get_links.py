#%%
import requests
import sys
import xml.etree.ElementTree as ET
import gzip
import csv
import os
from tempfile import TemporaryDirectory 
from pathlib import Path
import argparse
from progress.bar import IncrementalBar
from collections import Counter
import re


def get_links (output='./review_links.csv',
              sitemap_link='https://www.tripadvisor.com/sitemap/2/' +
              'en_US/sitemap_en_US_index.xml', 
              ):
    """
    This function extracts sitemap from the sitemap_link in xml format,
    parses the file and finds all links to restaurant review lists which
    are stored also in gzipped xml files. It downloads the files to temp 
    folder, unzips them, parses for links to reviwes and writes to 
    (output_file).csv file.
    Automatically cleans up all downloaded files and temp folder.

    Args:
        output (str, optional): output file path
            Defaults to './review_links.csv'
        sitemap_link (str, optional): TA sitemap link
            Defaults to 'https://www.tripadvisor.com/sitemap/2/en_US/sitemap_en_US_index.xml'
    """
    temp_fold = TemporaryDirectory()
    temp_path = Path(temp_fold.name)
    r = requests.get(sitemap_link)
    text = r.content.decode()
    sitemap_tree = ET.ElementTree(ET.fromstringlist(text))
    sitemap_root = sitemap_tree.getroot()
    links_to_gz = []
# parse xml to get links to restraurant review xml file links
    i = 0
    for element in sitemap_root:
        if 'restaurant_' in element[0].text:
            links_to_gz.append(element[0].text)
            i += 1
    print(f'Found {i} link lists as gzipped xml files.')
# download xmls with review to temp_path
    with IncrementalBar('Downloading', max=i) as bar:
        i = 0
        for link in links_to_gz:
            tempfile = temp_path / link.split('/')[-1]
            if not tempfile.is_file():
                r = requests.get(link, allow_redirects=True)
                with tempfile.open('wb') as file:
                    file.write(r.content)
            bar.next()
            i += 1
    print(f'Downloaded {i} restaurant list gzipped xml files',
          f'to folder {str(temp_path)}')
# unzip
    with IncrementalBar('Unzipping', max=i) as bar:
        i = 0
        for gz in temp_path.iterdir():
            gz = gz.resolve()
            if gz.suffix == '.gz':
                with gzip.open(gz) as archive:
                    with open(gz.parent / gz.stem, 'wb') as output_file:
                        output_file.write(archive.read())
                gz.unlink()
                bar.next()
            i += 1
    print(f'Unzipped {i} xml files.')
# parse xmls to find review links and append them to big list           
    review_list = []
    with IncrementalBar('Parsing xml files', max=len(list(temp_path.iterdir()))) as bar:
        for f in temp_path.iterdir():
            review_counter = 0
            review_tree = ET.parse(f)
            root_review = review_tree.getroot()
            for record in review_tree.findall('{*}url'):
                review_list.append(record[0].text)
                review_counter += 1
            bar.next()
    review_list = list(map(lambda x: [x], review_list))
    print(f'Totally {len(review_list)} links were extracted.')
# write this list to csv
    output_path = Path(output).resolve()
    with output_path.open('w+', newline='') as f:
        wr = csv.writer(f)
        wr.writerows(review_list)
    print(f'Output written to file {str(output_path)}')
# cleanup temp folder
    temp_fold.cleanup()

    return str(output_path)

def filter_reviews_by_city(links_file, top_city_count):
    """
    THe function filters reviews for top "top_city_count" number of cities by restraunt count.

    Args:
        links_list (list): list with all links
        top_city_count (int): number of top cities to take into accoung
    """ 
    full_list = []
    links_path = Path(links_file).resolve()
    with open(links_path, 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            full_list.append(row[0])
    city_count = Counter(map(lambda x: re.search('g\d+', x)[0], full_list))
    if top_city_count == 0:
        top_city_count = city_count
    top_city_ids = [x[0] for x in city_count.most_common(top_city_count)]
    print(f'Restaurant counts for top {top_city_count} cities:')
    rev_count = 0
    for id_ in top_city_ids:
        print (f'{id_}: {city_count[id_]}')
        rev_count += city_count[id_]
    print(f'Total number of reviews: {rev_count}')
    filtered_links = [[x] for x in full_list if re.search('g\d+', x)[0] in top_city_ids]
    filtered_path = links_path.parent / f'links_top_{top_city_count}.csv'
    with filtered_path.open('w+', newline='') as csv_file:
        wr = csv.writer(csv_file)
        wr.writerows(filtered_links)
        print(f'Saved filtered links to file {csv_file.name}')
    return str(Path(csv_file.name).absolute())


def start_scraping(input_path):
    """
    This function starts scraper with default parameters.
    Args:
        output_path (str): path to input file with links
    """
    print('Scraping started. Very time consuming.')
    os.chdir('./TA_scraper')
    os.system(f'scrapy crawl -a links_file={input_path} ' +
                f' -o ../dataset.csv -L ERROR TA_scraper')

def get_yesno(attempts, question):
    yes = ['yes', 'y', 'ye']
    no = ['no', 'n']
    i = 0
    while i < attempts:
        answer = input(f'{question} [y/n] \n ')
        if answer in yes:
            return True
        elif answer in no:
            return False
        else:
            print(f'Incorrect input, try again. Exiting after {4-i} attempts.')
    else:
        print('Sorry, could not recognize Your input.')
        return None

if __name__ == '__main__':
#   parse command line arguments
    argparser = argparse.ArgumentParser(
        description='Get the restaurant review ' +
        'links from Tripadvisor and write them to csv file')
    argparser.add_argument(
        'output_file', metavar='O', type=str,
        default='./review_links.csv', nargs='?',
        help='output file path (default: ./review_links.csv')
    argparser.add_argument(
        'sitemap_link', nargs='?', metavar='L',
        default='https://www.tripadvisor.com/sitemap/2/en_US/sitemap_en_US_index.xml',
        help='link to TA sitemap\n' +
        'default: https://www.tripadvisor.com/sitemap/2/en_US/sitemap_en_US_index.xml')
    args = argparser.parse_args()
    starter = input('Enter 1 to search for links on TA sitemap.\n' +
                    'Enter 2 to use already existing links file.\n' +
                    'Enter anything else to exit.\n')
    if starter == '1':
        print(f'Extraction started.\n' +
            f'Sitemap link: {args.sitemap_link}\n' +
            f'Output file: {os.path.abspath(args.output_file)}\n')
        output_path = get_links(args.output_file, args.sitemap_link)
    if starter == '2':
        output_path = input('Paste links file path.\n')
    flag = True
    while flag:
        count = input('Enter number of cities to filter from' + 
                      ' top by restaurant count or 0 for all: ')
        try:
            if count == 'e':
                flag = False
                print('Defaulted to 10')
                count = 10
            else:
                count = int(count)
            flag = False
        except ValueError:
            print('Incorrect input, try again or enter "e" to exit.')
    links_file = filter_reviews_by_city(output_path, count)
    print('\nRun the following commands in the project directory to ' +
          'start scraping Tripadvisor:\n \n' +
          'cd ./TA_scraper\n' +
          f'scrapy crawl -a links_file={links_file}' +
          f'-o ../dataset.csv -L ERROR TA_scraper\n \n' +
          'Specify dataset location in command as path if needed.',
          )
    answer = get_yesno(4, 'Start scraping with default parameters?')
    if  answer == True:
        start_scraping(output_path)
    elif answer == False:
        sys.exit
    else: 
        print('Sorry, could not recognize Your input.')
        sys.exit()