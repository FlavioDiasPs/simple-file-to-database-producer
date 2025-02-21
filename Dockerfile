# Use official Python runtime as base image
FROM python:3.13-slim

# Set working directory at the container
WORKDIR /app

# Copy current directory contents into the container at /app
COPY . /app

# Install uv and dependencies
RUN pip install uv && uv sync

# Run the app
CMD ["uv", "run", "main.py"]
