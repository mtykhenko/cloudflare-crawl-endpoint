# Multi-stage build for Python backend
FROM python:3.11-alpine AS builder

# Set working directory
WORKDIR /app

# Install build dependencies
RUN apk add --no-cache gcc musl-dev libffi-dev

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt


# Final stage
FROM python:3.11-alpine

# Set working directory
WORKDIR /app

# Install runtime dependencies
RUN apk add --no-cache libffi curl

# Copy Python dependencies from builder
COPY --from=builder /root/.local /home/appuser/.local

# Copy application code
COPY app ./app

# Create non-root user and set permissions
RUN adduser -D -u 1000 appuser && \
    chown -R appuser:appuser /app && \
    chown -R appuser:appuser /home/appuser/.local

# Switch to non-root user
USER appuser

# Add local bin to PATH
ENV PATH=/home/appuser/.local/bin:$PATH

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Run the application
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
