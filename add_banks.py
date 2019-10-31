import requests
from classes import Bank
from classes import Snapshot
import csv
import json
import os
import re
from time import sleep
import random
import html2text
import signal
from contextlib import contextmanager
import concurrent.futures


@contextmanager
def timeout(time):
    # Register a function to raise a TimeoutError on the signal.
    signal.signal(signal.SIGALRM, raise_timeout)
    # Schedule the signal to be sent after ``time``.
    signal.alarm(time)

    try:
        yield
    except TimeoutError:
        pass
    finally:
        # Unregister the signal so it won't be triggered
        # if the timeout is not reached.
        signal.signal(signal.SIGALRM, signal.SIG_IGN)


def raise_timeout(signum, frame):
    raise TimeoutError


# function to load in a bank-data json file
# parameter is a filename, returns bank dict of bank
def load_bank_file(filename):
    with open(filename, 'r') as f:
        data = json.load(f)

    return data


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
    out_dir = 'jsons_new'
    file_name = clean_name(bank.name) + '.json'
    outfile = os.path.join(out_dir, file_name)

    out_dict = {
        'bank name': bank.name,
        'bank root url': bank.root_url,
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
        

def get_bank_deltas():
    new_bank_list = []
    dirname = 'jsons'
    json_files = os.listdir(dirname)
    bank_names = []
    for name in json_files:
        if name == '.DS_Store':
            pass
        else:
            json_file = load_bank_file(os.path.join(dirname, name))
            bank_names.append(json_file['bank name'].replace(',', '').replace('.', '').strip())
          
    stratified_banks = []
    with open('stratified_list.txt', 'r') as fin:
        lines = fin.readlines()
        for line in lines:
            stratified_banks.append([line.split(',')[0].strip(), line.split(',')[1].strip()])
                
    for bank in stratified_banks:
        if bank[0] in bank_names:
            pass
        else:
            new_bank_list.append(Bank(bank[0], bank[1]))


    return new_bank_list


# function to extract the text content from a page.
#  page_body -> text object
def get_page_text(page_body):
    text_maker = html2text.HTML2Text()
    text_maker.ignore_links = True
    text_maker.ignore_images = True
    text_maker.ignore_anchors = True
    text_maker.body_width = 0


    text = text_maker.handle(page_body).lower().replace('#', '').replace('*', '').replace('_', '').replace(' - ', ' ').replace('|', '').replace('(icon)', '').strip()

    return text


def load_new_banks():
    new_banks = []
    json_dir = 'jsons_new'
    jsons = os.listdir(json_dir)
    for json in jsons:
        if json == '.DS_Store':
            pass
        else:
            filepath = os.path.join(json_dir, json)
            new_banks.append(load_bank_file(filepath))
            
    return new_banks


def get_wayback_url_pages(bank):
    holder_dir = 'new_archived_texts'
    try:
        os.mkdir(holder_dir)
    except Exception:
        pass
    bank_dir = bank['bank name'].replace(' ', '_').replace('&', '').replace('__', '_')
    bank_path = os.path.join(holder_dir, bank_dir)
    try:
        os.mkdir(bank_path)
    except Exception:
        pass
    live_dir = 'live'
    live_dir_path = os.path.join(holder_dir, bank_dir, live_dir)
    try:
        os.mkdir(live_dir_path)
    except Exception:
        pass
    
    bank_archives = bank['archives']
    for item in bank_archives:
        if item == '.DS_Store':
            pass
        else:
            year = item['year']
            year_urls = item['urls']
            year_dir = os.path.join(holder_dir, bank_dir, str(year))
            try:
                os.mkdir(year_dir)
            except Exception:
                pass
            
            #session = requests.Session()
            try:
                for url in year_urls:
                    with timeout(15):
                        result = requests.get(url)
                        print('Got: {}'.format(url))
                        page_text = get_page_text(result.text)
                        outfile_name = url.lower().replace('/', '').replace('.', '').replace(':', '')[:250] + '.txt'
                        outfile_path = os.path.join(holder_dir, bank_dir, str(year), outfile_name)
                        with open(outfile_path,'w') as fout:
                            fout.write(page_text)
                            
            except Exception as e:
                print(e)
                
        print()
            
        
        
        
    
    
def main():
    #banks = get_bank_deltas()
    #for bank in banks:
    #   wayback_urls_index(bank)
    # output_json(bank)
  
    new_banks = load_new_banks()
     
     
    holder_dir = 'new_archived_texts'
    try:
        os.mkdir(holder_dir)
    except Exception:
        pass
    
    #for bank in new_banks:
    #    get_wayback_url_pages(bank)
        
    with concurrent.futures.ProcessPoolExecutor(max_workers=None) as executor:
        future_to_file = {executor.submit(get_wayback_url_pages, bank): bank for bank in new_banks}
        

        
    
            
    
    
   
            
            
main()