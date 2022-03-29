from scrapy import Field, Item
from scrapy.loader import ItemLoader
from itemloaders.processors import(
    MapCompose, 
    Compose, 
    TakeFirst, 
    Identity
)


CHARS = {
    "\u00f3": "o", 
    "\u0142": "l",
    "\u0105": "a",
    "\u0107": "c",
    "\u0119": "e",
    "\u0144": "n",
    "\u015b": "s",
    "\u017a": "z",
    "\u017c": "z",
    "\u00d3": "O",
    "\u0141": "L",
    "\u0104": "A",
    "\u0106": "C",
    "\u0118": "E",
    "\u0143": "N",
    "\u015a": "s",
    "\u0179": "z",
    "\u017b": "z", 
}

ALLOWED_LOCATIONS = [
    'Warszawa',
    'Krakow',
    'Poznan',
    'Gdansk',
    'Gliwice',
    'Katowice',
    'Lublin',
    'Rzeszow',
    'Wroclaw',
    'Zielona Gora',
    'Bydgoszcz',
    'Torun',
    'Kielce',
    'Bialystok'
]


def replace_polish_chars(value: str) -> str:
    for polish, replacement in CHARS.items():
        if polish in value:
            value = value.replace(polish, replacement)
    return value


def parse_locations(locations: str) -> list[str]:
    locations = locations.split(", ")
    try:
        locations.remove("\u2022")
    except ValueError:
        pass
    return locations


def set_remote(value: str) -> bool:
    return True if value is not None else False


def filter_location(location: str):
    return location if location in ALLOWED_LOCATIONS else None


class JobOfferHeader(Item):
    offer_id = Field()
    position = Field()
    company = Field()
    locations = Field()
    salary = Field()
    remote = Field()


class JobOfferContent(JobOfferHeader):
    category = Field()
    seniority = Field()
    required = Field()
    optional = Field()


class NFJOfferHeaderLoader(ItemLoader):
    company_in = MapCompose(lambda v: v.strip(' @'))
    salary_in = MapCompose(lambda v: v.replace(u'\xa0', u' '))
    locations_in = MapCompose(lambda v: v.split(', '))


class NFJOfferContentLoader(ItemLoader):

    default_output_processor = TakeFirst()
    default_input_processor = MapCompose(lambda v: v.strip())

    salary_in = MapCompose(lambda v: v.replace("\xa0", ""))
    locations_in = MapCompose(
        lambda v: v.strip(' +1'), parse_locations, 
        replace_polish_chars, filter_location)
    remote_in = Compose(set_remote)
    category_in = MapCompose(lambda v: v.split(', '))

    locations_out = Identity()
    required_out = Identity()
    optional_out = Identity()
    seniority_out = Identity()