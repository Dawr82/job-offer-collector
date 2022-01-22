import sys

import scrapy_splash
import scrapy
import redis

sys.path.append("..\..")

from config import settings
from config import sns


class BaseJobOfferSpider(scrapy.Spider):

    """Abstract class for job offer spiders."""

    offer_container_selector = "a.search-list-item" 
    offer_title_selector = "div.title h3::text"
    offer_company_selector = "div.company::text"
    offer_salary_selector = "div.salary::text"
    offer_location_selector = "//div[@class='location']/i/following-sibling::text()"
    next_page_selector = "a.next"
    request_class = scrapy.Request
    request_count = 0
    url = ""


    def start_requests(self):
        if not self.url:
            raise ValueError("Incomplete url! Define url class variable in your JobOfferSpider class.")
        yield self.request_class(url=self.url, callback=self.parse)


    def parse_single(self, offer):
        return {}


    def parse(self, response):
        offers = response.css(self.offer_container_selector)
        for offer in offers:
            yield self.parse_single(offer)
        self.request_count += 1      
        next_page = response.css(self.next_page_selector).attrib["href"]
        if next_page is not None and self.request_count < settings.MAX_REQUESTS:
            next_page = response.urljoin(next_page)
            yield self.request_class(next_page, callback=self.parse)


class BDGJobOfferSpider(BaseJobOfferSpider):

    name = "bdg"
    url = sns.SCRAPED_URLS[name]
    offer_id = 0
  
    def parse_single(self, offer):
        offer_title = offer.css(self.offer_title_selector).get().strip()
        offer_company = offer.css(self.offer_company_selector).get().strip()
        offer_salary = offer.css(self.offer_salary_selector).get()
        offer_location = offer.xpath(self.offer_location_selector).get().strip().split(", ")
        self.offer_id += 1
        return {
            "offer_id": self.offer_id,
            "source": self.name,
            "title" : offer_title,
            "company" : offer_company,
            "salary" : offer_salary,
            "location" : offer_location,
        }


class NFJJobOfferSpider(BaseJobOfferSpider):

    name = "nfj"
    url = sns.SCRAPED_URLS[name]
    offer_id = 0
   
    offer_container_selector = "div.list-container a.posting-list-item"
    offer_title_selector = "h3.posting-title__position::text"
    offer_company_selector = "span.d-block.posting-title__company::text"
    offer_salary_selector = "span.salary::text"
    offer_location_selector = "span.posting-info__location::text"
    next_page_selector = "a[aria-label=Next]"

    request_class = scrapy_splash.SplashRequest


    def parse_single(self, offer):
        offer_title = offer.css(self.offer_title_selector).get().strip()
        offer_company = offer.css(self.offer_company_selector).get().strip(' @')
        offer_salary = offer.css(self.offer_salary_selector).get().replace(u'\xa0', u' ').strip()
        try:
            offer_location = offer.css(self.offer_location_selector).get().strip()
        except AttributeError:
            offer_location = offer.css("span.posting-info__location [class]::text").get().strip().split(", ")[0] + "+"
        self.offer_id += 1
        return {
            "offer_id": self.offer_id,
            "source": self.name,
            "title" : offer_title,
            "company" : offer_company,
            "salary" : offer_salary,
            "location" : offer_location,
        }