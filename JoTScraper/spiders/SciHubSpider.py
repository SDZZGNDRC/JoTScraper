import scrapy
import csv
import logging

class SciHubSpider(scrapy.Spider):
    name = 'SciHubSpider'
    csvDOIs = './sorted-results.csv'
    save_path = './papers/'
    scrapy.utils.log.configure_logging(install_root_handler=False)
    logging.basicConfig(
        filename='log.txt',
        format='%(levelname)s: %(message)s',
        level=logging.INFO
    )
    
    def start_requests(self):
        datas = []
        SciHubDomain = 'https://sci-hub.se/'
        with open('sorted-results.csv', 'r', encoding='utf-8', newline='') as csvfile:
            csvReader = csv.DictReader(csvfile)
            datas = list(csvReader)
        for data in datas:
            yield scrapy.Request(
                url=SciHubDomain+data['DOI'], 
                callback=self.parse,
                meta={'name': '. '.join([ # Specify th name of the paper.
                    data['title'] if len(data['title'])<=100 else data['title'][:100],
                    data['author'] if len(data['title'])<=65 else data['title'][:65],
                    data['Coverdate'],
                    data['Volume'],
                    data['Issue'],
                    data['Pages'],
                ]), 'DOI':data['DOI']}
            )
    
    def parse(self, response):
        if self.checkRespones(response):
            return self.parse_1(response)
        else:
            return self.parse_2(response)
    
    def parse_1(self, response):
        '''
        parse the response which find the specified paper, 
        get its download link.
        '''
        hrefLink = response.css('button::attr(onclick)').re('href=(.*)')[0].strip('\'')
        if hrefLink[0] == '/':
            downloadLink : str = response.urljoin(hrefLink)
        else:
            downloadLink : str = 'https:'+ hrefLink
        yield scrapy.Request(
            downloadLink,
            callback=self.parse_3,
            meta=response.meta
        )
    
    def parse_2(self, response):
        '''
        parse the response which not find the specified paper.
        '''
        name = response.meta['name']
        DOI = response.meta['DOI']
        logging.info(f'Could not find the specified paper {name}, DOI:{DOI}')
    
    def parse_3(self, response):
        '''
        Download the paper.
        '''
        path : str = response.meta['name']+'.pdf'
        # the characters below can not exist in a path name
        path = path.replace('\\','')
        path = path.replace('/','')
        path = path.replace(':','')
        path = path.replace('*','')
        path = path.replace('?','')
        path = path.replace('<','')
        path = path.replace('>','')
        path = path.replace('|','')
        path = self.save_path+path
        with open(path, 'wb') as f:
            f.write(response.body)
        logging.info('Saving PDF %s', path)
        
    
    def checkRespones(self, response):
        '''
        Determine whether the query is successful according the response
        '''
        if 'article not found' in response.css('head title::text').get():
            return False # Failed to find the specified paper.
        elif 'Sci-Hub' in response.css('head title::text').get():
            return True # Succeed to find the specified paper.
        else:
            raise Exception(f'the response is not expected: {response.text}')
        
        
        
