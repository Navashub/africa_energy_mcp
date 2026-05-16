"""
MCP Tool definitions for Africa Energy API.
Defines schemas and metadata for all available tools.
"""

import mcp.types as types

# Tool: Get Electricity Data
GET_ELECTRICITY_DATA = types.Tool(
    name="get_electricity_data",
    description=(
        "Fetch electricity-related data for an African country. "
        "Returns metrics like installed capacity, generation, and energy access. "
        "Data covers years 2000–2022."
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "country": {
                "type": "string",
                "description": "Name of the African country, e.g. 'Kenya', 'Nigeria', 'Egypt'",
            },
            "year": {
                "type": "integer",
                "description": "Optional: filter by specific year (2000–2022)",
            },
            "metric": {
                "type": "string",
                "description": "Optional: specific metric to filter by, e.g. 'Installed capacity'",
            },
            "unit": {
                "type": "string",
                "description": "Optional: unit of measurement, e.g. 'MW'",
            },
        },
        "required": ["country"],
    },
)

# Tool: Get Energy Data
GET_ENERGY_DATA = types.Tool(
    name="get_energy_data",
    description=(
        "Fetch general energy sector data for an African country. "
        "Can filter by sub-sector such as 'Access', 'Efficiency', or 'Renewables'. "
        "Data covers years 2000–2022."
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "country": {
                "type": "string",
                "description": "Name of the African country, e.g. 'Kenya', 'South Africa'",
            },
            "sub_sector": {
                "type": "string",
                "description": "Optional: sub-sector to filter by, e.g. 'Access', 'Efficiency', 'Renewables'",
            },
            "start_year": {
                "type": "integer",
                "description": "Optional: start of a year range, e.g. 2005",
            },
            "end_year": {
                "type": "integer",
                "description": "Optional: end of a year range, e.g. 2020",
            },
            "metric": {
                "type": "string",
                "description": "Optional: specific metric name",
            },
        },
        "required": ["country"],
    },
)

# Tool: Get Economic Data
GET_ECONOMIC_DATA = types.Tool(
    name="get_economic_data",
    description=(
        "Fetch economic indicator data for an African country. "
        "Includes GDP, inflation, population, energy spending, and more. "
        "Can filter by year range. Data covers years 2000–2022."
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "country": {
                "type": "string",
                "description": "Name of the African country, e.g. 'Kenya', 'Ghana'",
            },
            "start_year": {
                "type": "integer",
                "description": "Optional: start of a year range, e.g. 2000",
            },
            "end_year": {
                "type": "integer",
                "description": "Optional: end of a year range, e.g. 2022",
            },
            "metric": {
                "type": "string",
                "description": "Optional: specific metric, e.g. 'GDP', 'Rural population'",
            },
            "unit": {
                "type": "string",
                "description": "Optional: unit filter, e.g. 'Current US$'",
            },
        },
        "required": ["country"],
    },
)

# Tool: Check API Health
CHECK_API_HEALTH = types.Tool(
    name="check_api_health",
    description="Check whether the Africa Energy Data API is online and responding correctly.",
    inputSchema={
        "type": "object",
        "properties": {},
        "required": [],
    },
)

# Tool: List Supported Countries
LIST_COUNTRIES = types.Tool(
    name="list_countries",
    description=(
        "List all 54 African countries supported by the Africa Energy API. "
        "Use this to discover which countries are available for querying."
    ),
    inputSchema={
        "type": "object",
        "properties": {},
        "required": [],
    },
)


def get_tools() -> list[types.Tool]:
    """Return all available tools."""
    return [
        GET_ELECTRICITY_DATA,
        GET_ENERGY_DATA,
        GET_ECONOMIC_DATA,
        CHECK_API_HEALTH,
        LIST_COUNTRIES,
    ]
