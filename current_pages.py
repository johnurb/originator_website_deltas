import requests
import csv
import json
import os
from bs4 import BeautifulSoup
import html2text
import tldextract


total_pages = []
checked_pages = []
suffix = ''

# get all of the local pages from the current version of a live website
def cur_links(url):
    global total_pages
    global checked_pages
    global suffix
    
    if url in checked_pages:
        pass
    
    else:
        try:
            print('Pulling from: {}'.format(url))
                        
            r = requests.get(url, timeout=3)
            if not r.status_code == 200:
                with open('errors.txt', 'a') as f:
                    f.write(url + '\n')
                    
            # save pages
            out_dir = 'cur_txts'
            try:
                os.mkdir(out_dir)
            except Exception:
                pass
            page_text = get_page_text(r.text)
            file_name = url.replace('https://', 'http://').replace('http://', '').replace('www.', '').lower().replace('/', '').replace('.', '') + '.txt'
            with open(os.path.join(out_dir, file_name), 'w') as fout:
                fout.write(str(r.status_code) + '\n')
                fout.write(page_text)
                
            soup = BeautifulSoup(r.text, 'html.parser')
            links = soup.find_all('a', href=True)
        
            proper_links = []
            for link in links:
                if '#' in link['href'] or 'mailto' in link['href']:
                    pass
                else:
                    proper_links.append(link['href'].lower())
                    
                    
            proper_links = list(set(proper_links[:]))
            
            local_links = []
            invalid = ['twitter.com', 'linkedin.com', 'facebook.com', 'instagram.com', 'tel:', 'youtube.com', 'nmlsconsumeraccess.org', 'trustpilot.com',
                       '/media/', '/images/', '.css', '.png', '.jpeg', 'jpg', '.gif', '.ashx', '=', '.ico', '/css/', 'google.com', '.pdf']
            for link in proper_links:
                if any(substring in link for substring in invalid):
                    pass
                else:
                    local_links.append(link)
            
            fixed_local_links = []
            for link in local_links:
                if link.startswith('/'):
                    fixed_local_links.append('www.' + suffix + link)
                elif link.endswith('/'):
                    fixed_local_links.append(link[:-1])
                elif len(link) < 2:
                    pass
                else:
                    fixed_local_links.append(link)
            
            schemaless_links = []
            for link in fixed_local_links:
                schemaless_links.append(link.replace('http://','').replace('https://','').strip())
            
            final_local_links = []
            for link in schemaless_links:
                if link.endswith('/'):
                    pass
                else:
                    final_local_links.append(link)
            
            schema_links = []
            for link in final_local_links:
                schema_links.append('http://' + link)
        
            checked_pages.append(url)
            for link in schema_links:
                if not suffix in link:
                    pass
                else:
                    schema_links.append(cur_links(link))    
            
            return schema_links
        
        except Exception as e:
            checked_pages.append(url)
            cur_links(url)
    
    
def count_init(bank_url):
    global total_pages
    global checked_pages
    global suffix
    
    url = bank_url
    parts = tldextract.extract(url)
    suffix = '.'.join(parts[1:])
    
    cur_links(url)
    
    checked = checked_pages[:]
    del total_pages[:]  
    del checked_pages[:]
    return checked

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
            good_lines.append(line.strip())
    
    text = ' '.join(good_lines)

    return text
    
    




    
    
    
    
    

    
    