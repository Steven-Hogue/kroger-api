"""Models for Kroger API."""

from clientforge import ForgeModel
from dataclass_wizard.v1 import Alias, AliasPath, TimePattern


class AisleLocation(ForgeModel):
    bay_number: int
    description: str
    number: int
    number_of_facings: int
    side: str
    shelf_number: int
    shelf_position_in_bay: int
    sequence_number: int | None = None


class Fulfillment(ForgeModel):
    curbside: bool = False
    delivery: bool = False
    in_store: bool = False
    ship_to_home: bool = False


class Price(ForgeModel):
    regular: float
    promo: float
    regularPerUnitEstimate: float | None = None
    promoPerUnitEstimate: float | None = None


class Item(ForgeModel):
    item_id: str
    favorite: bool
    fulfillment: Fulfillment
    size: str

    price: Price | None = None
    national_price: Price | None = None
    sold_by: str | None = None
    stock_level: str | None = Alias("inventory.stockLevel", default=None)


class Sizes(ForgeModel):
    size: str
    url: str


class Image(ForgeModel):
    perspective: str
    sizes: list[Sizes]


class Product(ForgeModel):
    product_id: str
    aisle_locations: list[AisleLocation]
    brand: str
    categories: list[str]
    description: str
    items: list[Item]
    images: list[Image]
    upc: str
    product_page_uri: str = Alias("productPageURI")
    temp_indicator: str = AliasPath("temperature.indicator")
    heat_sensitive: bool = AliasPath("temperature.heatSensitive")

    country_origin: str | None = None
    depth: float | None = AliasPath("itemInformation.depth", default=None)
    height: float | None = AliasPath("itemInformation.height", default=None)
    width: float | None = AliasPath("itemInformation.width", default=None)


class DayHours(ForgeModel):
    open: TimePattern["%H:%M"]  # noqa: F722
    close: TimePattern["%H:%M"]  # noqa: F722
    open24: bool


class Hours(ForgeModel):
    Open24: bool
    monday: DayHours
    tuesday: DayHours
    wednesday: DayHours
    thursday: DayHours
    friday: DayHours
    saturday: DayHours
    sunday: DayHours

    gmtOffset: str | None = None
    timezone: str | None = None


class Geolocation(ForgeModel):
    latitude: float
    longitude: float


class Address(ForgeModel):
    addressLine1: str
    city: str
    state: str
    zipCode: str

    county: str | None = None
    addressLine2: str | None = None


class Department(ForgeModel):
    departmentId: str
    name: str

    hours: Hours | None = None
    phone: str | None = None
    address: Address | None = None
    geolocation: Geolocation | None = None
    offsite: bool | None = None


class Location(ForgeModel):
    name: str
    division_number: int
    store_number: int
    location_id: str
    chain: str
    phone: str
    address: Address
    departments: list[Department]
    geolocation: Geolocation
    hours: Hours
