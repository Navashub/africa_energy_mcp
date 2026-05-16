"""
Configuration module for Africa Energy MCP Server.
Loads environment variables and exposes constants.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
API_BASE_URL = os.getenv(
    "AFRICA_ENERGY_API_BASE_URL",
    "https://africa-energy-api.onrender.com"
)
API_KEY = os.getenv("AFRICA_ENERGY_API_KEY", "")

# Request Configuration
REQUEST_TIMEOUT = 30.0  # seconds
RETRY_MAX_ATTEMPTS = 3
RETRY_BACKOFF_FACTOR = 2.0

# Cache Configuration
CACHE_TTL_SECONDS = 600  # 10 minutes

# Supported countries (all 54 African nations)
SUPPORTED_COUNTRIES = [
    "Algeria", "Angola", "Benin", "Botswana", "Burkina Faso", "Burundi",
    "Cameroon", "Cape Verde", "Central African Republic", "Chad", "Comoros",
    "Democratic Republic of the Congo", "Republic of the Congo", "Côte d'Ivoire",
    "Djibouti", "Egypt", "Equatorial Guinea", "Eritrea", "Eswatini", "Ethiopia",
    "Gabon", "Gambia", "Ghana", "Guinea", "Guinea-Bissau", "Kenya", "Lesotho",
    "Liberia", "Libya", "Madagascar", "Malawi", "Mali", "Mauritania", "Mauritius",
    "Morocco", "Mozambique", "Namibia", "Niger", "Nigeria", "Rwanda",
    "São Tomé and Príncipe", "Senegal", "Seychelles", "Sierra Leone", "Somalia",
    "South Africa", "South Sudan", "Sudan", "Tanzania", "Togo", "Tunisia",
    "Uganda", "Zambia", "Zimbabwe"
]

# Data range
MIN_YEAR = 2000
MAX_YEAR = 2022

# Server info
SERVER_NAME = "africa-energy-mcp"
SERVER_VERSION = "1.0.0"
