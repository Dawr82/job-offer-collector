import logging
import sys
import json

import scrapy_splash
import scrapy

sys.path.append('..\..')

from config import settings, sns
from scraper.scraper import items


class BaseJobOfferSpider(scrapy.Spider):

    """Abstract class for job offer spiders."""

    content_link_selector = ""
    next_page_selector = ""

    request_class = scrapy.Request
    parse_method = "content"
    page_count = 0
    url = ""


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.check()
        self.set_logging()


    @classmethod
    def check(cls):
        if not all([cls.content_link_selector, cls.next_page_selector, cls.url]):
            raise ValueError(f"{cls.__name__}: class attributes need to be defined in child classes!")


    @classmethod
    def set_logging(cls):
        try:
            formatter = logging.Formatter("[%(asctime)s] %(message)s", settings.CRAWLER_LOG_DATETIME_FORMAT)
            handler = logging.FileHandler(settings.CRAWLER_LOG_FILE, settings.CRAWLER_LOG_MODE)
            handler.setFormatter(formatter)
            handler.setLevel(logging.INFO)
            cls.logger = logging.getLogger("crawler")
            cls.logger.setLevel(logging.INFO)
            cls.logger.addHandler(handler)
        except Exception as error:
            print(error)
    

    def start_requests(self):
        yield self.request_class(url=self.url, callback=self.parse, meta={'proxy': sns.PROXY})


    def parse_header(self, offer_header):
        raise NotImplementedError("parse_header callable not defined")


    def parse_content(self, offer_content):
        raise NotImplementedError("parse_content callable not defined")


    def parse(self, response):
        content_links = response.css(self.content_link_selector)
        
        if self.parse_method == 'content':
            method = self.parse_content
        elif self.parse_method == 'header':
            method = self.parse_header
        else:
            raise ValueError("Unsupported type of parse method")

        for content_link in content_links:
            yield self.request_class(response.urljoin(content_link.get()), callback=method)
        
        self.page_count += 1   
        next_page = response.css(self.next_page_selector).attrib["href"]
        if next_page is not None and self.page_count < settings.MAX_PAGES:
            next_page = response.urljoin(next_page)
            yield self.request_class(next_page, callback=self.parse)


class NFJJobOfferSpider(BaseJobOfferSpider):

    name = "nfj"

    next_page_selector = "a[aria-label=Next]"
    content_link_selector = "div.list-container a.posting-list-item::attr(href)"
    url = sns.SCRAPED_URLS[name]

    request_class = scrapy_splash.SplashRequest


    def parse_header(self, offer):
        loader = items.NFJOfferHeaderLoader(item=items.JobOfferHeader(), selector=offer)
        try:
            loader.add_css('position', 'h3.posting-title__position::text')
            loader.add_css('company', 'span.d-block.posting-title__company::text')
            loader.add_css('salary', 'span.salary::text')
            loader.add_css('locations', 'span.posting-info__location::text')
            loader.add_css('locations', 'span.posting-info__location [class]::text')
        except Exception as error:
            self.logger.error(f"{type(error).__name__}: {error} URL -> {offer.url}")
        return loader.load_item()
     

    def parse_content(self, offer_content):
        loader = items.NFJOfferContentLoader(item=items.JobOfferContent(), selector=offer_content)
        try:
            loader.add_css('position', 'div.row.mb-3 [id=posting-header] h1::text')
            loader.add_css('category', 'div.row.mb-3 span.font-weight-semi-bold::text')
            loader.add_css('seniority', 'div.row.mb-3 [id=posting-seniority] span::text')
            loader.add_css('company', 'div.row.mb-3 [id=postingCompanyUrl]::text')
            loader.add_css('salary', 'div.row.mb-3 div.salary h4::text')
            loader.add_css('required', 'div [id=posting-requirements] [class=d-block] h3.mb-0 button::text')
            loader.add_css('required', 'div [id=posting-requirements] [class=d-block] h3.mb-0 a::text')
            loader.add_css('optional', 'div [id=posting-requirements] [id=posting-nice-to-have] h3.mb-0 button::text')
            loader.add_css('optional', 'div [id=posting-requirements] [id=posting-nice-to-have] h3.mb-0 a::text')
            loader.add_css('remote', 'div.row.mb-3 [maticon=home]')
            loader.add_css('locations', 'div.row.mb-3 [popoverplacement=bottom] span::text')
            item = loader.load_item()
            item['offer_id'] = hash(json.dumps(dict(item), sort_keys=True)) % ((sys.maxsize + 1) * 2)
        except Exception as error:
            self.logger.error(f"{type(error).__name__}: {error} URL -> {offer_content.url}")
        return item


class BDGJobOfferSpider(BaseJobOfferSpider):
    name = "bdg"

    next_page_selector = "a[aria-label=Next]"
    content_link_selector = "div.list-container a.posting-list-item::attr(href)"
    url = sns.SCRAPED_URLS[name]