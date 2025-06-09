FROM python:3.11-bullseye

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Replace default Debian sources with Iranian mirror (handle all sources files)
RUN find /etc/apt/sources.list.d/ -type f -exec sed -i 's|http://deb.debian.org/debian|http://mirror.sbu.ac.ir/debian|g' {} + && \
    find /etc/apt/sources.list.d/ -type f -exec sed -i 's|http://security.debian.org/debian-security|http://mirror.sbu.ac.ir/debian-security|g' {} +

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    gnupg \
    build-essential \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get update && \
    apt-get install -y --no-install-recommends \
    nodejs \
    ca-certificates \
    && update-ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create necessary directories
RUN mkdir -p /app/app/static/exports /app/app/static/backups /app/app/static/fonts

# Install Node.js dependencies and build assets
RUN npm install && \
    npm run build

# Expose port
EXPOSE 5000

# Run the application
CMD ["python", "app.py"] 