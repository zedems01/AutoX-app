import json
from os import getenv
from typing import Optional, List, Dict

from pydantic import BaseModel, Field
from langchain_core.tools import tool
import logging


try:
    from firecrawl import FirecrawlApp
except ImportError:
    raise ImportError("The `firecrawl` package is not installed. Please install it.")


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)




class TrendData(BaseModel):
    """Schema for trend data extraction"""
    trend_subject: str = Field(..., description="Trending topic or hashtag.")
    posts_count: int = Field(..., description="Number of posts related to the trend.")


class TrendsResponse(BaseModel):
    """Schema for multiple trend data response. Response schema for the web scraper agent"""
    trends: List[TrendData] = Field(..., description="List of trending topics and their post counts.")
    

class FirecrawlResponse(BaseModel):
    """Schema for Firecrawl API response"""
    success: bool = Field(..., description="Indicates if the API call was successful.")
    data: Dict = Field(..., description="The data returned by the Firecrawl API.")
    status: str = Field(..., description="The status of the Firecrawl API call.")
    expiresAt: str = Field(..., description="The expiration timestamp of the cached Firecrawl API data.")


def format_url(country=None, city=None):
    if country == "worldwide":
        return "https://trends24.in/"
    elif country and city:
        return f"https://trends24.in/{country}/{city}/"
    elif country:
        return f"https://trends24.in/{country}/"
    else:
        return "https://trends24.in/"  # worldwide by default
    

@tool
def get_trending_topics(
            country: str = "worldwide",
            city: Optional[str] = None,
            max_trends: int = 5,
            api_key: Optional[str] = None,
    ) -> str:
        """
        Use this function to extract the top trending topics on Twitter from a specific location using Firecrawl.

        Args:
            country (str, optional): The country to search for trends. Defaults to "worldwide". 
            city (str, optional): The city to search for trends. Defaults to None. If a city is chosen, then a country must also be set.
            max_trends (int, optional): The maximum number of trends to extract. Defaults to 2.

        Returns:
            str: JSON string containing a list of trending topics and post counts.
        """


        api_key: Optional[str] = api_key or getenv("FIRECRAWL_API_KEY")

        if not api_key:
            logger.error("FIRECRAWL_API_KEY not set. Please set the FIRECRAWL_API_KEY environment variable.")

        app = FirecrawlApp(api_key=api_key)

        country = country.lower().replace(" ", "-")
        if city:
            city = city.lower().replace(" ", "-")
        logger.info(f"Extracting trending topics for: country={country}, city={city}, max_trends={max_trends}...")


        try:
            url = format_url(country, city)
            urls = [url]
            # params = {
            #     "prompt": f"Extract the top {max_trends} trending topics from **1 hour ago**, along with their associated post count if available.\nIf the count is not available, replace by *null*.",
            #     # "prompt": f"Extract the most recent top {max_trends} trending topics or hashtags along with their associated post count.",
            #     "schema": TrendsResponse.model_json_schema(),
            # }

            prompt= f"Extract the top {max_trends} trending topics from **1 hour ago**, along with their associated post count if available.\n" \
                        "If the count is not available, replace by *null*."
            schema= TrendsResponse.model_json_schema()
            
            # raw_response = app.extract(urls=urls, params=params)
            raw_response = app.extract(urls=urls, prompt=prompt, schema=schema)
            logger.info(f"Extraction completed.")

            # Handle potential errors and format the response properly
            if raw_response and raw_response.success and raw_response.data:
                # Make a FirecrawlResponse from the result
                # parsed_response = FirecrawlResponse(**raw_response)
                trend_data = raw_response.data

                if trend_data is None:
                    return json.dumps({"trends": []}, indent=2)
                return json.dumps(trend_data, indent=2)

            else:
                logger.error(f"Firecrawl API call failed. The response was : {raw_response}")
                return json.dumps(
                    {"error": "Firecrawl API call failed"}, indent=2
                )  # Return an error object, not just an empty string.

        except Exception as e:
            logger.error(f"Error extracting trends from Firecrawl: {e}")
            return json.dumps({"error": str(e)}, indent=2)  