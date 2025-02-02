"""Kroger API client."""

import logging
from collections.abc import Generator

from clientforge import BaseModel, ClientCredentialsOAuth2Auth, ForgeClient

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
        scopes: list = None,
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
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": "Kroger API Client",
            },
        )

        self.limit = limit

        if self.limit <= 0 or self.limit > 50:
            raise ValueError("Limit must be between 1 and 50")

        if not scopes:
            logger.warning("No scopes provided!")

    def _paginate_request(
        self,
        method: str,
        endpoint: str,
        params: dict = None,
        **kwargs,
    ) -> Generator[list[dict], None, None]:
        """Paginate through the results of a request."""
        params["filter.limit"] = self.limit

        response = self._make_request(method, endpoint, params=params, **kwargs)
        yield response["data"]

        if response.get("meta"):
            total_results = len(response["data"])
            pagination = response["meta"]["pagination"]
            while total_results < pagination["total"]:
                params["filter.start"] = total_results
                response = self._make_request(method, endpoint, params=params, **kwargs)

                yield response["data"]
                total_results += len(response["data"])

    def _model_request(
        self,
        method: str,
        endpoint: str,
        model: BaseModel,
        params: dict = None,
        number_of_results: int = 10,
        **kwargs,
    ) -> list[BaseModel]:
        """Make a request and return a list of model objects."""
        generator = self._paginate_request(method, endpoint, params=params, **kwargs)

        results = []
        for data in generator:
            results.extend([model.from_dict(item) for item in data])
            if len(results) >= number_of_results:
                break

        return results[:number_of_results]

    def search_products(
        self,
        terms: list[str] = None,
        brand: str = None,
        fulfillment: str = None,
        location_id: str = None,
        product_id: str = None,
        number_of_results: int = 10,
    ) -> list[Product]:
        """Search for products based on the provided search terms.

        Parameters
        ----------
            terms (list[str], optional): Search terms. Defaults to None.
            brand (str, optional): Brand name. Defaults to None.
            fulfillment (str, optional): Fulfillment type. Defaults to None.
            location_id (str, optional): Location ID. Defaults to None.
            product_id (str, optional): Product ID. Defaults to None.
            number_of_results (int, optional): Number of results to return.
                Defaults to 10.

        Returns
        -------
            list[Product]: List of Product objects.

        Scopes:
            - product.compact

        Notes
        -----
            https://developer.kroger.com/api-products/api/product-api-public
        """
        if len(terms) > 8:
            raise ValueError("Number of search terms must be less than or equal to 8")

        params = {
            "filter.term": terms,
            "filter.brand": brand,
            "filter.fulfillment": fulfillment,
            "filter.locationId": location_id,
            "filter.productId": product_id,
        }
        return self._model_request(
            "GET",
            "products",
            Product,
            params=params,
            number_of_results=number_of_results,
        )

    def get_product(self, product_id: str) -> Product:
        """Get a product by its ID.

        Args:
            product_id (str): Product ID.

        Returns
        -------
            Product: Product object.

        Scopes:
            - product.compact

        Notes
        -----
            https://developer.kroger.com/api-products/api/product-api-public
        """
        return self._make_request("GET", f"products/{product_id}").to_model(
            Product, key="data"
        )

    def search_locations(
        self,
        zip_code: str = None,
        lat_long: tuple[float, float] = None,
        radius: int = 10,
        chain: str = "Kroger",
        department: str = None,
        location_ids: list[str] = None,
        number_of_results: int = 10,
    ) -> list[Location]:
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
            number_of_results (int, optional): Number of results to return.
                Defaults to 10.

        Returns
        -------
            list[Location]: List of Location objects.

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
            params=params,
            number_of_results=number_of_results,
        )

    def get_location(self, location_id: str) -> Location:
        """Get a location by its ID.

        Parameters
        ----------
            location_id (str): Location ID.

        Returns
        -------
            Location: Location object.

        Notes
        -----
            https://developer.kroger.com/api-products/api/location-api-public
        """
        return self._make_request("GET", f"locations/{location_id}").to_model(
            Location, key="data"
        )
