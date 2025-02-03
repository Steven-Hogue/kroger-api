"""Models for Kroger API."""

from dataclasses import dataclass

from clientforge import ForgeModel
from dataclass_wizard import TimePattern, path_field


@dataclass
class AisleLocation(ForgeModel):
    bay_number: int
    description: str
    number: int
    number_of_facings: int
    sequence_number: int
    side: str
    shelf_number: int
    shelf_position_in_bay: int


@dataclass
class Fulfillment(ForgeModel):
    curbside: bool = False
    delivery: bool = False
    instore: bool = False
    shiptohome: bool = False


@dataclass
class Price(ForgeModel):
    regular: float
    promo: float
    regularPerUnitEstimate: float
    promoPerUnitEstimate: float


@dataclass
class Item(ForgeModel):
    item_id: str
    favorite: bool
    fulfillment: Fulfillment
    size: str

    price: Price | None = None
    national_price: Price | None = None
    sold_by: str | None = None
    stock_level: str | None = path_field("inventory.stockLevel", default=None)


@dataclass
class Sizes(ForgeModel):
    size: str
    url: str


@dataclass
class Image(ForgeModel):
    perspective: str
    sizes: list[Sizes]


@dataclass
class Product(ForgeModel):
    product_id: str
    product_page_uri: str
    aisle_locations: list[AisleLocation]
    brand: str
    categories: list[str]
    description: str
    items: list[Item]
    images: list[Image]
    upc: str
    temp_indicator: str = path_field("temperature.indicator")
    heat_sensitive: bool = path_field("temperature.heatSensitive")

    country_origin: str | None = None
    depth: float | None = path_field("itemInformation.depth", default=None)
    height: float | None = path_field("itemInformation.height", default=None)
    width: float | None = path_field("itemInformation.width", default=None)


@dataclass
class DayHours(ForgeModel):
    open: TimePattern["%H:%M"]  # noqa: F722
    close: TimePattern["%H:%M"]  # noqa: F722
    open24: bool


@dataclass
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


@dataclass
class Geolocation(ForgeModel):
    latitude: float
    longitude: float


@dataclass
class Department(ForgeModel):
    departmentId: str
    name: str

    hours: Hours | None = None
    phone: str | None = None


@dataclass
class Address(ForgeModel):
    addressLine1: str
    city: str
    county: str
    state: str
    zipCode: str

    addressLine2: str | None = None


@dataclass
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
