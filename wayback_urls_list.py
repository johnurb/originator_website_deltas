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
import random
import matplotlib.pyplot as plt; plt.rcdefaults()
import numpy as np
import matplotlib.pyplot as plt
from current_pages import cur_links
from current_pages import count_init
import string
import shutil



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


# function to grab all of the WayBack-archived pages year-over-year for a bank website.
#   outputs all unique archived urls to yearly text files
def wayback_urls_index(bank):
    holder_dir = 'archive'
    bank_dir = bank.name.replace(' ','_').replace('.','').replace(',','')
    url = bank.root_url
    try:
        os.mkdir(os.path.join(holder_dir, bank_dir))
    except Exception:
        pass
    
    years = map(str, [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018])
    # for each desired year pull the archived pages and append into the dictionary of archives for the bank
    # structure the url to pull the archived pages from
    # base_url filtering options remove duplicate urls, unwanted mimetypes, and unsuccessfully requested pages
    for year in years:
        base_url = 'http://web.archive.org/cdx/search/cdx?url={url}&from={year}&to={year}' \
                   '&fl=timestamp,original&filter=statuscode:200' \
                   '&filter=mimetype:text/html&matchType=host&collapse=urlkey'.format(url=url, year=year)
        
        
        
        results = requests.get(base_url).text

        # each result line contains information about an individual archived page
        # go through the lines, pull desired content (ignore url strings containing unwanted substrings)
        lines = results.split('\n')
        bad_contents = ['/media/', '/images/', '.css', '.png', '.jpeg', 'jpg', '.gif',
                        '.ashx', '=', '.ico', '%20', '/css/', '.pdf', '/ajax']
        
        good_lines = []
        for line in lines:
            items = line.split()
            if len(items) == 2 and not any(contents in items[1].lower() for contents in bad_contents):
                if line.endswith('/'):
                    good_lines.append(line[:-1].replace(':80','').replace('/?',''))
                else:
                    good_lines.append(line.replace(':80','').replace('/?',''))
        
        file_name = '{name}_{year}.txt'.format(name = bank.name, year = year)
        
        file_out = os.path.join(holder_dir, bank_dir, file_name)
        with open(file_out, 'w') as fout:
            for line in good_lines:
                fout.write(line.split()[1] + '\n')
                
                
    ###
    # get just Q3 2018
    base_url = 'http://web.archive.org/cdx/search/cdx?url={url}&from={year}&to={year}' \
                   '&fl=timestamp,original&filter=statuscode:200' \
                   '&filter=mimetype:text/html&matchType=host&collapse=urlkey'.format(url=url, year=2018)
    
    results = requests.get(base_url).text

    # each result line contains information about an individual archived page
    # go through the lines, pull desired content (ignore url strings containing unwanted substrings)
    lines = results.split('\n')
    bad_contents = ['/media/', '/images/', '.css', '.png', '.jpeg', 'jpg', '.gif',
                    '.ashx', '=', '.ico', '%20', '/css/', '.pdf', '/ajax']
    
    good_lines = []
    for line in lines:
        items = line.split()
        if len(items) == 2 and not any(contents in items[1].lower() for contents in bad_contents):
            if int(items[0][4:6]) >= 10 and int(items[0][4:6]) <= 12:
                if line.endswith('/'):
                    good_lines.append(line[:-1].replace(':80','').replace('/?',''))
                else:
                    good_lines.append(line.replace(':80','').replace('/?',''))
    
    file_name = '{name}_{year}_q3.txt'.format(name = bank.name, year = year)
        
    file_out = os.path.join(holder_dir, bank_dir, file_name)
    with open(file_out, 'w') as fout:
        for line in good_lines:
            fout.write(line.split()[1] + '\n')
            
        
    


def yearly_deltas(bank):
    holder_dir = 'archive'
    url = bank.root_url
    name = bank.name
    ####
    ####
    # Current live urls
    num_live = count_init(url)
    current_live = len(num_live)
    
    
    ####
    ####
    ####
    
    
    dir = bank.name.replace(' ','_').replace('.','').replace(',','')
    try:
        os.mkdir(holder_dir, dir)
    except Exception:
        pass
    
    yearly_urls = []
    
    items = sorted(os.listdir(os.path.join(holder_dir, dir)))
    for item in items:
        if item == '.DS_Store':
            pass
        else:
            with open(os.path.join(holder_dir, dir, item), 'r') as fin:
                lines = fin.readlines()
                year = []
                for line in lines:
                    year.append(line.strip())
     
            yearly_urls.append(year)
        
    
    graph_years = ('2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018', '2018 Q3', 'Current Live')
    size = [len((yearly_urls)[0]),
            len((yearly_urls)[1]),
            len((yearly_urls)[2]),
            len((yearly_urls)[3]),
            len((yearly_urls)[4]),
            len((yearly_urls)[5]),
            len((yearly_urls)[6]),
            len((yearly_urls)[7]),
            len((yearly_urls)[8]),
            len((yearly_urls)[9]),
            current_live
            ]
    
    sizes = pd.Series(size)
    
    plt.figure()
    
    ax = sizes.plot(kind='bar')
    ax.set_title('{name} archive counts'.format(name=dir))
    ax.set_xlabel('Year')
    ax.set_ylabel('Size (# of of Archived URLs)')
    ax.set_xticklabels(graph_years)
    
    rects = ax.patches
    rects[-1].set_color('r')

    # Make some labels.
    labels = [len((yearly_urls)[0]),
            len((yearly_urls)[1]),
            len((yearly_urls)[2]),
            len((yearly_urls)[3]),
            len((yearly_urls)[4]),
            len((yearly_urls)[5]),
            len((yearly_urls)[6]),
            len((yearly_urls)[7]),
            len((yearly_urls)[8]),
            len((yearly_urls)[9]),
            current_live
            ]
    
    for rect, label in zip(rects, labels):
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width() / 2, height , label, ha='center', va='bottom')
     
    
    
    
    plt.tight_layout()
    file_name = '{dir} Page Counts.pdf'.format(dir=dir)
    outfile = os.path.join(holder_dir, dir, file_name)
    plt.savefig(outfile, bbox_inches='tight')
        
    

def main():
    banks = load_banks()
    holder_dir = 'archive'
    try:
        os.mkdir(holder_dir)
    except Exception:
        pass
    
    try:
        with open('checked.txt', 'r') as fin:
            lines = fin.readlines()
    except Exception:
        lines = []
    
    
    for bank in banks:
        try:
            out_dir = 'cur_txts'
            try:
                os.mkdir(out_dir)
            except Exception:
                pass
                
        
            bank_dir = bank.name.replace(' ','_').replace('.','').replace(',','')
            url = bank.root_url
            try:
                os.mkdir(os.path.join(holder_dir, bank_dir))
            except Exception:
                pass
                    
            current_info = current_counts(url)
                    
            bank_cur_txt = 'live_pages'
                    
            shutil.copytree('cur_txts', os.path.join(holder_dir, bank_dir, bank_cur_txt))
            sleep(1)
            shutil.rmtree('cur_txts')
                    
            with open(os.path.join(holder_dir, bank_dir, 'counts.txt'), 'w') as fout:
                fout.write('Total Pages: {}\n'.format(current_info[0]))
                fout.write('Total Words: {}\n'.format(current_info[1]))
                    
            with open('checked.txt', 'a') as fout:
                fout.write(bank.name + '\n')
                    
            print()
            print()
        
        except Exception as e:
            print(e)
        
        
        
        
    
    
    
    
    # for bank in banks:
    #     try:
    #         wayback_urls_index(bank)
    #         yearly_deltas(bank)
    #         print()
    #     
    #     except Exception as e:
    #          print('Error on {bank}'.format(bank = bank.name))
    #          print(e)
    #          with open('errors.txt', 'a') as fout:
    #              fout.write(bank.name + '\n')
                
    
    
    
    # for i, bank in enumerate(banks):
    #     if bank.name == 'american internet mortgage':
    #         index = i
    # 
    # test_bank = banks[index]
    # 
    # wayback_urls_index(test_bank)
    # 
    # yearly_deltas(test_bank.root_url)
    
#main()



def current_counts(url):
    url = url
    num_live = len(count_init(url))
    
    total_words = 0
    for item in os.listdir('cur_txts'):
        name = os.path.join('cur_txts', item)
        with open(name, 'r') as f:
            lines = f.readlines()
            for line in lines:
                line = line.replace('—', '-')
                line = line.translate(str.maketrans('', '', string.punctuation))
                words = line.split()
                
                total_words += len(words)
    
    
    return [num_live, total_words]
                
    
    
main()