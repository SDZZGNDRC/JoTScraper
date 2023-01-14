import csv
from functools import cmp_to_key

fieldnames = ['title', 'author', 'Coverdate', 'Volume', 'Issue', 'Pages', 'DOI']

def cmp_pages(a:str, b:str):
    '''
    compare tow pages like 1, 6, 7-9, 15-75
    '''
    A : int = int(a) if not ('-' in a) else (int(a.split('-')[0])+int(a.split('-')[1]))/2
    B : int = int(b) if not ('-' in b) else (int(b.split('-')[0])+int(b.split('-')[1]))/2
    if A < B:
        return True
    else:
        return False
    

def cmp(a:dict, b:dict):
    Volume_a = int(a['Volume'])
    Volume_b = int(b['Volume'])
    Issue_a = int(a['Issue'].strip('()'))
    Issue_b = int(b['Issue'].strip('()'))
    if Volume_a < Volume_b:
        return -1
    elif Volume_a > Volume_b:
        return 1
    elif Issue_a < Issue_b:
        return -1
    elif Issue_a > Issue_b:
        return 1
    elif cmp_pages(a['Pages'],b['Pages']):
        return -1
    else: 
        return 1

if __name__ == '__main__':
    data = []
    with open('results.csv', 'r', encoding='utf-8', newline='') as csvfile:
        csvReader = csv.DictReader(csvfile, fieldnames=fieldnames)
        data = list(csvReader)[1:]
    data = sorted(data, key=cmp_to_key(cmp))
    with open('sorted-results.csv', 'w', encoding='utf-8', newline='') as csvfile:
        csvWriter = csv.DictWriter(csvfile, fieldnames=fieldnames)
        csvWriter.writeheader()
        csvWriter.writerows(data)
    print('Finished...')