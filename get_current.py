import requests
from bs4 import BeautifulSoup
import os
from classes import Bank
import csv
import tldextract
from time import sleep
import html2text
import browser_cookie3
import random
import signal
from contextlib import contextmanager



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


def current_urls(urls_list, session):
    bad_contents = ['/media/', '/images/', '.css', '.png', '.jpeg', 'jpg', '.gif',
                    '.ashx', '=', '.ico', '%20', '/css/', '.pdf', '/ajax', '.mp4', '.wav', 'facebook', 'twitter',
                    'instagram', 'pinterest', '.mp3', '.mov', 'trustpilot', 'mailto', '.zip', '.tar', '.gz', 'webmaxstaging', '#', '.docx', '.doc', '.xlsx', '.csv' ]

    while len(urls_list[0]) > 0:
        try:
            for url in urls_list[0]:
                if url in urls_list[1]:
                    pass
                else:

                    print(url)
                    urls_list[1].append(url)
                    with timeout(15):
                        r = session.get(url, timeout=5)
                    if not r.status_code == 200:
                        print(r.status_code)
                        urls_list[0].remove(url)
                    else:
                        urls_list[0].remove(url)
    
                        r_text = r.text
                        out_text = get_page_text(r_text)
                        page_name = url.replace('https://', '').replace('http://', '').replace('/', '_').replace('www.', '').replace('.', '-') + '.txt'
                        out_dir = urls_list[3][0]
                        try:
                            os.mkdir(out_dir)
                        except Exception:
                            pass
                        out_path = os.path.join(out_dir, page_name)
                        with open(out_path, 'w') as fout:
                            fout.write(out_text)
    
                        soup = BeautifulSoup(r_text, 'html.parser')
                        for anchor in soup.find_all('a', href=True):
                            link = anchor['href']
    
                            if link.startswith('#'):
                                pass
                            if link.endswith('/'):
                                link = link[:-1]
                            if link.startswith('/'):
                                link = 'https://www.' + urls_list[2][0] + link
    
                            if not urls_list[2][0] in link:
                                pass
                            else:
                                if any(substring in link for substring in bad_contents):
                                    pass
                                else:
                                    link = link.replace('https://', 'http://')
                                    urls_list[0].append(link)
                                    for url in urls_list[0]:
                                        if url in urls_list[1]:
                                            urls_list[0].remove(url)
                                            urls_list[0] = list(set(urls_list[0]))
                                        
            
                
        except Exception as e:
            print(e)

    with open('seen_live.txt', 'a') as fout:
        fout.write(urls_list[3][0] + '\n')

def init():
    session = requests.Session()
    session.headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML like Gecko) Chrome/44.0.2403.155 Safari/537.36',
    }
    proxies = {
        'http' : 'http://38.141.44.186:19001',
        'https' : 'http://38.141.44.186:19001'
    }
    #session.proxies = proxies
    
    cookie = browser_cookie3.chrome()
    session.cookies.update(cookie)
    
    
    
    
    
    f = open('seen_live.txt', 'a')
    f.write('\n')
    f.close()
    
    banks_to_check = [
        'movement mortgage',
        'essex mortgage',
        'chicago mortgage solutions',
        'phh mortgage',
        'vip mortgage inc'
        'gateway mortgage group llc',
        'caliber funding',
        'network funding lp',
        'guardian mortgage company inc',
        'village capital investment',
        'amcap mortgage ltd',
        'ditech financial',
        'envoy mortgage',
        'mortgage network ltd',
        'cendera funding inc',
        'on q financial',
        'iowa bankers mortgage corporat',
        'pennymac loan services',
        'vandyk mortgage corporation',
        'amerihome mortgage',
        'mason mcduffie mortgage corp',
        'united shore financial services',
        'first continential mortgage ltd'
    ]
    
    banks = load_banks()
    
    banks_to_scrape = []
    for bank in banks:
        banks_to_scrape.append(bank)
    
    already_scraped = []
    with open('seen_live.txt', 'r') as fin:
        lines = fin.readlines()
        for line in lines:
            if not line == '\n':
                already_scraped.append(line.replace('\n', ''))
        
    
    
    for bank in banks_to_scrape:
        try:
            url = bank.root_url
            bank_name = bank.name.strip().replace(',', '').replace(' ', '_').replace('.', '').replace('-', '')
            bank_live_folder = os.path.join('archived_texts', bank_name, 'live')
            if bank_live_folder in already_scraped:
                pass
            else:
                print(bank_live_folder)
                with open('seen_live.txt', 'a') as fout:
                    fout.write(bank_live_folder.strip() + '\n')
                urls_list = [[url], [], [], [bank_live_folder]] #[ [current_urls_list], [seen_urls], [current domain], [live folder] ]
                domain = tldextract.extract(url)
                root = '{}.{}'.format(domain[1], domain[2])
                print(root)
                urls_list[2].append(root)
                current_urls(urls_list, session)
                print(len(urls_list[1]))
            
            
        
        except Exception as e:
            print(e)




init()


