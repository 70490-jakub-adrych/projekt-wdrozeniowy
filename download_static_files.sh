#!/bin/sh
# Shell script to download static files from GitHub repository

# Create directory structure for development
mkdir -p static/crm/css static/crm/js static/crm/webfonts

# Create directory structure for production (myDevil hosting)
mkdir -p public/static/crm/css public/static/crm/js public/static/crm/webfonts
mkdir -p public/media

echo "Downloading static files from GitHub repository..."

# Base URL for your static files repository
BASE_URL="https://raw.githubusercontent.com/70490-jakub-adrych/static/main/static"

# Download CSS files to both locations
echo "Downloading CSS files..."
curl -s -o static/crm/css/bootstrap.min.css "$BASE_URL/crm/css/bootstrap.min.css"
curl -s -o static/crm/css/all.min.css "$BASE_URL/crm/css/all.min.css"
curl -s -o public/static/crm/css/bootstrap.min.css "$BASE_URL/crm/css/bootstrap.min.css"
curl -s -o public/static/crm/css/all.min.css "$BASE_URL/crm/css/all.min.css"

# Download JS files to both locations
echo "Downloading JavaScript files..."
curl -s -o static/crm/js/bootstrap.min.js "$BASE_URL/crm/js/bootstrap.min.js"
curl -s -o static/crm/js/jquery-3.5.1.slim.min.js "$BASE_URL/crm/js/jquery-3.5.1.slim.min.js"
curl -s -o static/crm/js/popper.min.js "$BASE_URL/crm/js/popper.min.js"
curl -s -o public/static/crm/js/bootstrap.min.js "$BASE_URL/crm/js/bootstrap.min.js"
curl -s -o public/static/crm/js/jquery-3.5.1.slim.min.js "$BASE_URL/crm/js/jquery-3.5.1.slim.min.js"
curl -s -o public/static/crm/js/popper.min.js "$BASE_URL/crm/js/popper.min.js"

# Download Font Awesome webfonts to both locations
echo "Downloading Font Awesome webfonts..."

# Brand fonts
echo "  Downloading fa-brands-400.eot..."
curl -s -o "static/crm/webfonts/fa-brands-400.eot" "$BASE_URL/crm/webfonts/fa-brands-400.eot"
curl -s -o "public/static/crm/webfonts/fa-brands-400.eot" "$BASE_URL/crm/webfonts/fa-brands-400.eot"

echo "  Downloading fa-brands-400.svg..."
curl -s -o "static/crm/webfonts/fa-brands-400.svg" "$BASE_URL/crm/webfonts/fa-brands-400.svg"
curl -s -o "public/static/crm/webfonts/fa-brands-400.svg" "$BASE_URL/crm/webfonts/fa-brands-400.svg"

echo "  Downloading fa-brands-400.ttf..."
curl -s -o "static/crm/webfonts/fa-brands-400.ttf" "$BASE_URL/crm/webfonts/fa-brands-400.ttf"
curl -s -o "public/static/crm/webfonts/fa-brands-400.ttf" "$BASE_URL/crm/webfonts/fa-brands-400.ttf"

echo "  Downloading fa-brands-400.woff..."
curl -s -o "static/crm/webfonts/fa-brands-400.woff" "$BASE_URL/crm/webfonts/fa-brands-400.woff"
curl -s -o "public/static/crm/webfonts/fa-brands-400.woff" "$BASE_URL/crm/webfonts/fa-brands-400.woff"

echo "  Downloading fa-brands-400.woff2..."
curl -s -o "static/crm/webfonts/fa-brands-400.woff2" "$BASE_URL/crm/webfonts/fa-brands-400.woff2"
curl -s -o "public/static/crm/webfonts/fa-brands-400.woff2" "$BASE_URL/crm/webfonts/fa-brands-400.woff2"

# Regular fonts
echo "  Downloading fa-regular-400.eot..."
curl -s -o "static/crm/webfonts/fa-regular-400.eot" "$BASE_URL/crm/webfonts/fa-regular-400.eot"
curl -s -o "public/static/crm/webfonts/fa-regular-400.eot" "$BASE_URL/crm/webfonts/fa-regular-400.eot"

echo "  Downloading fa-regular-400.svg..."
curl -s -o "static/crm/webfonts/fa-regular-400.svg" "$BASE_URL/crm/webfonts/fa-regular-400.svg"
curl -s -o "public/static/crm/webfonts/fa-regular-400.svg" "$BASE_URL/crm/webfonts/fa-regular-400.svg"

echo "  Downloading fa-regular-400.ttf..."
curl -s -o "static/crm/webfonts/fa-regular-400.ttf" "$BASE_URL/crm/webfonts/fa-regular-400.ttf"
curl -s -o "public/static/crm/webfonts/fa-regular-400.ttf" "$BASE_URL/crm/webfonts/fa-regular-400.ttf"

echo "  Downloading fa-regular-400.woff..."
curl -s -o "static/crm/webfonts/fa-regular-400.woff" "$BASE_URL/crm/webfonts/fa-regular-400.woff"
curl -s -o "public/static/crm/webfonts/fa-regular-400.woff" "$BASE_URL/crm/webfonts/fa-regular-400.woff"

echo "  Downloading fa-regular-400.woff2..."
curl -s -o "static/crm/webfonts/fa-regular-400.woff2" "$BASE_URL/crm/webfonts/fa-regular-400.woff2"
curl -s -o "public/static/crm/webfonts/fa-regular-400.woff2" "$BASE_URL/crm/webfonts/fa-regular-400.woff2"

# Solid fonts
echo "  Downloading fa-solid-900.eot..."
curl -s -o "static/crm/webfonts/fa-solid-900.eot" "$BASE_URL/crm/webfonts/fa-solid-900.eot"
curl -s -o "public/static/crm/webfonts/fa-solid-900.eot" "$BASE_URL/crm/webfonts/fa-solid-900.eot"

echo "  Downloading fa-solid-900.svg..."
curl -s -o "static/crm/webfonts/fa-solid-900.svg" "$BASE_URL/crm/webfonts/fa-solid-900.svg"
curl -s -o "public/static/crm/webfonts/fa-solid-900.svg" "$BASE_URL/crm/webfonts/fa-solid-900.svg"

echo "  Downloading fa-solid-900.ttf..."
curl -s -o "static/crm/webfonts/fa-solid-900.ttf" "$BASE_URL/crm/webfonts/fa-solid-900.ttf"
curl -s -o "public/static/crm/webfonts/fa-solid-900.ttf" "$BASE_URL/crm/webfonts/fa-solid-900.ttf"

echo "  Downloading fa-solid-900.woff..."
curl -s -o "static/crm/webfonts/fa-solid-900.woff" "$BASE_URL/crm/webfonts/fa-solid-900.woff"
curl -s -o "public/static/crm/webfonts/fa-solid-900.woff" "$BASE_URL/crm/webfonts/fa-solid-900.woff"

echo "  Downloading fa-solid-900.woff2..."
curl -s -o "static/crm/webfonts/fa-solid-900.woff2" "$BASE_URL/crm/webfonts/fa-solid-900.woff2"
curl -s -o "public/static/crm/webfonts/fa-solid-900.woff2" "$BASE_URL/crm/webfonts/fa-solid-900.woff2"

echo "All static files downloaded successfully!"
echo "Files downloaded to both 'static/' (for development) and 'public/static/' (for production)"
chmod +x download_static_files.sh
