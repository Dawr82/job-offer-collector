import sys

from scrapy_splash import SplashRequest
import scrapy
import redis

sys.path.append("..\..")

from config import settings


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
            try:
                parsed = self.parse_single(offer)
            except AttributeError:
                yield None
            else:
                yield parsed
        self.request_count += 1      
        next_page = response.css(self.next_page_selector).attrib["href"]
        if next_page is not None and self.request_count < settings.MAX_REQUESTS:
            next_page = response.urljoin(next_page)
            yield self.request_class(next_page, callback=self.parse)


class BDGJobOfferSpider(BaseJobOfferSpider):

    name = "bdg"
    url = settings.SCRAPED_URLS[name]
  
    def parse_single(self, offer):
        offer_title = offer.css(self.offer_title_selector).get().strip()
        offer_company = offer.css(self.offer_company_selector).get().strip()
        offer_salary = offer.css(self.offer_salary_selector).get()
        offer_location = offer.xpath(self.offer_location_selector).get().strip().split(", ")
        return {
            "title" : offer_title,
            "company" : offer_company,
            "salary" : offer_salary,
            "location" : offer_location,
        }


class NFJJobOfferSpider(BaseJobOfferSpider):

    name = "nfj"
   
    offer_title_selector = "h3.posting-title__position.color-main.ng-star-inserted::text"
    offer_company_selector = "span.d-block.posting-title__company.text-truncate::text"
    offer_salary_selector = "span.text-truncate.badgy.salary.btn.btn-outline-secondary.btn-sm.ng-star-inserted::text"
    offer_location_selector = "span.posting-info__location.d-flex.align-items-center.ml-auto::text"
    next_page_selector = "a[aria-label=Next]"
    offers = "div.list-container.ng-star-inserted a"

    request_class = SplashRequest
    url = settings.SCRAPED_URLS[name]


    def parse_single(self, offer):
        offer_title = offer.css(self.offer_title_selector).get().strip()
        offer_company = offer.css(self.offer_company_selector).get().strip(' @')
        offer_salary = offer.css(self.offer_salary_selector).get().replace(u'\xa0', u' ').strip()
        offer_location = offer.css(self.offer_location_selector).get().strip()
        return {
            "title" : offer_title,
            "company" : offer_company,
            "salary" : offer_salary,
            "location" : offer_location,
        }