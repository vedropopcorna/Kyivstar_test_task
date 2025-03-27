# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY requirements.txt requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install additional system dependencies if required
RUN apt-get update && \
    apt-get install -y --no-install-recommends g++ make && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

ADD . /app

# Runtime configuration
EXPOSE 8030
ENV PYTHONUNBUFFERED=1 \
    PORT=8030 \
    HOST=0.0.0.0

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8030/ || exit 1

# Run the application
ENTRYPOINT ["uvicorn", "app.main:app"]
CMD ["--host", "0.0.0.0", "--port", "8030"]