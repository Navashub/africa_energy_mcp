# Africa Energy Data MCP Server

An MCP (Model Context Protocol) server that exposes the [Africa Energy Data API](https://rapidapi.com/api-details/africa-energy-api) as tools for Claude, Cursor, and other MCP-compatible clients.

Query electricity, energy, and economic data for all 54 African countries spanning 2000–2022. The server includes **automatic caching** (10-minute TTL), **retry logic with exponential backoff**, **input validation**, and **structured logging**.

## Features

- **5 Tools**: Electricity data, Energy data, Economic indicators, Health check, Country list
- **Auto-caching**: 10-minute in-memory cache to reduce API calls
- **Retry logic**: 3 retries with exponential backoff on 5xx errors and timeouts
- **Input validation**: Validates country names, years, and year ranges
- **Structured logging**: Full debug logs output to stderr (doesn't interfere with MCP stdio)
- **Production-ready**: Modular design, error handling, timeout management

## Setup

### 1. Clone or download this repository
```bash
cd africa_energy_mcp
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Get an API key
1. Go to [Africa Energy Data API on RapidAPI](https://rapidapi.com/api-details/africa-energy-api)
2. Sign up or log in to RapidAPI
3. Click "Subscribe" (free tier available)
4. Copy your API key from the dashboard

### 4. Create a `.env` file
```bash
cp .env.example .env
```

Edit `.env` and paste your API key:
```env
AFRICA_ENERGY_API_KEY=your_key_here
```

### 5. Test the server locally
```bash
python server.py
```

You should see startup logs on stderr. Press Ctrl+C to stop.

## Available Tools

### 1. `get_electricity_data`
Fetch electricity metrics for an African country.

**Parameters:**
- `country` (required): Country name, e.g. "Kenya", "Nigeria"
- `year` (optional): Filter by year (2000–2022)
- `metric` (optional): Specific metric name
- `unit` (optional): Measurement unit

**Example:**
```json
{
  "country": "Kenya",
  "year": 2022
}
```

### 2. `get_energy_data`
Fetch general energy sector data (access, efficiency, renewables, etc.).

**Parameters:**
- `country` (required): Country name
- `sub_sector` (optional): "Access", "Efficiency", "Renewables", etc.
- `start_year` (optional): Year range start (2000–2022)
- `end_year` (optional): Year range end
- `metric` (optional): Specific metric name

**Example:**
```json
{
  "country": "South Africa",
  "start_year": 2010,
  "end_year": 2022
}
```

### 3. `get_economic_data`
Fetch economic indicators: GDP, inflation, population, energy spending, etc.

**Parameters:**
- `country` (required): Country name
- `start_year` (optional): Year range start
- `end_year` (optional): Year range end
- `metric` (optional): "GDP", "Inflation", "Rural population", etc.
- `unit` (optional): Measurement unit

### 4. `check_api_health`
Verify the API is online and responding.

**No parameters required.**

### 5. `list_countries`
Get the list of all 54 supported African countries.

**No parameters required.**

## Connect to Claude Desktop

### macOS / Linux

Edit `~/.config/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "africa-energy": {
      "command": "python",
      "args": ["/path/to/africa_energy_mcp/server.py"]
    }
  }
}
```

Replace `/path/to/africa_energy_mcp` with the full path to your repository.

### Windows

Edit `%APPDATA%\Claude\claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "africa-energy": {
      "command": "python",
      "args": ["C:\\path\\to\\africa_energy_mcp\\server.py"]
    }
  }
}
```

Then restart Claude Desktop. The tool should appear in the MCP tools list.

## Connect to Cursor

1. Open Cursor Settings (Cmd/Ctrl + ,)
2. Search for "MCP"
3. Click "Edit in Settings JSON"
4. Add to your `settings.json`:

```json
"mcp.servers": {
  "africa-energy": {
    "command": "python",
    "args": ["/path/to/africa_energy_mcp/server.py"]
  }
}
```

Save and restart Cursor. Tools should be available in chat.

## Optional: CI and publishing

If you'd like to publish or run this server automatically (for example to make it runnable from remote hosts or CI), consider adding CI that builds a Docker image and pushes it to a registry (GitHub Container Registry or Docker Hub). A `Dockerfile` and an example GitHub Actions workflow are included in the repository as a starting point — feel free to customize them for your preferred registry and release process.

For most users, the simplest path is to run the server locally (see "Setup" above) and connect an MCP client such as Claude Desktop or Cursor.

## Project Structure

```
africa_energy_mcp/
├── server.py              # MCP server entry point, wires tools + handlers
├── config.py              # Environment variables, constants, country list
├── api_client.py          # Async HTTP client, retry logic, caching
├── tools.py               # MCP tool schema definitions
├── handlers.py            # Input validation, routing, response formatting
├── requirements.txt       # Python dependencies
├── .env.example          # Example environment configuration
└── README.md             # This file
```

## Architecture

**Request flow:**
1. **server.py** receives tool call via MCP
2. **handlers.py** validates input, calls **api_client.py**
3. **api_client.py** checks cache, makes HTTP request, retries on failure
4. Response is cached and returned as JSON
5. **server.py** formats and returns to MCP client

**Caching:**
- Key: `(endpoint, frozenset(params))`
- TTL: 10 minutes (configurable in `config.py`)
- In-memory only (cleared on server restart)

**Retry logic:**
- Retries on `5xx` errors and timeouts
- Up to 3 attempts
- Exponential backoff: 1s, 2s, 4s
- Does NOT retry on `4xx` errors (client errors)

## Configuration

Edit `config.py` to adjust:

- `REQUEST_TIMEOUT`: HTTP timeout (default: 30s)
- `RETRY_MAX_ATTEMPTS`: Max retries (default: 3)
- `RETRY_BACKOFF_FACTOR`: Backoff multiplier (default: 2.0)
- `CACHE_TTL_SECONDS`: Cache expiry (default: 600s)

## Logging

Logs are written to **stderr** with format:
```
2024-05-16 10:30:45,123 - handlers - DEBUG - Tool call: get_electricity_data for Kenya, year=2022
```

**Log levels:**
- `DEBUG`: Tool calls, cache hits/misses, retry attempts
- `INFO`: Successful API calls, cache operations
- `WARNING`: Retries, expired cache entries
- `ERROR`: API failures, validation errors, network issues

## Error Handling

All tool calls return well-formatted JSON error responses:

```json
{
  "error": "Validation error: Country must be a non-empty string."
}
```

Common errors:
- `Validation error`: Invalid input (bad country, year out of range)
- `API error`: Server returned 4xx or 5xx
- `Request timeout`: API didn't respond within 30s (will retry)
- `Unexpected error`: Unhandled exception

## Testing

```bash
# Start the server
python server.py

# In another terminal, test with curl (mock MCP call):
# This is for manual testing; MCP clients handle this automatically
```

Or test the handler directly in Python:

```python
import asyncio
from handlers import call_tool
from api_client import APIClient

async def test():
    async with APIClient() as client:
        result = await call_tool(
            "get_electricity_data",
            {"country": "Kenya", "year": 2022},
            client
        )
        print(result[0].text)

asyncio.run(test())
```

## Troubleshooting

**"Unknown or invalid tool"**
- Restart Claude Desktop / Cursor
- Check config file path is correct

**"AFRICA_ENERGY_API_KEY not found"**
- Create `.env` file (copy from `.env.example`)
- Check `AFRICA_ENERGY_API_KEY` is set
- Verify it's a valid RapidAPI key

**"API error 401"**
- API key is invalid or expired
- Regenerate key from RapidAPI dashboard

**"Request timeout"**
- API is slow; server will retry automatically
- Increase `REQUEST_TIMEOUT` in `config.py` if retries exhaust

**"No such file or directory: server.py"**
- Run from the `africa_energy_mcp` directory
- Or provide full path: `python /path/to/server.py`

## Contributing

To improve the server:

1. Fork this repo (if on GitHub)
2. Create a feature branch
3. Make changes to `handlers.py`, `api_client.py`, or add new tools to `tools.py`
4. Test locally
5. Submit a pull request

## License

MIT License — feel free to use and modify for your projects.

## Support

For issues or questions:
- Check the [MCP documentation](https://modelcontextprotocol.io)
- Review [RapidAPI Africa Energy API docs](https://rapidapi.com/api-details/africa-energy-api)
- Open an issue on GitHub (if hosted there)

---

**Version**: 1.0.0  
**Last Updated**: 2024-05-16  
**Status**: Production-ready ✅
