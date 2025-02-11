"""Kroger API client."""

import logging

from clientforge import ClientCredentialsOAuth2Auth, ForgeClient
from clientforge.models import Result
from clientforge.paginate import OffsetPaginator

from kroger_api.models import Location, Product

logger = logging.getLogger(__name__)


class KrogerClient(ForgeClient):
    """Kroger API client.

    Notes
    -----
        https://developer.kroger.com
    """

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        scopes: list | None = None,
        limit: int = 10,
    ):
        """Kroger API client.

        Parameters
        ----------
            client_id (str): Client ID.
            client_secret (str): Client secret.
            scopes (list, optional): List of scopes. Defaults to None.
            limit (int, optional): Number of results to return. Defaults to 10.
        """
        super().__init__(
            api_url="https://api.kroger.com/v1/{endpoint}",
            auth=ClientCredentialsOAuth2Auth(
                "https://api.kroger.com/v1/connect/oauth2/token",
                client_id=client_id,
                client_secret=client_secret,
                scopes=scopes,
            ),
            paginator=OffsetPaginator(
                page_size=limit,
                page_size_param="filter.limit",
                path_to_data="data",
                page_offset_param="filter.start",
                path_to_total="meta.pagination.total",
            ),
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": "Kroger API Client",
            },
        )

        if limit <= 0 or limit > 50:
            raise ValueError("Limit must be between 1 and 50")

        if not scopes:
            logger.warning("No scopes provided!")

    def search_products(
        self,
        terms: list[str] | None = None,
        brand: str | None = None,
        fulfillment: str | None = None,
        location_id: str | None = None,
        product_id: str | None = None,
        top_n: int = 10,
    ) -> Result[Product]:
        """Search for products based on the provided search terms.

        Parameters
        ----------
            terms (list[str], optional): Search terms. Defaults to None.
            brand (str, optional): Brand name. Defaults to None.
            fulfillment (str, optional): Fulfillment type. Defaults to None.
            location_id (str, optional): Location ID. Defaults to None.
            product_id (str, optional): Product ID. Defaults to None.
            top_n (int, optional): Number of results to return.
                Defaults to 10.

        Returns
        -------
            Result[Product]: Result object containing list of Product objects.

        Scopes:
            - product.compact

        Notes
        -----
            https://developer.kroger.com/api-products/api/product-api-public
        """
        if terms and len(terms) > 8:
            raise ValueError("Number of search terms must be less than or equal to 8")

        params = {
            "filter.term": " ".join(terms) if terms else None,
            "filter.brand": brand,
            "filter.fulfillment": fulfillment,
            "filter.locationId": location_id,
            "filter.productId": product_id,
        }
        return self._model_request(
            "GET",
            "products",
            Product,
            model_key="data",
            params=params,
            top_n=top_n,
        )

    def get_product(self, product_id: str) -> Result[Product]:
        """Get a product by its ID.

        Args:
            product_id (str): Product ID.

        Returns
        -------
            Result[Product]: Result object containing Product object.

        Scopes:
            - product.compact

        Notes
        -----
            https://developer.kroger.com/api-products/api/product-api-public
        """
        return self._model_request(
            "GET",
            f"products/{product_id}",
            Product,
            model_key="data",
        )

    def search_locations(
        self,
        zip_code: str | None = None,
        lat_long: tuple[float, float] | None = None,
        radius: int = 10,
        chain: str = "Kroger",
        department: str | None = None,
        location_ids: list[str] | None = None,
        top_n: int = 10,
    ) -> Result[Location]:
        """Search for locations based on the provided search criteria.

        Requires either zip_code or lat_long to be provided, but not both.

        Parameters
        ----------
            zip_code (str, optional): Search near zip code. Defaults to None.
            lat_long (tuple[float, float], optional): Search near latitude and
                longitude. Defaults to None.
            radius (int, optional): Search radius in miles. Defaults to 10.
            chain (str, optional): Filter by chain name, only stores matching the
                provided chain name are returned. Defaults to "Kroger".
            department (str, optional): Filter by department ID, only stores that have
                all of the departments provided are returned. Defaults to None.
            location_ids (list[str], optional): Comma-separated list of location IDs.
                Defaults to None.
            top_n (int, optional): Number of results to return.
                Defaults to 10.

        Returns
        -------
            Result[Location]: Result object containing list of Location objects.

        Notes
        -----
            https://developer.kroger.com/api-products/api/location-api-public
        """
        if (zip_code and lat_long) or not (zip_code or lat_long):
            raise ValueError("Provide either zip_code or lat_long, not both or neither")

        params = {
            "filter.zipCode.near": zip_code,
            "filter.latLong.near": lat_long,
            "filter.radiusInMiles": radius,
            "filter.chain": chain,
            "filter.department": department,
            "filter.locationId": location_ids,
        }
        return self._model_request(
            "GET",
            "locations",
            Location,
            model_key="data",
            params=params,
            top_n=top_n,
        )

    def get_location(self, location_id: str) -> Result[Location]:
        """Get a location by its ID.

        Parameters
        ----------
            location_id (str): Location ID.

        Returns
        -------
            Result[Location]: Result object containing Location object.

        Notes
        -----
            https://developer.kroger.com/api-products/api/location-api-public
        """
        return self._model_request(
            "GET",
            f"locations/{location_id}",
            Location,
            model_key="data",
        )
