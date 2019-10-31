import os
import csv
import json
 
 
def print_archive_dirs():
    texts_dir = 'archived_texts'
    archived_dirs = os.listdir(texts_dir)
     
    for bank in archived_dirs:
        if bank == '.DS_Store':
            pass
        else:
            bank_dirs = os.listdir(os.path.join(texts_dir, bank))
             
            for year in bank_dirs:
                if year == '.DS_Store':
                    pass
                else:
                    if year == 'live':
                        year_files = os.listdir(os.path.join(texts_dir, bank, year))
                        if len(year_files) > 5:
                            out_dir = os.path.join(texts_dir, bank, year)
                            with open('seen_live.txt', 'a') as fout:
                                fout.write(out_dir.strip() + '\n')
                                print(out_dir)



# function to load in a bank-data json file
# parameter is a filename, returns bank dict of bank
def load_bank_file(filename):
    with open(filename, 'r') as f:
        data = json.load(f)

    return data


def print_banks():
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
            stratified_banks.append(line.split(',')[0].strip())
    
    
        
    bank_deltas = [bank for bank in stratified_banks if bank not in bank_names]
    for bank in bank_deltas:
        print(bank)
    
    print(len(bank_deltas))
    




print_banks()
    
                    