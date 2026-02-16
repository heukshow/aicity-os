# Imperial OS Docker Environment
FROM python:3.11-slim

# Install system dependencies (for pygame and other libs)
RUN apt-get update && apt-get install -y \
    gcc \
    libasound2-dev \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-mixer-dev \
    libsdl2-ttf-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/execution

# Run the command center by default
CMD ["python", "execution/central_cmd.py"]
