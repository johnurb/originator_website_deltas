#######
# John Urbine - jon.urbine@gmail.com - 2019
#
# program to extract pages/page information from full sitemaps of a website, year-over-year.
# pulling data from years 2010 - 2018
#
#######

import requests
from classes import Bank
from classes import Snapshot
import csv
import json
import os
#from bs4 import BeautifulSoup
import html2text
import re
from time import sleep
import pandas as pd
import numpy as np
from FogCalc import get_fog


# function to cleanup the name of a bank for use as an output filename
# parameter is a bank name string, returns bank name string (cleaned)
def clean_name(name):
    rebuilt = ''
    chars = list(name)
    for char in chars:
        if char.isalpha() or char == ' ':
            rebuilt += char

    rebuilt = rebuilt.replace(' ', '_')

    return rebuilt


# function to load in a bank-data json file
# parameter is a filename, returns bank dict of bank
def load_bank_file(filename):
    with open(filename, 'r') as f:
        data = json.load(f)

    return data


# function to extract the text content from a page.
#  page_body -> text object
def get_page_text(page_body):
    text_maker = html2text.HTML2Text()
    text_maker.ignore_links = True
    text_maker.ignore_images = True
    text_maker.ignore_anchors = True
    text_maker.body_width = 0


    text = text_maker.handle(page_body).lower().replace('#', '').replace('*', '').replace('_', '').replace(' - ', ' ').replace('|', '').replace('(icon)', '').strip()
    with open('temp.txt', 'w') as f:
        f.write(text)
    
    with open('temp.txt', 'r') as f:
        lines = f.readlines()
        
    os.remove('temp.txt')
    
    good_lines = []
    for line in lines:
        if line.strip() == '':
            pass
        else:
            good_lines.append(line.lstrip())
    
    text = ' '.join(good_lines)

    #words = text.split()

    #fixed_words = ' '.join(words)

    return text


# function to process a bank-data file
# parameter is a dict of bank data, returns....->
def process_data(bank_data):
    bank_name = bank_data['bank name']
    archives = bank_data['archives']

    # create an output folder for all text files, the specific bank
    text_file_folder = 'texts'
    if not os.path.exists(text_file_folder):
        os.mkdir(text_file_folder)

    bank_folder = clean_name(bank_name)
    out_folder = os.path.join(text_file_folder, bank_folder)
    if not os.path.exists(out_folder):
        os.mkdir(out_folder)

    # iterate over each year
    for item in archives:
        year = str(item['year'])
        year_urls = item['urls']

        site_structure = {
            0: []
        }

        # determine the number of levels (depth of website urls) for the website for current year
        max_level = 0
        for url in year_urls:
            less_prefix = url.split('_/http://')[1]
            spliced = less_prefix.split('/')

            if spliced[1] == '':
                pass
            else:
                level = len(spliced) - 1
                if level > max_level:
                    max_level = level

        # create appropriate dictionary structure for current 
        for i in range(max_level):
                site_structure[i] = []

        # create output folder for specific year's text files
        year_folder = year
        output_folder = os.path.join(out_folder, year_folder)
        if not os.path.exists(output_folder):
            os.mkdir(output_folder)

        # iterate over each url and process into the dictionary for output to final csv
        # create corresponding text files and output to file folder
        for url in year_urls:
            less_prefix = url.split('_/http://')[1]
            spliced = less_prefix.split('/')

            level = 0
            if spliced[1] == '':
                file_name = 'root.txt'
                outfile = os.path.join(output_folder, file_name)
                r = requests.get(url).text
                page_contents = get_page_text(r)
                with open(outfile, 'w') as f:
                    f.write(page_contents)
                
                page_words = len(page_contents.split())

                url_data = [url, 'root', file_name, page_words]
                site_structure[level].append(url_data)
            else:
                spliced.pop(0)
                level = len(spliced) - 1

                joiner = '/'
                relative_url = joiner.join(spliced)

                joiner = '_'
                file_name = joiner.join(spliced).lower().strip() + '.txt'
                file_name = file_name.replace('_.txt', '.txt').replace('?', '').replace('.html', '')
                outfile = os.path.join(output_folder, file_name)
                r = requests.get(url).text
                page_contents = get_page_text(r)
                with open(outfile, 'w') as f:
                    f.write(page_contents)
                
                page_words = len(page_contents.split())

                url_data = [url, relative_url, file_name, page_words]
                site_structure[level].append(url_data)

        out_fold = 'structures'
        try:
            os.mkdir(out_fold)
        except Exception:

            pass
            
        struct_name = year + '_' + bank_name.replace(' ', '_').replace(',', '').replace('.', '') + '.json'
        with open(os.path.join(out_fold, struct_name), 'w') as f:
            json.dump(site_structure, f)
            print('Output JSON')

# function to load in a list of banks and their associated urls. ie: 'AmeriSave Mortgage' : 'http://www.amerisave.com'
# no parameters, returns a dictionary of banks and urls: {'AmeriSave Mortgage' : 'http://www.amerisave.com'}
def load_banks():
    file_name = 'banks_data.csv'

    # open spreadsheet holding banks and their urls
    # for each bank in the sheet append to a list the bank name and its root url ['name', 'url']
    with open(file_name, 'r') as f:
        reader = csv.reader(f)
        data = []
        for row in reader:
            data.append([row[0], row[1]])

    # create a list of Bank objects
    list_banks = []
    for item in data:
        bank = Bank(item[0].strip(), item[1].strip())
        list_banks.append(bank)

    list_banks.pop(0)
    return list_banks


# function to grab all of the WayBack-archived pages year-over-year for a bank website
# parameter is a Bank object, no returns, Bank object is modified in memory
def wayback_urls_index(bank):
    years = map(str, [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018])

    # for each desired year pull the archived pages and append into the dictionary of archives for the bank
    # structure the url to pull the archived pages from
    # base_url filtering options remove duplicate urls, unwanted mimetypes, and unsuccessfully requested pages
    url = bank.root_url
    for year in years:
        base_url = 'http://web.archive.org/cdx/search/cdx?url={url}&from={year}&to={year}' \
                   '&fl=timestamp,original&filter=statuscode:200' \
                   '&filter=mimetype:text/html&matchType=host&collapse=urlkey'.format(url=url, year=year)
        results = requests.get(base_url).text

        # each result line contains information about an individual archived page
        # go through the lines, pull desired content (ignore url strings containing unwanted substrings)
        lines = results.split('\n')
        bad_contents = ['/media/', '/images/', '.css', '.png', '.jpeg', 'jpg', '.gif',
                        '.ashx', '=', '.ico', '%20', '/css/']
        for line in lines:
            items = line.split()
            if len(items) == 2 and not any(contents in items[1].lower() for contents in bad_contents):
                snap = Snapshot(items[0], items[1].replace(':80', '').replace('https', 'http'))
                bank.snapshots[year].append(snap['snapshot_url'])

        print('Pulled {year} archived urls for {name}'.format(year=year, name=bank.name))

# output bank objects
def output_json(bank):
    out_dir = 'jsons'
    file_name = clean_name(bank.name) + '.json'
    outfile = os.path.join(out_dir, file_name)

    out_dict = {
        'bank name': bank.name,
        'archives': [
            {
                'year': 2010,
                'urls': bank.snapshots['2010']
            },
            {
                'year': 2011,
                'urls': bank.snapshots['2011']
            },
            {
                'year': 2012,
                'urls': bank.snapshots['2012']
            },
            {
                'year': 2013,
                'urls': bank.snapshots['2013']
            },
            {
                'year': 2014,
                'urls': bank.snapshots['2014']
            },
            {
                'year': 2015,
                'urls': bank.snapshots['2015']
            },
            {
                'year': 2016,
                'urls': bank.snapshots['2016']
            },
            {
                'year': 2017,
                'urls': bank.snapshots['2017']
            },
            {
                'year': 2018,
                'urls': bank.snapshots['2018']
            },
        ]

    }

    with open(outfile, 'w') as f:
        json.dump(out_dict, f)
        print('Output JSON')


# base execution
def main():
    dir_name = 'jsons'
    all_files = os.listdir(dir_name)
    for item in all_files:
        infile = os.path.join(dir_name, item)
    
        data = load_bank_file(infile)
        process_data(data)


def format_test():
    file_name = 'structure.json'
    file_out_name = 'LoanDepot_2018.csv'
    with open(os.path.join(file_name), 'r') as fin:
        data = json.load(fin)
    
    levels = []
    for key, value in data.items():
        levels.append([data[key]])
    
    num_levels = len(levels)
    columns = [i for i in range(1, num_levels+1)]
    fixed_cols = []
    for item in columns:
        fixed_cols.append('Level {}'.format(item))
    
    df = pd.DataFrame(dict([ (k,pd.Series(v)) for k,v in data.items() ]))
    df.columns = [fixed_cols]
    df.to_csv(file_out_name, index=False)


def fog_test():
    print(get_fog())

#main()
#format_test()
fog_test()



