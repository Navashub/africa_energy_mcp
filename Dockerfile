FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies
COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

ENV PYTHONUNBUFFERED=1

# Expose a port in case users run behind a proxy (not strictly required)
EXPOSE 8080

# Run the MCP server
CMD ["python", "server.py"]
