import sys

import scrapy_splash
import scrapy
import redis

sys.path.append("..\..")

from config import settings
from config import sns

import utils


class BaseJobOfferSpider(scrapy.Spider):

    """Abstract class for job offer spiders."""

    offer_container_selector = "a.search-list-item" 
    offer_title_selector = "div.title h3::text"
    offer_company_selector = "div.company::text"
    offer_salary_selector = "div.salary::text"
    offer_location_selector = "//div[@class='location']/i/following-sibling::text()"

    offer_content_selector = "div.list-container a.posting-list-item::attr(href)"

    next_page_selector = "a.next"
    request_class = scrapy.Request
    request_count = 0
    url = ""


    def start_requests(self):
        if not self.url:
            raise ValueError("Incomplete url! Define url class variable in your JobOfferSpider class.")
        yield self.request_class(url=self.url, callback=self.parse, meta={'proxy':'http://103.92.114.2:80'})


    def parse_single(self, offer):
        raise NotImplementedError("This function is not implemented")


    def parse_offer_content(self, offer_content):
        raise NotImplementedError("This function is not implemented!")


    def parse(self, response):
        offer_content_links = response.css(self.offer_content_selector)
        for offer_content_link in offer_content_links:
            yield self.request_class(response.urljoin(offer_content_link.get()), callback=self.parse_offer_content)

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

    
    def parse_offer_content(self, offer_content):

        self.offer_id += 1

        requirements_container = offer_content.css("div [id=posting-requirements]")
        requirements = self.parse_offer_requirements(requirements_container)

        params_container = offer_content.css("div.row.mb-3")
        params = self.parse_offer_params(params_container)

        return {
            "offer_id": self.offer_id,
            **params,
            **requirements,
        }
    
    def parse_offer_requirements(self, requirements_container):
        try:
            required = requirements_container.css("[class=d-block] h3.mb-0 button::text").getall()
            required += requirements_container.css("[class=d-block] h3.mb-0 a::text").getall()

            optional = requirements_container.css("[id=posting-nice-to-have] h3.mb-0 button::text").getall()
            optional += requirements_container.css("[id=posting-nice-to-have] h3.mb-0 a::text").getall()
        except Exception as exc:
            print(exc)

        return {
            "required": required,
            "optional": optional,
        }

    def parse_offer_params(self, params_container):
        try:
            position = params_container.css("[id=posting-header] h1::text").get()
            company = params_container.css("[id=postingCompanyUrl]::text").get()
            category = params_container.css("span.font-weight-semi-bold::text").get()
            seniority = params_container.css("[id=posting-seniority] span::text").get()
            salary = params_container.css("div.salary h4::text").get().replace("\xa0", "")

            locations = list()
            is_remote = params_container.css("[maticon=home]").get()
            if is_remote is not None:
                locations.append("Remote")

            try:
                locations += params_container.css("[popoverplacement=bottom] span::text").get().split(", ")
            except Exception:
                pass

            locations = utils.map_polish_chars(locations)
        except Exception as exc:
            print(exc)
   
        return {
            "position": position,
            "category": category,
            "company": company,
            "locations": locations,
            "seniority": seniority,
            "salary": salary,
        }