import scrapy
import redis

from . import config


class BaseJobOfferSpider(scrapy.Spider):

    """Abstract class for other job scraping related spider classes."""

    offer_title_selector = "div.title h3::text"
    offer_company_selector = "div.company::text"
    offer_salary_selector = "div.salary::text"
    offer_location_selector = "//div[@class='location']/i/following-sibling::text()"
    next_page_selector = "a.next"

    request_count = 0

    
    def parse_single(self, offer):
        return {}


    def parse(self, response):
        offers = response.css("a.search-list-item")
        for offer in offers:
            yield self.parse_single(offer)

        self.request_count += 1
        
        next_page = response.css(self.next_page_selector).attrib["href"]
        if next_page is not None and self.request_count < config.MAX_REQUESTS:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)



class JobOfferSpider1(BaseJobOfferSpider):

    name = "bdg"
    start_urls = [
        config.SCRAPED_URLS[name],
    ]

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


class JobOfferSpider2(BaseJobOfferSpider):

    name = "nfj"
    start_urls = [
        config.SCRAPED_URLS[name]
    ]