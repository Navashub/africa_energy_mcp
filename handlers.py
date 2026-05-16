"""
Tool call handlers for Africa Energy API.
Routes requests, validates input, formats responses, and handles errors.
"""

import json
import logging
import mcp.types as types
from api_client import APIClient, APIError
from config import SUPPORTED_COUNTRIES, MIN_YEAR, MAX_YEAR

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Custom exception for input validation errors."""
    pass


def validate_country(country: str) -> None:
    """Validate that country is a non-empty string."""
    if not isinstance(country, str) or not country.strip():
        raise ValidationError("Country must be a non-empty string.")


def validate_year(year: int, field_name: str = "year") -> None:
    """Validate that year is an integer between MIN_YEAR and MAX_YEAR."""
    if not isinstance(year, int):
        raise ValidationError(f"{field_name} must be an integer.")
    if year < MIN_YEAR or year > MAX_YEAR:
        raise ValidationError(
            f"{field_name} must be between {MIN_YEAR} and {MAX_YEAR}, got {year}."
        )


def validate_year_range(start_year: int, end_year: int) -> None:
    """Validate a year range."""
    if start_year is not None:
        validate_year(start_year, "start_year")
    if end_year is not None:
        validate_year(end_year, "end_year")
    if start_year is not None and end_year is not None and start_year > end_year:
        raise ValidationError(f"start_year ({start_year}) must be <= end_year ({end_year}).")


async def handle_get_electricity_data(args: dict, client: APIClient) -> dict:
    """Handle get_electricity_data tool call."""
    country = args.get("country")
    validate_country(country)
    
    year = args.get("year")
    if year is not None:
        validate_year(year)

    logger.debug(f"Tool call: get_electricity_data for {country}, year={year}")
    
    data = await client.get("/api/v1/electricity", {
        "country": country,
        "year": year,
        "metric": args.get("metric"),
        "unit": args.get("unit"),
    })
    return data


async def handle_get_energy_data(args: dict, client: APIClient) -> dict:
    """Handle get_energy_data tool call."""
    country = args.get("country")
    validate_country(country)
    
    start_year = args.get("start_year")
    end_year = args.get("end_year")
    validate_year_range(start_year, end_year)

    logger.debug(f"Tool call: get_energy_data for {country}, years {start_year}-{end_year}")
    
    data = await client.get("/api/v1/energy", {
        "country": country,
        "sub_sector": args.get("sub_sector"),
        "start_year": start_year,
        "end_year": end_year,
        "metric": args.get("metric"),
    })
    return data


async def handle_get_economic_data(args: dict, client: APIClient) -> dict:
    """Handle get_economic_data tool call."""
    country = args.get("country")
    validate_country(country)
    
    start_year = args.get("start_year")
    end_year = args.get("end_year")
    validate_year_range(start_year, end_year)

    logger.debug(f"Tool call: get_economic_data for {country}, years {start_year}-{end_year}")
    
    data = await client.get("/api/v1/economic", {
        "country": country,
        "start_year": start_year,
        "end_year": end_year,
        "metric": args.get("metric"),
        "unit": args.get("unit"),
    })
    return data


async def handle_check_api_health(args: dict, client: APIClient) -> dict:
    """Handle check_api_health tool call."""
    logger.debug("Tool call: check_api_health")
    
    data = await client.get("/api/v1/health", {})
    return data


async def handle_list_countries(args: dict, client: APIClient) -> dict:
    """Handle list_countries tool call."""
    logger.debug("Tool call: list_countries")
    
    return {
        "count": len(SUPPORTED_COUNTRIES),
        "countries": sorted(SUPPORTED_COUNTRIES),
    }


async def call_tool(
    name: str,
    arguments: dict | None,
    client: APIClient,
) -> list[types.TextContent]:
    """
    Route tool calls to appropriate handlers.
    Validates input and formats responses.
    
    Args:
        name: Tool name
        arguments: Tool arguments dict
        client: APIClient instance
        
    Returns:
        List with single TextContent result
    """
    args = arguments or {}
    logger.debug(f"Tool call received: {name} with args {args}")

    try:
        # Route to appropriate handler
        if name == "get_electricity_data":
            data = await handle_get_electricity_data(args, client)
        elif name == "get_energy_data":
            data = await handle_get_energy_data(args, client)
        elif name == "get_economic_data":
            data = await handle_get_economic_data(args, client)
        elif name == "check_api_health":
            data = await handle_check_api_health(args, client)
        elif name == "list_countries":
            data = await handle_list_countries(args, client)
        else:
            logger.error(f"Unknown tool: {name}")
            return [types.TextContent(
                type="text",
                text=json.dumps({"error": f"Unknown tool: {name}"}, indent=2)
            )]

        # Return successful response
        logger.info(f"Tool {name} completed successfully")
        return [types.TextContent(
            type="text",
            text=json.dumps(data, indent=2)
        )]

    except ValidationError as e:
        logger.warning(f"Validation error for tool {name}: {str(e)}")
        return [types.TextContent(
            type="text",
            text=json.dumps({"error": f"Validation error: {str(e)}"}, indent=2)
        )]

    except APIError as e:
        logger.error(f"API error for tool {name}: {str(e)}")
        return [types.TextContent(
            type="text",
            text=json.dumps({"error": f"API error: {str(e)}"}, indent=2)
        )]

    except Exception as e:
        logger.error(f"Unexpected error in tool {name}: {str(e)}", exc_info=True)
        return [types.TextContent(
            type="text",
            text=json.dumps({"error": f"Unexpected error: {str(e)}"}, indent=2)
        )]
