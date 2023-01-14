import scrapy

class JoTSpider(scrapy.Spider):
    name = 'JoTSpider'
    
    def start_requests(self):
        urls = [
            'https://jot.pm-research.com/content/by/year/2005',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)
    
    def parse(self, response):
        if 'by/year' in response.url:
            return self.parse_1(response)
        else:
            return self.parse_2(response)
    
    def parse_1(self, response):
        '''
        Used to parse the pages like https://jot.pm-research.com/content/by/year/2005 
        in which has a substr 'by/year'.
        '''
        # Find all issues in this page
        issues = response.css('.single-issue')
        for i, issue in enumerate(issues):
            issue_url = issue.css('.hw-issue-meta-data::attr(href)').get()
            if issue_url is not None:
                issue_url = response.urljoin(issue_url)
            else: 
                raise Exception(f'No.{i} issue has no url in {response.url}')
            yield scrapy.Request(issue_url, callback=self.parse)
        
        # Jump to the next page
        nextpage = response.css('#block-system-main .link-icon-right::attr(href)').get()
        if nextpage is not None:
            nextpage = response.urljoin(nextpage)
            yield scrapy.Request(nextpage, callback=self.parse)
            
        
    
    def parse_2(self, response):
        '''
        Used to parse the pages like https://jot.pm-research.com/content/13/4 
        in which hasn't a substr 'by/year'.
        '''
        papers = response.css('.highwire-citation-iij-list-complete')
        # Get titles 
        titles = []
        for i, paper in enumerate(papers):
            temp = paper.css('.highwire-cite-title::text, strong::text, em::text').getall()
            title = ''.join([ i for i in temp if i != '\n']).strip('\n')
            if title is not None:
                titles.append(title)
            else:
                raise Exception(f'No.{i} paper has no title in {response.url}')
        # Get authors
        authors = []
        for i, paper in enumerate(papers):
            author = paper.css('.highwire-citation-author::text').getall()
            if len(author) > 1:
                author_s = ' and '.join([','.join(author[:-1]), author[-1]])
            elif len(author) == 1:
                author_s = author[0]
            else:
                raise Exception(f'No.{i} paper has no author in {response.url}')
            authors.append(author_s)
        # Get DOIs
        DOIs = []
        for i, paper in enumerate(papers):
            DOI : str = paper.css('.highwire-cite-metadata-doi::text').get()
            if DOI is not None:
                DOI = DOI.strip()[5:]
                DOIs.append(DOI)
            else:
                raise Exception(f'No.{i} paper has no DOI in {response.url}')
        # Get Coverdates
        Coverdates = []
        for i, paper in enumerate(papers):
            Coverdate : str = paper.css('.highwire-cite-metadata-coverdate::text').get()
            if Coverdate is not None:
                # Coverdate = Coverdate[:Coverdate.index(', ')] if ', ' in Coverdate else Coverdate
                Coverdates.append(Coverdate.strip(', '))
            else:
                raise Exception(f'No.{i} paper has no DOI in {response.url}')
        # Get Volumes
        Volumes = []
        for i, paper in enumerate(papers):
            Volume : str = paper.css('.highwire-cite-metadata-volume::text').get()
            if Volume is not None:
                Volumes.append(Volume.strip(' '))
            else:
                raise Exception(f'No.{i} paper has no Volume in {response.url}')                
        # Get Issues
        Issues = []
        for i, paper in enumerate(papers):
            Issue : str = paper.css('.highwire-cite-metadata-issue::text').get()
            if Issue is not None:
                Issues.append(Issue.strip(' '))
            else:
                raise Exception(f'No.{i} paper has no Issue in {response.url}')                
        # Get Pages
        Pages = []
        for i, paper in enumerate(papers):
            Page : str = paper.css('.highwire-cite-metadata-pages::text').get()
            if Page is not None:
                Pages.append(Page.strip(' '))
            else:
                raise Exception(f'No.{i} paper has no DOI in {response.url}')
        
        # make them up
        for i in range(len(papers)):
            yield {
                'title': titles[i],
                'author': authors[i],
                'Coverdate': Coverdates[i],
                'Volume': Volumes[i],
                'Issue': Issues[i],
                'Pages': Pages[i],
                'DOI': DOIs[i],
            }
        
