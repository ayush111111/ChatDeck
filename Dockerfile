FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir -e .

# Copy application code
COPY . .

# Create data directory for mounted volume
RUN mkdir -p /data && chmod 777 /data

# Create a non-root user for security
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app /data

USER app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Set environment variables
ENV DATABASE_URL="sqlite:///data/flashcards.db"
ENV PYTHONPATH="/app"

# Default to SQLite, but can be overridden with environment variables:
# POSTGRES_ENABLED=true
# POSTGRES_HOST=your-db-host
# POSTGRES_USER=your-username
# POSTGRES_PASSWORD=your-password
# POSTGRES_DATABASE=flashcards

# Run the application
CMD ["uvicorn", "fcg.main:app", "--host", "0.0.0.0", "--port", "8000"]
